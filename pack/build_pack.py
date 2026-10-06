"""Render the First Pass PDFs. Run:  py -3.10 pack/build_pack.py

Renders pack/content_free.py and pack/content_pack.py to downloads/*.pdf with reportlab.
No network. Deterministic: same input, same bytes (reportlab stamps no timestamp beyond the
document info date, which we set from the data date).
"""
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "downloads")

BG = colors.HexColor("#0B0B0C")
PAPER = colors.HexColor("#F5F3EE")
INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#6B6862")
RULE = colors.HexColor("#D8D4CA")
ACCENT = colors.HexColor("#C97A00")
ACCENT_L = colors.HexColor("#E8B44A")
RED = colors.HexColor("#B23A2B")

DATA_DATE = "5 October 2026"
PAGE_URL = "https://maxhemmerich.github.io/first-pass-ca/"

SS = getSampleStyleSheet()


def styles():
    return {
        "h1": ParagraphStyle("h1", parent=SS["Heading1"], fontName="Helvetica-Bold",
                             fontSize=22, leading=25, textColor=INK, spaceAfter=10, spaceBefore=2),
        "h2": ParagraphStyle("h2", parent=SS["Heading2"], fontName="Helvetica-Bold",
                             fontSize=13.5, leading=17, textColor=INK, spaceAfter=6, spaceBefore=14),
        "h3": ParagraphStyle("h3", parent=SS["Heading3"], fontName="Helvetica-BoldOblique",
                             fontSize=10.5, leading=14, textColor=ACCENT, spaceAfter=4, spaceBefore=10),
        "p": ParagraphStyle("p", parent=SS["BodyText"], fontName="Helvetica", fontSize=9.6,
                            leading=13.6, textColor=INK, spaceAfter=7, alignment=TA_LEFT),
        "small": ParagraphStyle("small", parent=SS["BodyText"], fontName="Helvetica", fontSize=8.2,
                                leading=11.4, textColor=MUTED, spaceAfter=6),
        "bul": ParagraphStyle("bul", parent=SS["BodyText"], fontName="Helvetica", fontSize=9.6,
                              leading=13.4, textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=3.5),
        "num": ParagraphStyle("num", parent=SS["BodyText"], fontName="Helvetica", fontSize=9.6,
                              leading=13.4, textColor=INK, leftIndent=20, bulletIndent=2, spaceAfter=3.5),
        "callout": ParagraphStyle("callout", parent=SS["BodyText"], fontName="Helvetica", fontSize=9.4,
                                  leading=13.2, textColor=INK, leftIndent=8, rightIndent=8,
                                  spaceAfter=0, spaceBefore=0),
        "quote": ParagraphStyle("quote", parent=SS["BodyText"], fontName="Helvetica-Oblique",
                                fontSize=9.2, leading=12.6, textColor=INK, leftIndent=10, spaceAfter=3),
        "mono": ParagraphStyle("mono", parent=SS["BodyText"], fontName="Courier", fontSize=8.6,
                               leading=12, textColor=INK, spaceAfter=3),
    }


def callout_flowable(text, st, border=ACCENT):
    inner = Paragraph(text, st["callout"])
    t = Table([[inner]], colWidths=[468])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFEBE0")),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def bar_table(rows, st, total_label="of 43"):
    """rows: (label, count, total, note) -> label | count | proportional bar"""
    maxn = max(r[2] for r in rows)
    data = []
    for label, n, total, note in rows:
        pct = n / float(maxn)
        bar_w = max(3, int(150 * pct))
        bar = Table([[""]], colWidths=[bar_w], rowHeights=[7])
        bar.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                 ("TOPPADDING", (0, 0), (-1, -1), 0),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        lab = Paragraph(label + ("<br/><font size=7.6 color='#6B6862'>%s</font>" % note if note else ""), st["p"])
        data.append([lab, Paragraph('<font face="Courier">%d</font>' % n, st["p"]), bar])
    t = Table(data, colWidths=[268, 30, 170])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def grid(head, rows, st, widths):
    data = [[Paragraph("<font face='Helvetica-Bold' size=8.4>%s</font>" % h, st["p"]) for h in head]]
    for r in rows:
        data.append([Paragraph(str(c), st["p"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, INK),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build(doc_spec, path):
    st = styles()
    title = doc_spec["title"]
    subtitle = doc_spec["subtitle"]

    def cover(canv, doc):
        canv.saveState()
        w, h = LETTER
        canv.setFillColor(BG)
        canv.rect(0, 0, w, h, stroke=0, fill=1)
        canv.setFillColor(ACCENT)
        canv.rect(54, h - 96, 46, 3, stroke=0, fill=1)
        canv.setFillColor(PAPER)
        canv.setFont("Helvetica-Bold", 40)
        canv.drawString(54, h - 150, "FIRST PASS")
        canv.setFont("Courier", 11)
        canv.setFillColor(ACCENT_L)
        canv.drawString(54, h - 176, "CANADA / TECHNICAL ROLES")
        canv.setFillColor(PAPER)
        canv.setFont("Helvetica-Bold", 19)
        canv.drawString(54, h - 250, title)
        canv.setFont("Helvetica", 11)
        canv.setFillColor(colors.HexColor("#B9B4A8"))
        y = h - 276
        for line in subtitle.split("|"):
            canv.drawString(54, y, line.strip())
            y -= 15
        canv.setStrokeColor(colors.HexColor("#2A2A2F"))
        canv.setLineWidth(0.6)
        canv.line(54, 150, w - 54, 150)
        canv.setFont("Courier", 8.5)
        canv.setFillColor(colors.HexColor("#8C887C"))
        canv.drawString(54, 133, "Data collected %s. Every count in this document is measured from" % DATA_DATE)
        canv.drawString(54, 121, "the 141 postings named in the method note. Nothing here is estimated.")
        canv.drawString(54, 100, doc_spec.get("cover_footer", ""))
        canv.drawString(54, 88, PAGE_URL)
        canv.restoreState()

    def later(canv, doc):
        canv.saveState()
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(54, 52, LETTER[0] - 54, 52)
        canv.setFont("Helvetica", 7.6)
        canv.setFillColor(MUTED)
        canv.drawString(54, 40, "First Pass / %s / dataset of %s" % (title, DATA_DATE))
        canv.drawRightString(LETTER[0] - 54, 40, "%d" % doc.page)
        canv.restoreState()

    doc = BaseDocTemplate(path, pagesize=LETTER,
                          leftMargin=54, rightMargin=54, topMargin=58, bottomMargin=64,
                          title="First Pass - %s" % title, author="First Pass",
                          subject=doc_spec.get("subject", ""), creator="First Pass")
    frame = Frame(54, 64, LETTER[0] - 108, LETTER[1] - 58 - 64 - 34, id="body")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPage=cover),
                          PageTemplate(id="body", frames=[frame], onPage=later)])
    # first page uses the cover template, everything after uses body
    story = [PageBreak()]
    doc.handle_nextPageTemplate("body")

    for block in doc_spec["blocks"]:
        kind = block[0]
        if kind == "h1":
            story.append(Paragraph(block[1], st["h1"]))
        elif kind == "h2":
            story.append(Paragraph(block[1], st["h2"]))
        elif kind == "h3":
            story.append(Paragraph(block[1], st["h3"]))
        elif kind == "p":
            story.append(Paragraph(block[1], st["p"]))
        elif kind == "small":
            story.append(Paragraph(block[1], st["small"]))
        elif kind == "mono":
            story.append(Paragraph(block[1], st["mono"]))
        elif kind == "bul":
            for b in block[1]:
                story.append(Paragraph(b, st["bul"], bulletText="\u2022"))
            story.append(Spacer(1, 5))
        elif kind == "num":
            for i, b in enumerate(block[1], 1):
                story.append(Paragraph(b, st["num"], bulletText="%d." % i))
            story.append(Spacer(1, 5))
        elif kind == "quote":
            story.append(Paragraph("\u201c%s\u201d" % block[1], st["quote"]))
        elif kind == "callout":
            story.append(Spacer(1, 4))
            story.append(callout_flowable(block[1], st, ACCENT))
            story.append(Spacer(1, 9))
        elif kind == "warn":
            story.append(Spacer(1, 4))
            story.append(callout_flowable(block[1], st, RED))
            story.append(Spacer(1, 9))
        elif kind == "bars":
            story.append(Spacer(1, 2))
            story.append(bar_table(block[1], st))
            story.append(Spacer(1, 8))
        elif kind == "grid":
            head, rows, widths = block[1], block[2], block[3]
            story.append(Spacer(1, 2))
            story.append(grid(head, rows, st, widths))
            story.append(Spacer(1, 8))
        elif kind == "keep":
            story.append(KeepTogether([Paragraph(block[1], st["h3"]),
                                       *(Paragraph(x, st["p"]) for x in block[2])]))
        elif kind == "pb":
            story.append(PageBreak())
        elif kind == "space":
            story.append(Spacer(1, block[1]))
        else:
            raise ValueError("unknown block %r" % (kind,))

    doc.build(story)
    return path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    sys.path.insert(0, HERE)
    import content_free
    import content_pack

    made = []
    for spec, fname in ((content_free.DOC, "first-pass-free-screen-report.pdf"),
                        (content_pack.DOC, "first-pass-canada-tech-pack.pdf")):
        p = build(spec, os.path.join(OUT_DIR, fname))
        made.append(p)

    from pypdf import PdfReader
    for p in made:
        r = PdfReader(p)
        chars = [len((pg.extract_text() or "").strip()) for pg in r.pages]
        print("%-50s pages=%d bytes=%d minchars=%d maxchars=%d"
              % (os.path.basename(p), len(r.pages), os.path.getsize(p), min(chars), max(chars)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
