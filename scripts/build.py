# -*- coding: utf-8 -*-
"""从 chapters/ 构建合并 Markdown 与 PDF。

依赖：
- pandoc（Markdown -> HTML，需 3.x）
- Microsoft Edge（headless --print-to-pdf 生成 PDF，支持 SVG 与中文字体）

用法：python scripts/build.py
"""
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
TITLE = "物理AI：从自动驾驶到具身智能"
VERSION = "v2.1"
COMBINED = ROOT / f"{TITLE}-{VERSION}.md"
PDF = ROOT / f"{TITLE}-{VERSION}.pdf"
HTML = ROOT / "_book.html"
EDGE = pathlib.Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def build_combined():
    chapters = sorted((ROOT / "chapters").glob("*.md"))
    toc_lines, body_parts = [], []
    for ch in chapters:
        text = ch.read_text(encoding="utf-8")
        title = re.search(r"(?m)^# (.+)$", text).group(1).strip()
        toc_lines.append(f"- {title}")
        demoted = re.sub(r"(?m)^(#{1,5}) ", r"#\1 ", text)
        demoted = demoted.replace("](../figures/", "](figures/")
        body_parts.append(demoted.strip())
    header = (
        f"# {TITLE}\n\n**版本：{VERSION}**\n\n## 目录\n\n"
        + "\n".join(toc_lines)
        + "\n"
    )
    COMBINED.write_text(header + "\n" + "\n\n".join(body_parts) + "\n", encoding="utf-8")
    print(f"combined -> {COMBINED.name} ({COMBINED.stat().st_size} bytes)")


def build_pdf():
    subprocess.run(
        [
            "pandoc", str(COMBINED),
            "-o", str(HTML),
            "--standalone", "--mathml",
            "--css", "scripts/style.css",
            "--metadata", f"title={TITLE}",
            "--metadata", "lang=zh-CN",
        ],
        check=True, cwd=ROOT,
    )
    subprocess.run(
        [
            str(EDGE), "--headless", "--disable-gpu", "--no-pdf-header-footer",
            # 独立的临时 profile：避免与用户正在运行的 Edge 实例冲突导致静默失败
            f"--user-data-dir={pathlib.Path.home() / 'AppData/Local/Temp/edgepdf'}",
            f"--print-to-pdf={PDF}", HTML.resolve().as_uri(),
        ],
        check=True, timeout=300,
    )
    HTML.unlink(missing_ok=True)
    print(f"pdf -> {PDF.name} ({PDF.stat().st_size} bytes)")


if __name__ == "__main__":
    build_combined()
    build_pdf()
