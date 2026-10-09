"""Build /job-vacancies-by-industry/ — a fourth citable Canadian reference, from a *different*
source than the three salary pages: Statistics Canada's Job Vacancy and Wage Survey, table
14-10-0442 (Statistics Canada Open Licence, CSV via the no-account WDS endpoint).

Why this cut. The three salary pages all rest on ESDC's open-data *Wages* file and all answer the
same question sideways: what a role is *paid*. This page answers the other half of a job search —
what employers are *trying to hire* — and it does so on a different axis (industry, not occupation)
from a different survey. It prints the file's own numbers and nothing else:

  * every one of the twenty NAICS sectors the file publishes, plus "Total, all industries", for the
    latest reference period: job vacancies, job vacancy rate, and the average offered hourly wage;
  * the same three measures for the whole economy, quarter by quarter, over the last twelve
    reference periods the file carries.

Hard rules, the same as the siblings: every number on the page is a string copied out of the named
CSV — nothing computed, converted, ranked or averaged here; the file's units (a count, a percent, an
hourly dollar figure) are carried in the column headings, so each cell is the file's own string; a
cell the file leaves empty renders as a dash; no content or figure from the paid pack.

Run:
  py -3.10 pack/build_vacancy_page.py <path-to-14100442.csv>
"""
import csv, os, re, sys, hashlib, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE = {
    "publisher": "Statistics Canada",
    "survey": "Job Vacancy and Wage Survey",
    "table_title": ("Job vacancies, payroll employees, job vacancy rate, and average offered hourly "
                    "wage by industry sub-sector, quarterly, unadjusted for seasonality"),
    "product_id": "14-10-0442",
    "table_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410044201",
    "wds_url": "https://www150.statcan.gc.ca/n1/wds/rest/getFullTableDownloadCSV/14100442/en",
    "resource_url": "https://www150.statcan.gc.ca/n1/tbl/csv/14100442-eng.zip",
    "resource_file": "14100442-eng.zip",
    "licence": "Statistics Canada Open Licence",
    "licence_url": "https://www.statcan.gc.ca/en/reference/licence",
    "read_date": "2026-10-09",
}

NAICS_COL = "North American Industry Classification System (NAICS)"
LATEST = "2026-04"          # the latest reference period the file carries
SERIES = 12                 # whole-economy quarters shown

SECTOR_RE = re.compile(r"\[(?:[0-9]{2}|[0-9]{2}-[0-9]{2})\]$")


def load(path):
    csv.field_size_limit(10 ** 7)
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def parse(name):
    """'Manufacturing [31-33]' -> ('Manufacturing', '[31-33]'); 'Total, all industries' -> (name, None)."""
    m = re.search(r"\s*\[([^\]]+)\]$", name)
    if m:
        return name[:m.start()].strip(), "[" + m.group(1) + "]"
    return name.strip(), None


def lookup(rows, date, geo, naics, stat):
    for r in rows:
        if (r["REF_DATE"] == date and r["GEO"] == geo and r[NAICS_COL] == naics
                and r["Statistics"] == stat):
            return r
    return None


def main(path):
    rows = load(path)
    HASH = hashlib.sha256(open(path, "rb").read()).hexdigest()

    # the file's own sector rows, in the file's own order (first appearance).
    industries = []
    for r in rows:
        n = r[NAICS_COL]
        if n == "Total, all industries" or SECTOR_RE.search(n):
            if n not in industries:
                industries.append(n)

    dates = sorted({r["REF_DATE"] for r in rows})
    series_dates = dates[-SERIES:]

    def cell(rec, stat):
        if rec is None:
            return '<td class="n dim">&mdash;</td>'
        v = (rec["VALUE"] or "").strip()
        if not v:
            return '<td class="n dim">&mdash;</td>'
        return '<td class="n">%s</td>' % _html.escape(v)

    # 01 — by industry, latest period, Canada
    ind_rows = []
    for n in industries:
        title, code = parse(n)
        vac = lookup(rows, LATEST, "Canada", n, "Job vacancies")
        rate = lookup(rows, LATEST, "Canada", n, "Job vacancy rate")
        wage = lookup(rows, LATEST, "Canada", n, "Average offered hourly wage")
        ind_rows.append(
            '    <tr><td class="noc">%s</td><td class="occ">%s</td>%s%s%s</tr>'
            % (_html.escape(code) if code else "&mdash;", _html.escape(title),
               cell(vac, "Job vacancies"), cell(rate, "Job vacancy rate"),
               cell(wage, "Average offered hourly wage"))
        )

    # 02 — whole economy, quarter by quarter
    ser_rows = []
    for d in series_dates:
        vac = lookup(rows, d, "Canada", "Total, all industries", "Job vacancies")
        rate = lookup(rows, d, "Canada", "Total, all industries", "Job vacancy rate")
        wage = lookup(rows, d, "Canada", "Total, all industries", "Average offered hourly wage")
        ser_rows.append(
            '    <tr><td class="noc">%s</td>%s%s%s</tr>'
            % (_html.escape(d), cell(vac, "Job vacancies"), cell(rate, "Job vacancy rate"),
               cell(wage, "Average offered hourly wage"))
        )

    src_line = ("%s, <em>%s</em> (table %s), %s \u2014 %s. Read %s. SHA-256 "
                "<span class=\"mono\">%s</span>." % (
                    SOURCE["publisher"], SOURCE["survey"], SOURCE["product_id"],
                    SOURCE["table_title"].lower(), SOURCE["licence"], SOURCE["read_date"], HASH))

    html = PAGE.format(
        TITLE=TITLE, DESC=DESC, IND_ROWS="\n".join(ind_rows), SER_ROWS="\n".join(ser_rows),
        SOURCE_LINE=src_line, LATEST=LATEST, N=len(industries), NSER=len(series_dates),
        LIC_URL=SOURCE["licence_url"], TABLE_URL=SOURCE["table_url"],
        RES_URL=SOURCE["resource_url"], RES_FILE=SOURCE["resource_file"], HASH=HASH,
        FIRST=series_dates[0], LAST=series_dates[-1], PRODUCT=SOURCE["product_id"],
    )
    out = os.path.join(ROOT, "job-vacancies-by-industry", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(html)
    print("wrote", out, len(html), "bytes")
    print("csv rows:", len(rows), "sha256:", HASH)
    print("industry rows:", len(industries), "series rows:", len(series_dates),
          "(%s..%s)" % (series_dates[0], series_dates[-1]))


TITLE = "Canadian job vacancies by industry \u2014 who is hiring, from the JVWS"
DESC = ("Job vacancies, the job vacancy rate and the average hourly wage offered, for all twenty "
        "industry sectors in Canada and for the whole economy quarter by quarter, taken from "
        "Statistics Canada's Job Vacancy and Wage Survey (Statistics Canada Open Licence). Every "
        "figure carries its source and the date it was read.")

PAGE = """<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://maxhemmerich.github.io/first-pass-ca/job-vacancies-by-industry/">
<meta property="og:type" content="article">
<meta property="og:site_name" content="First Pass">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="https://maxhemmerich.github.io/first-pass-ca/job-vacancies-by-industry/">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="Canada's twenty industry sectors: how many jobs are open, the vacancy rate, and the wage offered \u2014 from Statistics Canada's own survey.">
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
  td.n.tot{{color:var(--accent)}}
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
  "@id": "https://maxhemmerich.github.io/first-pass-ca/job-vacancies-by-industry/#article",
  "url": "https://maxhemmerich.github.io/first-pass-ca/job-vacancies-by-industry/",
  "headline": "{TITLE}",
  "description": "{DESC}",
  "inLanguage": "en-CA",
  "datePublished": "2026-10-09",
  "dateModified": "2026-10-09",
  "author": {{"@type": "Organization", "name": "First Pass"}},
  "publisher": {{"@type": "Organization", "name": "First Pass", "url": "https://maxhemmerich.github.io/first-pass-ca/"}},
  "isPartOf": {{"@type": "WebSite", "@id": "https://maxhemmerich.github.io/first-pass-ca/#website", "url": "https://maxhemmerich.github.io/first-pass-ca/", "name": "First Pass"}},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://maxhemmerich.github.io/first-pass-ca/job-vacancies-by-industry/"}},
  "isBasedOn": {{"@type": "Dataset", "name": "Job Vacancy and Wage Survey, table 14-10-0442", "creator": {{"@type": "GovernmentOrganization", "name": "Statistics Canada"}}, "license": "{LIC_URL}", "url": "{TABLE_URL}"}}
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
  <div class="kicker">Canada &middot; Job Vacancy and Wage Survey &middot; the demand side</div>
  <h1>Canada's job vacancies, <span>industry by industry</span></h1>
  <p class="lede">Every other reference on this site measures what a job <em>pays</em>. This one
    measures what employers are trying to <em>fill</em>, from a different survey altogether:
    Statistics Canada's <b>Job Vacancy and Wage Survey</b>, which counts the jobs left open on a
    reference date and the wage offered for them. The page prints, for each of the country's
    <b>{N}</b> published industry sectors and for the whole economy quarter by quarter, the number of
    vacancies, the vacancy rate, and the average offered hourly wage &mdash; each one the survey's
    own figure, with the source and the date it was read.</p>
  <div class="facts mono">
    <span>{N} industry rows</span><span>quarterly, unadjusted</span><span>Statistics Canada</span><span>read 9 October 2026</span>
  </div>
</div></section>

<!-- 01 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">01</div><div>
    <h2>The demand side, industry by industry</h2>
    <p class="lede" style="margin-top:12px">Counts are numbers of jobs; the rate is the share of
      labour demand left vacant, in percent; the wage is the average hourly rate employers offered for
      those jobs, in Canadian dollars. All three are reproduced for the latest reference period the
      survey publishes, <span class="mono">{LATEST}</span>.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NAICS</th><th>Industry</th><th class="n">Job vacancies</th><th class="n">Vacancy rate (%)</th><th class="n">Avg offered wage ($)</th></tr></thead>
    <tbody id="vac-industry">
{IND_ROWS}
    </tbody>
  </table>
  </div>
  <p class="tcap">Source: {SOURCE_LINE} A vacancy is a job the employer is actively seeking to fill from
    outside the organisation; the rate is vacancies as a share of all occupied and vacant jobs; the
    offered wage excludes overtime, tips, commissions and bonuses. These are wages <em>offered</em>,
    not wages paid.</p>
</div></section>

<!-- 02 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">02</div><div>
    <h2>The whole economy, quarter by quarter</h2>
    <p class="lede" style="margin-top:12px"><span class="mono">Total, all industries</span> for all of
      Canada, printed across the last {NSER} reference periods in the file
      (<span class="mono">{FIRST}</span> to <span class="mono">{LAST}</span>), on the same three
      measures. The survey's quarters arrive one at a time, so this is a direction of travel, not a
      forecast.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>Period</th><th class="n">Job vacancies</th><th class="n">Vacancy rate (%)</th><th class="n">Avg offered wage ($)</th></tr></thead>
    <tbody id="vac-series">
{SER_ROWS}
    </tbody>
  </table>
  </div>
  <p class="tcap">The file is quarterly and covers every quarter from 2015-01 onward except the second
    and third quarters of 2020, which Statistics Canada suspended. The twelve periods above are the
    most recent the file carries; none is a projection.</p>
</div></section>

<!-- 03 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">03</div><div>
    <h2>Reading this page honestly</h2>
  </div></div>
  <ul class="limits">
    <li><b>One survey, one file.</b> The whole page rests on a single Statistics Canada table,
      <span class="mono">{PRODUCT}</span> from the Job Vacancy and Wage Survey, published under the
      <a href="{LIC_URL}">Statistics Canada Open Licence</a>. The CSV read here is
      <span class="mono">{RES_FILE}</span>; it hashes to <span class="mono">{HASH}</span>, and
      <a href="{TABLE_URL}">the table page</a> plus <a href="{RES_URL}">the download</a> are where that
      can be checked.</li>
    <li><b>Vacant means actively sought.</b> The survey counts a job as vacant only if the employer is
      taking steps to recruit someone from outside the organisation for it, so a filled post, a
      cancelled req or a role nobody is chasing is not in the total. It is a reading of employer
      demand, not a count of every opening that will ever exist.</li>
    <li><b>Offered, not paid.</b> The wage column is what employers advertised for the open jobs, and
      the survey records the bottom of a range when one is posted. The wage those same jobs actually
      pay once filled is a different survey's question, and it is the one the salary pages ask.</li>
    <li><b>Unadjusted for seasonality.</b> This is the survey's own unadjusted series, so a summer
      quarter and a winter quarter are not like for like. Read the twelve-period table as counts as
      printed, not as a seasonally-smoothed line.</li>
    <li><b>Data-quality marks.</b> Statistics Canada stamps each estimate with a quality letter: in the
      sector table <span class="mono">A</span> means excellent and <span class="mono">B</span> very good.
      The page prints the figure either way; the mark is the file's own.</li>
    <li><b>A snapshot, not a posting.</b> The table describes sectors and an economy, not a particular
      employer or a particular job, and nothing on it is guidance of any kind. Nothing here is drawn
      from the paid pack.</li>
  </ul>
  <div class="pull">
    <p>The survey also carries each sector's smaller pieces &mdash; sub-sectors such as computing
      infrastructure providers and data processing <span class="mono">[518]</span> inside information
      and cultural industries, and computer and electronic product manufacturing
      <span class="mono">[334]</span> &mdash; but this page stays at the sector level so every row is
      the file's own published aggregate. The CSV is free to reuse with attribution, and the link above
      is the whole source.</p>
  </div>
</div></section>

<!-- 04 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">04</div><div>
    <h2>Where this sits</h2>
    <p class="lede" style="margin-top:12px">This page is the demand half. What the roles pay, cut three
      ways, is on the salary pages; what employers actually asked and how to answer is the free report
      and the pack.</p>
  </div></div>
  <p style="color:#CFCBC1;font-size:14.5px;margin-bottom:22px">Paid wages by occupation:
    <a href="../tech-salaries/">tech salaries across Canada &rarr;</a> &middot; the same roles by urban
    region: <a href="../tech-salaries-by-city/">tech salaries by city &rarr;</a> &middot; the file's
    average column: <a href="../tech-average-pay/">average pay, by occupation &rarr;</a> &middot; the same
    survey on its occupation axis: <a href="../tech-vacancies-by-occupation/">tech job vacancies by
    occupation &rarr;</a> &middot; the federal projection model's look ahead: <a href="../tech-job-projections/">projected tech openings to 2033 &rarr;</a> &middot; the exit side, from the benefit that follows a job loss: <a href="../tech-layoffs/">tech layoffs by occupation &rarr;</a></p>
  <div class="two">
    <div class="free">
      <div class="kicker">Free &middot; no email</div>
      <h3 style="margin-top:10px">The Screen Report</h3>
      <p style="color:#CFCBC1;font-size:14.5px;margin-top:10px">The other half of a search, measured: the
        screening questions the postings asked and every salary band they printed.</p>
      <a class="btn ghost" href="../free-report/">Read the Screen Report &rarr;</a>
    </div>
    <div class="paid">
      <div class="paid-head"><h3>The First Pass pack</h3><span class="p mono">$24 CAD</span></div>
      <p style="padding:14px 18px;margin:0;font-size:14.5px;color:#CFCBC1">The pack turns the numbers into
        a search &mdash; a keyword map per role, an answer shape for each screening question, three salary
        scripts and a negotiation section written for Canada, in 21 pages.</p>
      <p style="padding:12px 18px;margin:0;border-top:1px solid var(--rule);font-size:13.5px"><a href="../whats-in-the-pack/">The eight sections, page by page &rarr;</a></p>
      <div class="paid-foot">
        <a class="btn sm" data-buy href="https://maxhemmerich.gumroad.com/l/yolqdo" target="_blank" rel="noopener">Get the pack</a>
        <span class="mono" style="color:var(--muted);font-size:11.5px">One PDF &middot; $24 CAD, paid once</span>
      </div>
    </div>
  </div>
</div></section>

<footer><div class="wrap">
  <div class="mono">FIRST PASS &middot; Canada &middot; vacancy data read 9 October 2026 &middot; <a href="../" style="border-bottom:0">the full page</a> &middot; <a href="../free-report/" style="border-bottom:0">the Screen Report</a></div>
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
        raise SystemExit("usage: build_vacancy_page.py <path-to-14100442.csv>")
    main(sys.argv[1])
