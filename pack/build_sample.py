"""Render the free one-page sample of the paid pack:  py -3.10 pack/build_sample.py

Cuts ONE page out of the paid pack and stamps it as a sample. It does not rebuild the pack, so
downloads/first-pass-canada-tech-pack.pdf is byte-untouched by this script.

The page given away is page 7 of 21 — the first page of section 03, "Work authorization and
sponsorship". See NEXT.md item 9 for why that page and not another: it shows the pack's structure
(the numbered section header, the verbatim-wording block, the answer bullets, the limits callout
and the "what never helps" list) without carrying a counted table, a ranked list, or any of the
pack's three headline deliverables (the keyword map, the screening-question bank, the negotiation
scripts).

Run: py -3.10 pack/build_sample.py
"""
import hashlib
import os
import sys

from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOWNLOADS = os.path.join(ROOT, "downloads")
PACK = os.path.join(DOWNLOADS, "first-pass-canada-tech-pack.pdf")
OUT = os.path.join(DOWNLOADS, "first-pass-pack-sample.pdf")

SAMPLE_PAGE = 7          # 1-based page of the pack that ships free
PACK_PAGES = 21
PAGE_URL = "https://maxhemmerich.github.io/first-pass-ca/"


def stamp(path, out):
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas as rl_canvas

    reader = PdfReader(PACK)
    if len(reader.pages) != PACK_PAGES:
        raise SystemExit("pack page count changed: %d" % len(reader.pages))

    accent = HexColor("#C97A00")
    ink = HexColor("#111111")
    muted = HexColor("#6B6862")

    gate = os.path.join(HERE, "_sample_overlay.pdf")
    c = rl_canvas.Canvas(gate, pagesize=LETTER)
    w, h = LETTER
    c.saveState()
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(54, h - 40, "SAMPLE \u2014 ONE PAGE OF THE 21-PAGE PACK")
    c.setFillColor(ink)
    c.setFont("Helvetica", 8.4)
    c.drawString(54, h - 55, "Page %d of 21, the first page of section 03, given away free. The complete pack is CA$24 CAD." % SAMPLE_PAGE)
    c.setStrokeColor(accent)
    c.setLineWidth(1.2)
    c.line(54, h - 64, w - 54, h - 64)
    c.setFillColor(muted)
    c.setFont("Helvetica-Oblique", 7.6)
    c.drawString(54, 26, "Free sample. Full pack: %s  \u00b7  questions or refunds: maxhemmerich@gmail.com" % PAGE_URL)
    c.restoreState()
    c.showPage()
    c.save()

    overlay = PdfReader(gate).pages[0]
    writer = PdfWriter()
    page = reader.pages[SAMPLE_PAGE - 1]
    page.merge_page(overlay)
    writer.add_page(page)
    writer.add_metadata({
        "/Title": "First Pass pack \u2014 free one-page sample",
        "/Author": "First Pass",
        "/Subject": "Sample: page %d of the 21-page First Pass pack" % SAMPLE_PAGE,
        "/Creator": "First Pass",
    })
    with open(out, "wb") as fh:
        writer.write(fh)
    os.remove(gate)
    return out


def main():
    if not os.path.exists(PACK):
        raise SystemExit("pack not found: %s" % PACK)
    stamp(PACK, OUT)

    b = open(OUT, "rb").read()
    r = PdfReader(OUT)
    text = (r.pages[0].extract_text() or "")
    checks = {
        "1 page": len(r.pages) == 1,
        "sample banner present": "SAMPLE \u2014 ONE PAGE OF THE 21-PAGE PACK".encode() and "SAMPLE" in text,
        "sample footer present": "Free sample." in text,
        "section 03 heading present": "Work authorization and sponsorship" in text,
        "pack page 7 body present": "what never helps" in text.lower(),
    }
    print("%s  pages=%d  bytes=%d  sha256=%s"
          % (os.path.basename(OUT), len(r.pages), len(b), hashlib.sha256(b).hexdigest()))
    for k, v in checks.items():
        print("  %-28s %s" % (k, "OK" if v else "FAIL"))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
