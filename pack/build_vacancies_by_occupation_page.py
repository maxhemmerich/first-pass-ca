"""Build /tech-vacancies-by-occupation/ — a fifth citable Canadian reference, from a *different*
survey than the three salary pages: Statistics Canada's Job Vacancy and Wage Survey, table
14-10-0444 (Statistics Canada Open Licence, CSV via the no-account WDS endpoint).

Why this cut. The three salary pages rest on ESDC's open-data *Wages* file and answer what a role
is *paid*. /job-vacancies-by-industry/ answers what employers are *trying to hire* on the industry
axis. This page answers the same demand question on the other axis — occupation — and it does it
for exactly the sixteen NOC 2021 unit groups the salary pages cover, so the two can be read side by
side: what the job pays (the salary pages) against how many of it are open and what was offered for
it (this page). It prints the file's own numbers and nothing else:

  * the sixteen technical unit groups, for the latest reference period the file carries:
    job vacancies and the average offered hourly wage;
  * the same sixteen unit groups' job vacancies, across the last four reference periods, so the
    direction is visible without computing anything.

Hard rules, the same as the siblings: every number on the page is a string copied out of the named
CSV — nothing computed, converted, ranked or averaged here; the file's units (a count, an hourly
dollar figure) are carried in the column headings, so each cell is the file's own string; a cell the
file leaves empty renders as a dash; no content or figure from the paid pack.

The CSV is large (roughly 1.2 GB) and carries 83 geographies, so the loader streams it and keeps
only the Canada rows; nothing else is held.

Run:
  py -3.10 pack/build_vacancies_by_occupation_page.py <path-to-14100444.csv>
"""
import csv, os, re, sys, hashlib, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE = {
    "publisher": "Statistics Canada",
    "survey": "Job Vacancy and Wage Survey",
    "table_title": ("Job vacancies and average offered hourly wage by occupation (unit group), "
                    "quarterly, unadjusted for seasonality"),
    "product_id": "14-10-0444",
    "table_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410044401",
    "wds_url": "https://www150.statcan.gc.ca/n1/wds/rest/getFullTableDownloadCSV/14100444/en",
    "resource_url": "https://www150.statcan.gc.ca/n1/tbl/csv/14100444-eng.zip",
    "resource_zip": "14100444-eng.zip",
    "resource_csv": "14100444.csv",
    "licence": "Statistics Canada Open Licence",
    "licence_url": "https://www.statcan.gc.ca/en/reference/licence",
    "read_date": "2026-10-09",
}

NOC_COL = "National Occupational Classification"
# The same sixteen NOC 2021 unit groups the three salary pages cover: software, data, analytics, IT,
# computer engineering. Codes are the file's own; titles are the file's own member names.
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

VAC = "Job vacancies"
WAGE = "Average offered hourly wage"
SERIES = 4                    # quarters of vacancies shown per occupation

CODE_RE = re.compile(r"\s*\[([^\]]+)\]\s*$")


def load_canada(path):
    """Stream the (large) file and return only the Canada rows for the sixteen codes we print,
    keyed by (date, code, statistic) -> record dict."""
    csv.field_size_limit(10 ** 7)
    codes = {c for c, _ in OCC}
    want_stats = {VAC, WAGE}
    keep = {}
    total = 0
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rd = csv.reader(fh)
        hdr = next(rd)
        i_date, i_geo, i_noc, i_stat, i_val = (hdr.index("REF_DATE"), hdr.index("GEO"),
                                               hdr.index(NOC_COL), hdr.index("Statistics"),
                                               hdr.index("VALUE"))
        for r in rd:
            total += 1
            if r[i_geo] != "Canada":
                continue
            if r[i_stat] not in want_stats:
                continue
            m = CODE_RE.search(r[i_noc])
            if not m or m.group(1) not in codes:
                continue
            keep[(r[i_date], m.group(1), r[i_stat])] = r[i_val]
    return keep, total


def cell(v):
    v = (v or "").strip()
    if not v:
        return '<td class="n dim">&mdash;</td>'
    return '<td class="n">%s</td>' % _html.escape(v)


def main(path):
    keep, total = load_canada(path)
    HASH = hashlib.sha256(open(path, "rb").read()).hexdigest()

    dates = sorted({d for (d, _c, _s) in keep})
    latest = dates[-1]
    series_dates = dates[-SERIES:]

    # 01 — the sixteen unit groups, latest period: vacancies + offered wage
    rows1 = []
    for code, title in OCC:
        rows1.append(
            '    <tr><td class="noc">%s</td><td class="occ">%s</td>%s%s</tr>'
            % (_html.escape(code), _html.escape(title),
               cell(keep.get((latest, code, VAC))), cell(keep.get((latest, code, WAGE))))
        )

    # 02 — the same sixteen, vacancies across the last four periods
    rows2 = []
    for code, title in OCC:
        cells = "".join(cell(keep.get((d, code, VAC))) for d in series_dates)
        rows2.append(
            '    <tr><td class="noc">%s</td><td class="occ">%s</td>%s</tr>'
            % (_html.escape(code), _html.escape(title), cells)
        )

    src_line = ("%s, <em>%s</em> (table %s), %s \u2014 %s. Read %s. SHA-256 "
                "<span class=\"mono\">%s</span>." % (
                    SOURCE["publisher"], SOURCE["survey"], SOURCE["product_id"],
                    SOURCE["table_title"].lower(), SOURCE["licence"], SOURCE["read_date"], HASH))

    html = PAGE.format(
        TITLE=TITLE, DESC=DESC, ROWS1="\n".join(rows1), ROWS2="\n".join(rows2),
        SOURCE_LINE=src_line, LATEST=latest, N=len(OCC), NSER=len(series_dates),
        FIRST=series_dates[0], LAST=series_dates[-1],
        LIC_URL=SOURCE["licence_url"], TABLE_URL=SOURCE["table_url"],
        RES_URL=SOURCE["resource_url"], RES_ZIP=SOURCE["resource_zip"],
        RES_CSV=SOURCE["resource_csv"], HASH=HASH, PRODUCT=SOURCE["product_id"],
        PHEAD="".join('<th class="n">%s</th>' % d for d in series_dates),
    )
    out = os.path.join(ROOT, "tech-vacancies-by-occupation", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(html)
    print("wrote", out, len(html), "bytes")
    print("csv rows scanned:", total, "sha256:", HASH)
    print("occupation rows:", len(OCC), "series period(s):", series_dates)


TITLE = "Canadian job vacancies by technical occupation \u2014 the JVWS, occupation by occupation"
DESC = ("Job vacancies and the average hourly wage offered, for the sixteen technical NOC 2021 unit "
        "groups this site already covers by pay, taken from Statistics Canada's Job Vacancy and Wage "
        "Survey (table 14-10-0444, Statistics Canada Open Licence). Every figure carries its source "
        "and the date it was read.")

PAGE = """<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://maxhemmerich.github.io/first-pass-ca/tech-vacancies-by-occupation/">
<meta property="og:type" content="article">
<meta property="og:site_name" content="First Pass">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="https://maxhemmerich.github.io/first-pass-ca/tech-vacancies-by-occupation/">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="How many software, data, security and IT jobs are open in Canada, and what employers offered for them \u2014 from Statistics Canada's own survey.">
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
  .mono{{font-family:var(--mono);font-variant-numeric:tabular-nums;overflow-wrap:anywhere}}
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
  td.dim{{color:#4A4A50}}
  td.noc{{font-family:var(--mono);font-size:12.5px;color:var(--muted)}}
  td.occ{{white-space:normal;min-width:220px;color:#CFCBC1}}
  .tcap{{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin:14px 0 0;max-width:82ch;white-space:normal}}

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
  "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-vacancies-by-occupation/#article",
  "url": "https://maxhemmerich.github.io/first-pass-ca/tech-vacancies-by-occupation/",
  "headline": "{TITLE}",
  "description": "{DESC}",
  "inLanguage": "en-CA",
  "datePublished": "2026-10-09",
  "dateModified": "2026-10-09",
  "author": {{"@type": "Organization", "name": "First Pass"}},
  "publisher": {{"@type": "Organization", "name": "First Pass", "url": "https://maxhemmerich.github.io/first-pass-ca/"}},
  "isPartOf": {{"@type": "WebSite", "@id": "https://maxhemmerich.github.io/first-pass-ca/#website", "url": "https://maxhemmerich.github.io/first-pass-ca/", "name": "First Pass"}},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-vacancies-by-occupation/"}},
  "isBasedOn": {{"@type": "Dataset", "name": "Job Vacancy and Wage Survey, table 14-10-0444", "creator": {{"@type": "GovernmentOrganization", "name": "Statistics Canada"}}, "license": "{LIC_URL}", "url": "{TABLE_URL}"}}
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
  <div class="kicker">Canada &middot; Job Vacancy and Wage Survey &middot; by occupation</div>
  <h1>Canada's technical job vacancies, <span>occupation by occupation</span></h1>
  <p class="lede">The salary pages ask what a technical role <em>pays</em>. This one asks how many of
    those roles are <em>open</em>, and what employers offered to fill them. It takes the sixteen
    technical NOC 2021 unit groups this site already covers by pay and reads the other half of the
    same question out of Statistics Canada's <b>Job Vacancy and Wage Survey</b> &mdash; a different
    survey from the wage file &mdash; with the source and the read date on every figure.</p>
  <div class="facts mono">
    <span>{N} occupation rows</span><span>quarterly, unadjusted</span><span>Statistics Canada</span><span>read 9 October 2026</span>
  </div>
</div></section>

<!-- 01 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">01</div><div>
    <h2>The demand side, occupation by occupation</h2>
    <p class="lede" style="margin-top:12px">Counts are numbers of jobs; the wage is the average
      hourly rate employers advertised for those jobs, in Canadian dollars. Both are reproduced for
      the latest reference period the survey publishes, <span class="mono">{LATEST}</span>, for the
      sixteen technical unit groups this lane covers.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th><th class="n">Job vacancies</th><th class="n">Avg offered wage ($)</th></tr></thead>
    <tbody id="vac-occupation">
{ROWS1}
    </tbody>
  </table>
  </div>
  <p class="tcap">Source: {SOURCE_LINE} A vacancy is a job the employer is actively seeking to fill
    from outside the organisation; the offered wage excludes overtime, tips, commissions and bonuses.
    The wage column is what an employer advertised, not what a hire was later paid.</p>
</div></section>

<!-- 02 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">02</div><div>
    <h2>The same sixteen, quarter by quarter</h2>
    <p class="lede" style="margin-top:12px">The same unit groups' <span class="mono">Job vacancies</span>
      across the last {NSER} reference periods the file carries
      (<span class="mono">{FIRST}</span> to <span class="mono">{LAST}</span>). The survey's quarters
      arrive one at a time, so this is the direction of travel as printed, not a forecast.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th>{PHEAD}</tr></thead>
    <tbody id="vac-occupation-series">
{ROWS2}
    </tbody>
  </table>
  </div>
  <p class="tcap">The file is quarterly and runs from 2015-01 onward, with the second and third
    quarters of 2020 suspended. The four periods above are the most recent the file carries; none is a
    projection. A period the file leaves blank for an occupation is shown as a dash, not as a zero.</p>
</div></section>

<!-- 03 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">03</div><div>
    <h2>What this page is, and what it is not</h2>
  </div></div>
  <ul class="limits">
    <li><b>A single source.</b> Every row above is a string out of one Statistics Canada table,
      <span class="mono">{PRODUCT}</span>, from the Job Vacancy and Wage Survey and published under the
      <a href="{LIC_URL}">Statistics Canada Open Licence</a>. The CSV read here
      (<span class="mono">{RES_CSV}</span>, unpacked from <span class="mono">{RES_ZIP}</span>) hashes to
      <span class="mono">{HASH}</span>; <a href="{TABLE_URL}">the table page</a> and
      <a href="{RES_URL}">the download</a> are where a reader can confirm it.</li>
    <li><b>Sixteen rows, chosen and named.</b> The occupations are the unit groups this lane covers,
      picked to mirror the salary pages and listed by NOC code so the choice is visible. They are a
      slice of the file's hundreds of occupations, not the whole labour market.</li>
    <li><b>A vacancy is an unfilled post.</b> Statistics Canada counts a job only where the employer is
      taking steps to recruit someone from outside the organisation to fill it, so a post that is filled,
      or one nobody is chasing, is not counted. What the table reads is employer demand, not every
      opening there is.</li>
    <li><b>The wage is the advertised one.</b> The survey records the rate an employer posted, and the
      lower end of a range where a range was published. What a hire is actually paid is a different
      survey's question &mdash; the one the salary pages ask.</li>
    <li><b>The quarters are not seasonally adjusted.</b> These are the survey's own raw quarterly
      figures, so a July quarter and a January quarter are not like for like. Read them as counts on the
      date printed.</li>
    <li><b>Occupations and an economy, not a job ad.</b> Nothing here names an employer or a single
      opening, and none of it is advice. No part of this page is drawn out of the paid pack.</li>
  </ul>
  <div class="pull">
    <p>The survey's other axis is <a href="../job-vacancies-by-industry/">job vacancies industry by
      industry</a>. Its vacancy-rate and payroll-employee measures for these occupations sit in the same
      table and are left off here so each row lines up with the salary pages. Statistics Canada publishes
      the CSV for reuse with attribution; the links above are the whole source.</p>
  </div>
</div></section>

<!-- 04 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">04</div><div>
    <h2>Where this sits</h2>
    <p class="lede" style="margin-top:12px">This page is the demand half, by occupation. What the
      same roles pay, cut three ways, is on the salary pages; what employers asked and how to answer
      is the free report and the pack.</p>
  </div></div>
  <p style="color:#CFCBC1;font-size:14.5px;margin-bottom:22px">Paid wages by occupation:
    <a href="../tech-salaries/">tech salaries across Canada &rarr;</a> &middot; the same roles by urban
    region: <a href="../tech-salaries-by-city/">tech salaries by city &rarr;</a> &middot; the file's
    average column: <a href="../tech-average-pay/">average pay, by occupation &rarr;</a> &middot; the
    demand side by industry: <a href="../job-vacancies-by-industry/">job vacancies by industry &rarr;</a> &middot; the decade ahead: <a href="../tech-job-projections/">projected technical job openings to 2033 &rarr;</a></p>
  <div class="two">
    <div class="free">
      <div class="kicker">Free &middot; no email</div>
      <h3 style="margin-top:10px">The Screen Report</h3>
      <p style="color:#CFCBC1;font-size:14.5px;margin-top:10px">The measured other half of a search:
        the screening questions the postings asked, and every salary band they printed.</p>
      <a class="btn ghost" href="../free-report/">Open the free Screen Report &rarr;</a>
    </div>
    <div class="paid">
      <div class="paid-head"><h3>The First Pass pack</h3><span class="p mono">$24 CAD</span></div>
      <p style="padding:14px 18px;margin:0;font-size:14.5px;color:#CFCBC1">The pack is the search built
        on these numbers: a keyword map for each role, an answer shape for every screening question,
        three salary scripts and a Canadian negotiation section, across 21 pages.</p>
      <p style="padding:12px 18px;margin:0;border-top:1px solid var(--rule);font-size:13.5px"><a href="../whats-in-the-pack/">See what is inside, section by section &rarr;</a></p>
      <div class="paid-foot">
        <a class="btn sm" data-buy href="https://maxhemmerich.gumroad.com/l/yolqdo" target="_blank" rel="noopener">Get the pack</a>
        <span class="mono" style="color:var(--muted);font-size:11.5px">One PDF &middot; $24 CAD, paid once</span>
      </div>
    </div>
  </div>
</div></section>

<footer><div class="wrap">
  <div class="mono">FIRST PASS &middot; sixteen technical occupations, read 9 October 2026 &middot; <a href="../" style="border-bottom:0">the full page</a> &middot; <a href="../free-report/" style="border-bottom:0">the Screen Report</a></div>
  <div class="fnote">Vacancy figures are reproduced from Statistics Canada's <em>Job Vacancy and Wage
    Survey</em>, which is published under the <a href="{LIC_URL}">Statistics Canada Open Licence</a>;
    this page carries that information with attribution and is neither endorsed by nor affiliated with
    Statistics Canada. Questions, refunds or corrections:
    <a href="mailto:maxhemmerich@gmail.com">maxhemmerich@gmail.com</a>. No tracking of individuals, no cookies and no personal data on this site. Page views are counted in aggregate &mdash; one number per page, no identifier.</div>
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
    if len(sys.argv) < 2:
        raise SystemExit("usage: build_vacancies_by_occupation_page.py <path-to-14100444.csv>")
    main(sys.argv[1])
