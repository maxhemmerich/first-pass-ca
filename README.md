# First Pass

A paid pack for Canadian technical job seekers being screened by automated systems: the screening
questions employers actually ask, the ATS keyword map, and the salary scripts for the Canadian market.

- Live page: https://maxhemmerich.github.io/first-pass-ca/
- Free report: `downloads/first-pass-free-screen-report.pdf` (8 pages)
- Paid pack: `downloads/first-pass-canada-tech-pack.pdf` (21 pages, $24 CAD)
- Generator: `py -3.10 pack/build_pack.py` (reportlab; rebuilds both PDFs byte-identically)

## Where the numbers come from

141 Canadian technical job postings collected on 5 October 2026. 140 were readable in full; 43
published the employer's own screening questions; 39 published the answer set; 53 were scored against
a written fit rubric. Every count in the page and in both PDFs is a keyword match against those
posting texts. Nothing is estimated, no external study is cited, and none of the postings' applicants'
answers are used.

The sample is Ontario-heavy (Toronto, Mississauga, Markham, Oakville, Burlington) and skews to
analytics, business intelligence, clinical data and operations analysis. It is one applicant's
pipeline, counted — not a random sample of the Canadian market.

## What is not in this repo

The harvester, the raw posting texts and the internal specs are gitignored (they contain a private
application pipeline). The pack's content files and the PDF renderer are here, so every number in the
documents can be traced back to the method note printed inside them.

## Honest state

Checkout is not connected. The page's buy buttons say so and are disabled; `CHECKOUT_URL` at the top
of the script in `index.html` is the single slot that activates them. No revenue has been recorded.
