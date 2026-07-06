"""
html_to_pdf.py
Converts newsletter_output.html into a polished PDF attachment.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

INPUT_FILE = Path("newsletter_output.html")
OUTPUT_FILE = Path("newsletter_output.pdf")


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"{INPUT_FILE} not found. Generate the newsletter first.")

    html_path = INPUT_FILE.resolve()
    pdf_path = OUTPUT_FILE.resolve()

    print(f"[pdf] Rendering {html_path.name} to {pdf_path.name}...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 1400})
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.emulate_media(media="print")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={
                "top": "14mm",
                "right": "12mm",
                "bottom": "16mm",
                "left": "12mm",
            },
        )
        browser.close()

    size_kb = pdf_path.stat().st_size / 1024
    print(f"[pdf] Saved {pdf_path.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
