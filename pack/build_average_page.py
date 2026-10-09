"""Build /tech-average-pay/ — a third citable Canadian technical pay reference, from the SAME single
source the other two use: Employment and Social Development Canada's open-data "Wages" file
(Open Government Licence - Canada).

Why this cut. The two sibling pages print the file's *median* — /tech-salaries/ nationally (its low,
25th, median, 75th and high rows) and province by province, and /tech-salaries-by-city/ by economic
region. None of them prints the file's **average** wage, which the file publishes for the same
occupations. This page prints that average and nothing else: nationally, and for the ten provinces.
No figure on this page is printed on either sibling.

Hard rules, the same as the siblings: every number on the page is a string copied out of the named
CSV — nothing computed, converted or averaged here; the file reports by the hour and this page keeps
it hourly; a cell the file leaves empty renders as a dash; no content or figure from the paid pack.

Run:
  py -3.10 pack/build_average_page.py <path-to-wages-csv>
"""
import csv, os, sys, hashlib, collections, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE = {
    "dataset_title": "Wages",
    "publisher": "Employment and Social Development Canada",
    "dataset_url": "https://open.canada.ca/data/en/dataset/adad580f-76b0-4502-bd05-20c125de9116",
    "resource_name": "2025 Wages",
    "resource_url": "https://open.canada.ca/data/dataset/adad580f-76b0-4502-bd05-20c125de9116/resource/9da94d63-b178-4a64-aeb3-b6a3bd721ad2/download/2a71-das-wage2025opendata-esdc-all-19nov2025-vf.csv",
    "resource_file": "2a71-das-wage2025opendata-esdc-all-19nov2025-vf.csv",
    "resource_published": "2025-11-19",
    "licence": "Open Government Licence \u2013 Canada",
    "licence_url": "https://open.canada.ca/en/open-government-licence-canada",
    "read_date": "2026-10-09",
}

# The file's own column this page is built on. Named here so the verifier and the page agree.
COLUMN = "Average_Wage_Salaire_Moyen"

# The same sixteen NOC 2021 technical unit groups as the two sibling pages: (code, full title).
OCC = [
    ("21232", "Software developers and programmers"),
    ("21231", "Software engineers and designers"),
    ("21230", "Computer systems developers and programmers"),
    ("21211", "Data scientists"),
    ("21223", "Database analysts and data administrators"),
    ("21222", "Information systems specialists"),
    ("21221", "Business systems specialists"),
    ("21220", "Cybersecurity specialists"),
    ("21311", "Computer engineers (except software engineers and designers)"),
    ("21234", "Web developers and programmers"),
    ("21233", "Web designers"),
    ("21210", "Mathematicians, statisticians and actuaries"),
    ("22220", "Computer network and web technicians"),
    ("22222", "Information systems testing technicians"),
    ("22221", "User support technicians"),
    ("20012", "Computer and information systems managers"),
]

PROV = [
    ("BC", "British Columbia"), ("AB", "Alberta"), ("SK", "Saskatchewan"), ("MB", "Manitoba"),
    ("ON", "Ontario"), ("QC", "Quebec"), ("NB", "New Brunswick"), ("NS", "Nova Scotia"),
    ("PEI", "Prince Edward Island"), ("NL", "Newfoundland and Labrador"),
]

SRC_MARK = {
    "Labour Force Survey": "",
    "Small Area Estimation": "&dagger;",
    "Employment Insurance Survey Data": "&ddagger;",
    "2021 Census": "&sect;",
}


def load(path):
    csv.field_size_limit(10 ** 7)
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def code_of(r):
    return r["NOC_CNP"].replace("NOC_", "")


def collect(rows):
    national, provincial = {}, {}
    marks = collections.Counter()
    for r in rows:
        c = code_of(r)
        if c not in {o[0] for o in OCC}:
            continue
        if r["prov"] == "NAT":
            national[c] = r
        for (pc, full) in PROV:
            if r["prov"] == pc and r["ER_Name"].strip() == full:
                provincial[(c, pc)] = r
    for (c, pc), r in provincial.items():
        if r[COLUMN].strip():
            marks[SRC_MARK.get(r["Data_Source_E"].strip(), "?")] += 1
    return national, provincial, marks


def cell(v, mark):
    v = (v or "").strip()
    return "&mdash;" if not v else "$%s%s" % (_html.escape(v), mark)


def build(rows):
    national, provincial, marks = collect(rows)

    nrows, n_blank = [], 0
    for code, title in OCC:
        r = national.get(code)
        if r is None:
            raise SystemExit("no national row for " + code)
        v = r[COLUMN].strip()
        if not v:
            n_blank += 1
        mk = SRC_MARK.get(r["Data_Source_E"].strip(), "?")
        nrows.append(
            '    <tr><td class="noc">%s</td><td class="occ">%s</td><td class="n">%s</td></tr>'
            % (code, _html.escape(title), cell(v, mk))
        )

    phead = "".join('<th class="n">%s</th>' % ab for _p, ab in PROV)
    prows, n_dashes = [], 0
    for code, title in OCC:
        cells = []
        for (pc, _full) in PROV:
            r = provincial.get((code, pc))
            if r is None or not r[COLUMN].strip():
                cells.append('<td class="n dim">&mdash;</td>')
                n_dashes += 1
                continue
            mk = SRC_MARK.get(r["Data_Source_E"].strip(), "?")
            cells.append('<td class="n">%s</td>' % cell(r[COLUMN], mk))
        prows.append(
            '    <tr><td class="noc">%s</td><td class="occ">%s</td>%s</tr>'
            % (code, _html.escape(title), "".join(cells))
        )

    src_line = ("%s, <em>%s</em>, %s \u2014 %s. Read %s. SHA-256 "
                "<span class=\"mono\">%s</span>." % (
                    SOURCE["publisher"], SOURCE["dataset_title"], SOURCE["resource_name"],
                    SOURCE["licence"], SOURCE["read_date"], HASH))

    html = PAGE.format(
        TITLE=TITLE, DESC=DESC, NROWS="\n".join(nrows), PROWS="\n".join(prows),
        PHEAD=phead, SOURCE_LINE=src_line, N=len(OCC),
        DATASET_URL=SOURCE["dataset_url"], RES_URL=SOURCE["resource_url"],
        LIC_URL=SOURCE["licence_url"], RES_FILE=SOURCE["resource_file"],
        RES_PUB=SOURCE["resource_published"], HASH=HASH,
    )
    return html, marks, n_blank, n_dashes


TITLE = "Average Canadian tech salary \u2014 the wage file's average pay by occupation"
DESC = ("Average hourly pay for 16 Canadian software, data, IT and computer-engineering occupations, "
        "nationally and by province, taken from Employment and Social Development Canada's published "
        "wage file (Open Government Licence \u2013 Canada). Every figure carries its source and the "
        "date it was read.")

PAGE = """<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://maxhemmerich.github.io/first-pass-ca/tech-average-pay/">
<meta property="og:type" content="article">
<meta property="og:site_name" content="First Pass">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="https://maxhemmerich.github.io/first-pass-ca/tech-average-pay/">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="16 Canadian technical occupations, average pay per hour, nationally and by province, from the government's own wage file.">
<style>
  :root{{
    --bg:#0B0B0C; --panel:#131316; --panel2:#0F0F12;
    --ink:#F2F0EA; --muted:#9A968C; --rule:#2A2A2F; --rule2:#1C1C20;
    --accent:#FFB020; --red:#FF4D3D; --green:#35D07F;
    --serif:Georgia,'Times New Roman',serif;
    --sans:'Segoe UI',-apple-system,Helvetica,Arial,sans-serif;
    --mono:Consolas,'SF Mono',ui-monospace,monospace;
  }}
  *{{box-sizing:border-box}}
  html,body{{margin:0;padding:0}}
  body{{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.55;
    -webkit-font-smoothing:antialiased;overflow-x:hidden}}
  .wrap{{max-width:1080px;margin:0 auto;padding:0 20px}}
  a{{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule)}}
  a:hover{{border-bottom-color:var(--accent)}}
  h1,h2,h3{{font-family:var(--serif);font-weight:400;margin:0;text-wrap:pretty}}
  h1{{font-size:clamp(34px,7.4vw,62px);line-height:1.03;letter-spacing:-.02em}}
  h2{{font-size:clamp(24px,4.2vw,36px);line-height:1.12;letter-spacing:-.01em}}
  h3{{font-size:19px;line-height:1.25}}
  p{{margin:0 0 14px}}
  .mono{{font-family:var(--mono);font-variant-numeric:tabular-nums}}
  .kicker{{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}}

  .bar{{position:sticky;top:0;z-index:20;background:rgba(11,11,12,.94);border-bottom:1px solid var(--rule)}}
  .bar-in{{display:flex;align-items:center;gap:14px;justify-content:space-between;height:58px}}
  .mark{{font-family:var(--mono);font-size:13px;letter-spacing:.2em}}
  .mark b{{color:var(--accent);font-weight:400}}
  .bar-meta{{display:flex;align-items:center;gap:14px}}
  .bar-meta .price{{font-family:var(--mono);font-size:13px;color:var(--muted)}}
  @media (max-width:520px){{.bar-meta .price{{display:none}}}}

  .btn{{display:inline-flex;align-items:center;justify-content:center;gap:8px;
    min-height:48px;padding:0 20px;border:1px solid var(--accent);background:var(--accent);
    color:#141414;font-family:var(--mono);font-size:13px;letter-spacing:.06em;text-transform:uppercase;
    cursor:pointer;border-radius:0;transition:transform .12s ease}}
  .btn:hover{{transform:translateY(-1px)}}
  .btn:focus-visible{{outline:2px solid var(--ink);outline-offset:2px}}
  .btn.ghost{{background:transparent;color:var(--ink);border-color:var(--rule)}}
  .btn.ghost:hover{{border-color:var(--ink)}}
  .btn.sm{{min-height:40px;padding:0 14px;font-size:12px}}

  section{{border-top:1px solid var(--rule);padding:56px 0}}
  .sec-head{{display:grid;grid-template-columns:64px 1fr;gap:20px;align-items:baseline;margin-bottom:26px}}
  .sec-num{{font-family:var(--mono);font-size:12px;color:var(--accent);letter-spacing:.1em;padding-top:8px}}
  @media (max-width:640px){{.sec-head{{grid-template-columns:1fr;gap:6px}}.sec-num{{padding-top:0}}}}

  .hero{{border-top:0;padding-top:44px}}
  .hero h1 span{{color:var(--accent)}}
  .lede{{color:#CFCBC1;font-size:17px;max-width:62ch;margin-top:18px}}
  .facts{{display:flex;flex-wrap:wrap;gap:0 22px;margin-top:26px;font-family:var(--mono);font-size:12px;color:var(--muted)}}
  .facts span{{border-right:1px solid var(--rule);padding-right:22px}}
  .facts span:last-child{{border-right:0}}

  .scroll{{overflow-x:auto;border-top:1px solid var(--rule)}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  th,td{{padding:10px 12px;border-bottom:1px solid var(--rule2);text-align:left;white-space:nowrap}}
  thead th{{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;
    color:var(--muted);border-bottom:1px solid var(--rule);font-weight:600}}
  td.n,th.n{{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right}}
  td.avg{{color:var(--accent)}}
  td.dim{{color:#4A4A50}}
  td.noc{{font-family:var(--mono);font-size:12.5px;color:var(--muted)}}
  td.occ{{white-space:normal;min-width:220px;color:#CFCBC1}}
  .tcap{{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin:14px 0 0;max-width:80ch;white-space:normal}}

  .limits{{list-style:none;margin:0;padding:0}}
  .limits li{{padding:10px 0;border-bottom:1px solid var(--rule2);color:#CFCBC1;font-size:14.5px}}
  .limits li b{{color:var(--ink);font-weight:400}}

  .pull{{margin-top:24px;border:1px solid var(--rule);border-left:2px solid var(--accent);background:var(--panel2);padding:16px}}
  .pull p{{margin:0;font-size:14.5px;color:#CFCBC1}}
  .pull .mono{{color:var(--ink)}}

  .two{{display:grid;grid-template-columns:1fr 1.35fr;gap:34px;align-items:start}}
  @media (max-width:820px){{.two{{grid-template-columns:1fr;gap:24px}}}}
  .free{{border:1px solid var(--rule);padding:18px;background:var(--panel2)}}
  .paid{{border:1px solid var(--rule);padding:0;background:var(--panel)}}
  .paid-head{{padding:16px 18px;border-bottom:1px solid var(--rule);display:flex;justify-content:space-between;align-items:baseline;gap:10px}}
  .paid-head .p{{font-family:var(--mono);color:var(--accent);font-size:15px}}
  .paid-foot{{display:flex;align-items:center;gap:14px;padding:14px 18px;border-top:1px solid var(--rule)}}

  footer{{border-top:1px solid var(--rule);padding:30px 0 60px;color:var(--muted);font-size:13px}}
  footer .mono{{font-size:12px}}
  .fnote{{margin-top:14px;max-width:70ch}}
</style>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-average-pay/#article",
  "url": "https://maxhemmerich.github.io/first-pass-ca/tech-average-pay/",
  "headline": "{TITLE}",
  "description": "{DESC}",
  "inLanguage": "en-CA",
  "datePublished": "2026-10-09",
  "dateModified": "2026-10-09",
  "author": {{"@type": "Organization", "name": "First Pass"}},
  "publisher": {{"@type": "Organization", "name": "First Pass", "url": "https://maxhemmerich.github.io/first-pass-ca/"}},
  "isPartOf": {{"@type": "WebSite", "@id": "https://maxhemmerich.github.io/first-pass-ca/#website", "url": "https://maxhemmerich.github.io/first-pass-ca/", "name": "First Pass"}},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-average-pay/"}},
  "isBasedOn": {{"@type": "Dataset", "name": "Wages", "creator": {{"@type": "GovernmentOrganization", "name": "Employment and Social Development Canada"}}, "license": "{LIC_URL}", "url": "{DATASET_URL}"}}
}}
</script>
</head>
<body>

<div class="bar"><div class="wrap bar-in">
  <a class="mark" href="../" style="border-bottom:0">FIRST<b>&middot;</b>PASS</a>
  <div class="bar-meta">
    <span class="price">THE PACK &middot; 21 PAGES &middot; CA$24</span>
    <a class="btn sm" data-buy href="https://maxhemmerich.gumroad.com/l/yolqdo" target="_blank" rel="noopener">Get the pack</a>
  </div>
</div></div>

<!-- hero -->
<section class="hero"><div class="wrap">
  <div class="kicker">Canada &middot; official wage data &middot; the average column</div>
  <h1>The average Canadian tech wage, <span>by occupation</span></h1>
  <p class="lede">Employment and Social Development Canada's wage file carries two measures of the
    middle for every occupation: a median and an average. The sibling pages on this site print the
    median. This page prints the other one &mdash; the file's own <b>average</b> hourly wage for
    <b>{N}</b> software, data, IT and computer-engineering occupations, nationally and for each of the
    ten provinces. Every figure is the file's own string, with the survey behind it and the date it
    was read.</p>
  <div class="facts mono">
    <span>{N} occupations</span><span>national + 10 provinces</span><span>ESDC open data</span><span>read 9 October 2026</span>
  </div>
</div></section>

<!-- 01 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">01</div><div>
    <h2>The average, occupation by occupation</h2>
    <p class="lede" style="margin-top:12px">Canadian dollars per hour, exactly as the file publishes
      them. This is the file's average wage: the total paid across everyone in the occupation divided
      by the number of workers, as the file reports it. It is not a number this page calculated.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th><th class="n">Average</th></tr></thead>
    <tbody id="avg-nat">
{NROWS}
    </tbody>
  </table>
  </div>
  <p class="tcap">Source: {SOURCE_LINE} These are wages <em>paid</em>, not wages offered. NOC 2021 codes.</p>
</div></section>

<!-- 02 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">02</div><div>
    <h2>The same average, province by province</h2>
    <p class="lede" style="margin-top:12px">The file's average hourly wage for each occupation in each
      province. Where the file leaves a cell empty &mdash; it publishes no average for that occupation
      there &mdash; the cell is a dash and nothing is filled in.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th>{PHEAD}</tr></thead>
    <tbody id="avg-prov">
{PROWS}
    </tbody>
  </table>
  </div>
  <p class="tcap">Plain cells carry the Labour Force Survey's 2023&ndash;2024 window; the two cells marked
    &ddagger; come from the Employment Insurance survey instead. Yukon, Nunavut and the Northwest
    Territories are absent because the source carries nothing for these occupations there. A dash is the
    file's own silence &mdash; not a zero, and not a figure carried over from a neighbour.</p>
</div></section>

<!-- 03 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">03</div><div>
    <h2>Reading this page honestly</h2>
  </div></div>
  <ul class="limits">
    <li><b>One file, one column.</b> The whole page rests on a single document: Employment and Social
      Development Canada's open-data <em>Wages</em> release for 2025, published 19 November 2025 under the
      <a href="{LIC_URL}">Open Government Licence &ndash; Canada</a>. The file read here is
      <span class="mono">{RES_FILE}</span>; it hashes to <span class="mono">{HASH}</span>, and
      <a href="{DATASET_URL}">the dataset page</a> plus <a href="{RES_URL}">the download</a> are where
      that can be checked.</li>
    <li><b>Average, not median.</b> The two are different statistics and can sit apart: for each of these
      sixteen occupations the file's average is higher than its median, because the highest-paid workers
      pull a mean up in a way they do not move a middle value. The median, and the file's low, quartile
      and high rows, are on <a href="../tech-salaries/">the salary page</a> &mdash; not reprinted here.</li>
    <li><b>Paid, not advertised.</b> The file's own note is that these are wages <em>paid</em>, so an
      average here is what workers in an occupation were actually paid, not the figure in a job ad. Each
      number is the file's, moved into this table without alteration.</li>
    <li><b>The file counts by the hour and so does this page.</b> These occupations are published as an
      hourly rate and are kept that way. A yearly salary would need a paid-hours figure the file does not
      publish, so turning an hourly number into an annual one would mean inventing the multiplier.</li>
    <li><b>Where the file is silent, so is this table.</b> Some occupation-and-province cells carry no
      average at all in the source. Those cells render as a dash; none is estimated, borrowed from a
      neighbouring province or filled from the national figure.</li>
    <li><b>A reference, not an offer.</b> This table describes an occupation across a geography. A given
      employer, seniority level or office can sit above or below it, and it is not a posting, a recruiter,
      or guidance of any kind. Nothing on it is drawn from the paid pack.</li>
  </ul>
  <div class="pull">
    <p>The file publishes the same sixteen occupations at three levels of geography &mdash; national,
      provincial and economic-region &mdash; and in several measures. This page takes the average; its
      siblings take the median. The CSV is free to reuse with attribution under the
      <span class="mono">OGL&ndash;Canada</span>, and the link above is the whole source.</p>
  </div>
</div></section>

<!-- 04 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">04</div><div>
    <h2>Where this sits</h2>
    <p class="lede" style="margin-top:12px">Read this page for the file's <em>average</em>. For the
      median and the spread around it, nationally and by province, the salary page is the companion;
      for the same roles cut by city, the salary-by-city page; for what employers actually asked and how
      to answer, the free report and the pack are the other half.</p>
  </div></div>
  <p style="color:#CFCBC1;font-size:14.5px;margin-bottom:22px">The median and the full spread:
    <a href="../tech-salaries/">tech salaries across Canada &rarr;</a> &middot; the same roles by urban
    region: <a href="../tech-salaries-by-city/">tech salaries by city &rarr;</a></p>
  <div class="two">
    <div class="free">
      <div class="kicker">Free to read &middot; no email</div>
      <h3 style="margin-top:10px">The Screen Report</h3>
      <p style="color:#CFCBC1;font-size:14.5px;margin-top:10px">The measured half of the lane: the
        screening questions employers asked, the twenty salary wordings, and the bands the ads printed.</p>
      <a class="btn ghost" href="../free-report/">Read it free &rarr;</a>
    </div>
    <div class="paid">
      <div class="paid-head"><h3>The First Pass pack</h3><span class="p mono">$24 CAD</span></div>
      <p style="padding:14px 18px;margin:0;font-size:14.5px;color:#CFCBC1">The working half &mdash; a
        keyword map by role, an answer shape for each question, three salary scripts and a
        Canada-specific negotiation section, across 21 pages.</p>
      <p style="padding:12px 18px;margin:0;border-top:1px solid var(--rule);font-size:13.5px"><a href="../whats-in-the-pack/">Each of the eight sections, with page numbers &rarr;</a></p>
      <div class="paid-foot">
        <a class="btn sm" data-buy href="https://maxhemmerich.gumroad.com/l/yolqdo" target="_blank" rel="noopener">Get the pack</a>
        <span class="mono" style="color:var(--muted);font-size:11.5px">One PDF &middot; $24 CAD, paid once</span>
      </div>
    </div>
  </div>
</div></section>

<footer><div class="wrap">
  <div class="mono">FIRST PASS &middot; Canada &middot; average pay read 9 October 2026 &middot; <a href="../" style="border-bottom:0">the full page</a> &middot; <a href="../free-report/" style="border-bottom:0">the Screen Report</a></div>
  <div class="fnote">Average pay figures are reproduced from Employment and Social Development Canada's
    <em>Wages</em> open data, which is published under the <a href="{LIC_URL}">Open Government Licence
    &ndash; Canada</a>; this page carries that information with attribution and is neither endorsed by nor
    affiliated with ESDC. Questions, refunds or corrections:
    <a href="mailto:maxhemmerich@gmail.com">maxhemmerich@gmail.com</a>. No tracking of individuals. No cookies.
    No personal data. Page views are counted in aggregate &mdash; one number per page, no identifier.</div>
</div></footer>

<script>
const CHECKOUT_URL = "https://maxhemmerich.gumroad.com/l/yolqdo";   // same single slot as the other pages.
const CONTACT = "maxhemmerich@gmail.com";

(function () {{
  const live = typeof CHECKOUT_URL === "string" && CHECKOUT_URL.trim().length > 0;
  document.querySelectorAll("[data-buy]").forEach(function (b) {{
    const cls = b.getAttribute("class") || "btn";
    let replacement;
    if (live) {{
      replacement = document.createElement("a");
      replacement.className = cls;
      replacement.setAttribute("data-buy", "");
      replacement.href = CHECKOUT_URL.trim();
      replacement.target = "_blank";
      replacement.rel = "noopener";
      replacement.textContent = "Get the pack \\u2014 $24 CAD";
    }} else {{
      replacement = document.createElement("button");
      replacement.type = "button";
      replacement.className = cls;
      replacement.setAttribute("data-buy", "");
      replacement.setAttribute("aria-disabled", "true");
      replacement.disabled = true;
      replacement.textContent = "Checkout not connected yet";
    }}
    if (b.parentNode) {{ b.parentNode.replaceChild(replacement, b); }}
  }});
}})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ALPHA_WAGES_CSV")
    if not path:
        raise SystemExit("usage: build_average_page.py <wages.csv>")
    HASH = hashlib.sha256(open(path, "rb").read()).hexdigest()
    rows = load(path)
    html, marks, n_blank, n_dashes = build(rows)
    out = os.path.join(ROOT, "tech-average-pay", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(html)
    print("wrote", out, len(html), "bytes")
    print("source rows in file:", len(rows))
    print("national rows:", len(OCC), "blank national averages:", n_blank)
    print("province cells with an average:", len(OCC) * len(PROV) - n_dashes, "of", len(OCC) * len(PROV))
    print("dash cells:", n_dashes)
    print("province cells by source mark:", dict(marks))
