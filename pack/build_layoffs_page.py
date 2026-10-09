"""Build /tech-layoffs/ — a seventh citable Canadian reference, from a *third* dataset again:
Statistics Canada's table 14-10-0455, employment insurance beneficiaries (regular benefits) by
province, territory and occupation, monthly (Statistics Canada Open Licence, CSV via the
no-account WDS endpoint).

Why this cut. The salary pages say what a role is paid (ESDC's *Wages* file). The two vacancy
pages and /job-vacancies-by-industry/ say what employers are trying to fill (Statistics Canada's
Job Vacancy and Wage Survey). /tech-job-projections/ says what the federal model expects over the
decade (ESDC's COPS). None of them says what the *other* side of a search looks like: how many
people in these occupations have already lost a job and are drawing the benefit that follows one.
That is what this table counts — EI beneficiaries receiving regular income benefits, by the
occupation of the claim — and it is a different programme's record from every source above.

It prints the file's own numbers and nothing else:

  * the sixteen technical unit groups at the latest reference period the file carries: regular EI
    beneficiaries in Canada, beside the same month one year earlier, so the direction is visible
    without computing anything;
  * the same sixteen unit groups month by month across the last twelve reference periods.

Hard rules, the same as the siblings: every number on the page is a string copied out of the named
CSV — nothing computed, converted, ranked, summed or averaged here; the file's unit (persons) is
carried in the column headings, so each cell is the file's own string; a cell the file leaves empty
or suppresses renders as a dash; no content or figure from the paid pack.

The CSV is large (roughly 440 MB) and carries 15 geographies and 824 occupation members, so the
loader streams it and keeps only the Canada rows for the sixteen codes; nothing else is held.

Run:
  py -3.10 pack/build_layoffs_page.py <path-to-14100455.csv>
"""
import csv, os, re, sys, hashlib, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE = {
    "publisher": "Statistics Canada",
    "survey": "Employment Insurance Statistics",
    "table_title": ("Employment insurance beneficiaries (regular benefits) by province, territory "
                    "and occupation, monthly, unadjusted for seasonality"),
    "product_id": "14-10-0455",
    "table_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410045501",
    "wds_url": "https://www150.statcan.gc.ca/n1/wds/rest/getFullTableDownloadCSV/14100455/en",
    "resource_url": "https://www150.statcan.gc.ca/n1/tbl/csv/14100455-eng.zip",
    "resource_zip": "14100455-eng.zip",
    "resource_csv": "14100455.csv",
    "licence": "Statistics Canada Open Licence",
    "licence_url": "https://www.statcan.gc.ca/en/reference/licence",
    "read_date": "2026-10-09",
}

OCC_COL = "Occupations"
# The same sixteen NOC 2021 unit groups the salary, vacancy and projection pages cover.
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

SERIES = 12                    # months of the claimant count shown per occupation
CODE_RE = re.compile(r"\s*\[([^\]]+)\]\s*$")


def sha256_stream(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_canada(path):
    """Stream the (large) file and keep the Canada rows of the sixteen codes only:
    (date, code) -> (value, status)."""
    codes = {c for c, _ in OCC}
    keep = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rd = csv.reader(fh)
        hdr = next(rd)
        i_date, i_geo = hdr.index("REF_DATE"), hdr.index("GEO")
        i_occ, i_val, i_st = hdr.index(OCC_COL), hdr.index("VALUE"), hdr.index("STATUS")
        for r in rd:
            if r[i_geo] != "Canada":
                continue
            m = CODE_RE.search(r[i_occ])
            if not m or m.group(1) not in codes:
                continue
            keep[(r[i_date], m.group(1))] = (r[i_val], r[i_st])
    return keep


def cell(v):
    """The file's own string, or a dash where the file is silent or suppresses the cell."""
    val, status = v if v is not None else ("", "")
    val = (val or "").strip()
    if not val or status.strip().lower() == "x":
        return '<td class="n dim">&mdash;</td>'
    return '<td class="n">%s</td>' % _html.escape(val)


def main(path):
    keep = load_canada(path)
    HASH = sha256_stream(path)

    dates = sorted({d for (d, _c) in keep})
    latest = dates[-1]
    y, mo = latest.split("-")
    prior = "%d-%s" % (int(y) - 1, mo)          # the same month one year earlier
    series_dates = dates[-SERIES:]

    # 01 — the sixteen unit groups: latest month, and the same month a year earlier
    rows1 = []
    for code, title in OCC:
        rows1.append(
            '    <tr><td class="noc">%s</td><td class="occ">%s</td>%s%s</tr>'
            % (_html.escape(code), _html.escape(title),
               cell(keep.get((latest, code))), cell(keep.get((prior, code))))
        )

    # 02 — the same sixteen, month by month
    rows2 = []
    for code, title in OCC:
        cells = "".join(cell(keep.get((d, code))) for d in series_dates)
        rows2.append(
            '    <tr><td class="noc">%s</td><td class="occ">%s</td>%s</tr>'
            % (_html.escape(code), _html.escape(title), cells)
        )

    src_line = ("%s, <em>%s</em> (%s) \u2014 %s, %s. Read %s. SHA-256 "
                "<span class=\"mono\">%s</span>." % (
                    SOURCE["publisher"], SOURCE["table_title"], SOURCE["product_id"],
                    SOURCE["survey"], SOURCE["licence"], SOURCE["read_date"], HASH))

    html = PAGE.format(
        TITLE=TITLE, DESC=DESC, ROWS1="\n".join(rows1), ROWS2="\n".join(rows2),
        SOURCE_LINE=src_line, LATEST=latest, PRIOR=prior, N=len(OCC), NSER=len(series_dates),
        FIRST=series_dates[0], LAST=series_dates[-1],
        LIC_URL=SOURCE["licence_url"], TABLE_URL=SOURCE["table_url"],
        RES_URL=SOURCE["resource_url"], RES_ZIP=SOURCE["resource_zip"],
        RES_CSV=SOURCE["resource_csv"], HASH=HASH, PRODUCT=SOURCE["product_id"],
        PHEAD="".join('<th class="n">%s</th>' % d for d in series_dates),
    )
    out = os.path.join(ROOT, "tech-layoffs", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(html)
    print("wrote", out, len(html), "bytes")
    print("sha256:", HASH)
    print("occupation rows:", len(OCC), "latest:", latest, "prior:", prior)
    print("series:", series_dates)


TITLE = "Tech layoffs in Canada, counted \u2014 EI claimants by technical occupation"
DESC = ("How many people in each Canadian technical occupation are drawing regular Employment "
        "Insurance benefits, month by month, for the sixteen NOC 2021 unit groups this site covers \u2014 "
        "from Statistics Canada's table 14-10-0455 (Statistics Canada Open Licence). Every figure "
        "carries its source and the date it was read.")

PAGE = """<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://maxhemmerich.github.io/first-pass-ca/tech-layoffs/">
<meta property="og:type" content="article">
<meta property="og:site_name" content="First Pass">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="https://maxhemmerich.github.io/first-pass-ca/tech-layoffs/">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="The other side of a Canadian tech job search, counted: how many people in each technical occupation are on regular EI benefits, month by month, from Statistics Canada.">
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
  "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-layoffs/#article",
  "url": "https://maxhemmerich.github.io/first-pass-ca/tech-layoffs/",
  "headline": "{TITLE}",
  "description": "{DESC}",
  "inLanguage": "en-CA",
  "datePublished": "2026-10-09",
  "dateModified": "2026-10-09",
  "author": {{"@type": "Organization", "name": "First Pass"}},
  "publisher": {{"@type": "Organization", "name": "First Pass", "url": "https://maxhemmerich.github.io/first-pass-ca/"}},
  "isPartOf": {{"@type": "WebSite", "@id": "https://maxhemmerich.github.io/first-pass-ca/#website", "url": "https://maxhemmerich.github.io/first-pass-ca/", "name": "First Pass"}},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-layoffs/"}},
  "isBasedOn": {{"@type": "Dataset", "name": "Employment insurance beneficiaries (regular benefits) by province, territory and occupation, table 14-10-0455", "creator": {{"@type": "GovernmentOrganization", "name": "Statistics Canada"}}, "license": "{LIC_URL}", "url": "{TABLE_URL}"}}
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
  <div class="kicker">Canada &middot; Employment Insurance &middot; by occupation</div>
  <h1>Canada's technical layoffs, <span>counted</span></h1>
  <p class="lede">Every other reference on this site measures the market you are about to enter.
    This one measures the people who have just left it. It is not a list of announced job cuts;
    it is the benefit that follows one &mdash; the number of people in each technical occupation
    drawing <b>regular Employment Insurance</b>, counted by Statistics Canada and broken out by the
    occupation of the claim. The page prints, for the sixteen technical NOC 2021 unit groups this
    lane covers, that count at the latest reference period and month by month across the year, each
    figure the file's own, with the source and the date it was read.</p>
  <div class="facts mono">
    <span>{N} occupation rows</span><span>monthly, unadjusted</span><span>Statistics Canada</span><span>read 9 October 2026</span>
  </div>
</div></section>

<!-- 01 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">01</div><div>
    <h2>The sixteen technical occupations, at the latest reading</h2>
    <p class="lede" style="margin-top:12px">Each cell is a count of people, in Canada, receiving
      regular Employment Insurance benefits on the reference date and recorded under that occupation.
      Two columns are printed side by side &mdash; the newest month the file carries,
      <span class="mono">{LATEST}</span>, and the same month a year earlier,
      <span class="mono">{PRIOR}</span> &mdash; so the year-on-year direction is visible without
      anyone having to subtract.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th><th class="n">{LATEST} (persons)</th><th class="n">{PRIOR} (persons)</th></tr></thead>
    <tbody id="ei-latest">
{ROWS1}
    </tbody>
  </table>
  </div>
  <p class="tcap">Source: {SOURCE_LINE} A person is counted once per month under the occupation of
    the job they last held; the series is not adjusted for season, so the same month in two different
    years is the honest comparison, not two months side by side.</p>
</div></section>

<!-- 02 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">02</div><div>
    <h2>The same sixteen, month by month</h2>
    <p class="lede" style="margin-top:12px">Regular-benefit claimants in each of the sixteen unit
      groups, at every reference period from <span class="mono">{FIRST}</span> to
      <span class="mono">{LAST}</span> &mdash; the last {NSER} months the file carries. The column
      headings are the file's own reference dates; a cell the file suppresses is a dash, not a zero.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th>{PHEAD}</tr></thead>
    <tbody id="ei-series">
{ROWS2}
    </tbody>
  </table>
  </div>
  <p class="tcap">Read down a row, not across it: because the counts are unadjusted, a summer month
    and a winter month differ for seasonal reasons before any hiring signal. The comparable reading is
    the same month of the previous year, which is what the first table prints. Nothing in this table is
    a projection.</p>
</div></section>

<!-- 03 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">03</div><div>
    <h2>What this page counts, and what it does not</h2>
  </div></div>
  <ul class="limits">
    <li><b>One programme, one table.</b> Everything above comes from a single Statistics Canada
      table, <span class="mono">{PRODUCT}</span>, from the Employment Insurance Statistics programme
      and published under the <a href="{LIC_URL}">Statistics Canada Open Licence</a>. The CSV read here
      (<span class="mono">{RES_CSV}</span>, unpacked from <span class="mono">{RES_ZIP}</span>) hashes to
      <span class="mono">{HASH}</span>; <a href="{TABLE_URL}">the table page</a> and
      <a href="{RES_URL}">the download</a> are where a reader can confirm every figure.</li>
    <li><b>A claimant, not an announcement.</b> This is the administrative count of people actually
      drawing regular benefits. It is a different thing from the number of layoffs a company announces,
      because a separation only lands here once it happens and the person qualifies and applies. The
      page therefore lags the news, and undercounts it.</li>
    <li><b>Counted under the last job, not the current one.</b> A claimant is filed under the
      occupation of the work they lost. Someone retraining into a different field still counts under
      the old one, so this is a reading of where job losses landed, not of who is in the field now.</li>
    <li><b>Small numbers move a lot.</b> Several of these occupations number in the low hundreds
      nationally, so a month-to-month change of a few dozen people is noise as much as signal. Compare
      the same month across years and treat the direction, not the single reading.</li>
    <li><b>Unadjusted for season.</b> The programme publishes raw monthly counts, so winter is
      routinely higher than summer for reasons that have nothing to do with a particular occupation. No
      seasonal adjustment has been applied here or anywhere on this page.</li>
    <li><b>A snapshot, and not advice.</b> The table describes occupations and a country, not an
      employer or a job ad, and nothing on it is guidance of any kind. Whatever is inside the paid
      document, it is not the source of anything printed here.</li>
  </ul>
  <div class="pull">
    <p>The demand side of the same question &mdash; what employers <em>are</em> hiring for &mdash; is on
      the <a href="../tech-vacancies-by-occupation/">vacancy page</a>, and the decade ahead on the
      <a href="../tech-job-projections/">projection page</a>. Read together, the three say how many of
      a role are open, how many of it the government expects, and how many of it have just come
      loose. The whole of the figures above is that one open-licensed file, reproduced with the
      attribution the licence asks for.</p>
  </div>
</div></section>

<!-- 04 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">04</div><div>
    <h2>Where this sits</h2>
    <p class="lede" style="margin-top:12px">This page is the exit side of the market. What the same
      roles pay, how many are open, and what the screen asks are the pages beside it.</p>
  </div></div>
  <p style="color:#CFCBC1;font-size:14.5px;margin-bottom:22px">Paid wages by occupation:
    <a href="../tech-salaries/">tech salaries across Canada &rarr;</a> &middot; the same roles by urban
    region: <a href="../tech-salaries-by-city/">tech salaries by city &rarr;</a> &middot; the file's
    average column: <a href="../tech-average-pay/">average pay, by occupation &rarr;</a> &middot; what
    employers are trying to fill, by industry: <a href="../job-vacancies-by-industry/">job vacancies by industry &rarr;</a> &middot; the same demand by occupation: <a href="../tech-vacancies-by-occupation/">tech job vacancies by occupation &rarr;</a> &middot; the decade ahead: <a href="../tech-job-projections/">projected technical job openings to 2033 &rarr;</a></p>
  <div class="two">
    <div class="free">
      <div class="kicker">Free &middot; no email</div>
      <h3 style="margin-top:10px">The Screen Report</h3>
      <p style="color:#CFCBC1;font-size:14.5px;margin-top:10px">What the postings on the other side
        of this market actually asked, and every salary band they printed.</p>
      <a class="btn ghost" href="../free-report/">Read the Screen Report &rarr;</a>
    </div>
    <div class="paid">
      <div class="paid-head"><h3>The First Pass pack</h3><span class="p mono">$24 CAD</span></div>
      <p style="padding:14px 18px;margin:0;font-size:14.5px;color:#CFCBC1">Whichever way the counts
        above are moving, the rest of the search is the same: a keyword map for the role, an answer
        shape for every screening question, three salary scripts and a Canadian negotiation section,
        in 21 pages.</p>
      <p style="padding:12px 18px;margin:0;border-top:1px solid var(--rule);font-size:13.5px"><a href="../whats-in-the-pack/">The pack, section by section &rarr;</a></p>
      <div class="paid-foot">
        <a class="btn sm" data-buy href="https://maxhemmerich.gumroad.com/l/yolqdo" target="_blank" rel="noopener">Get the pack</a>
        <span class="mono" style="color:var(--muted);font-size:11.5px">One PDF &middot; $24 CAD, paid once</span>
      </div>
    </div>
  </div>
</div></section>

<footer><div class="wrap">
  <div class="mono">FIRST PASS &middot; sixteen technical occupations, read 9 October 2026 &middot; <a href="../" style="border-bottom:0">the full page</a> &middot; <a href="../free-report/" style="border-bottom:0">the Screen Report</a></div>
  <div class="fnote">Employment insurance figures are reproduced from Statistics Canada's
    <em>Employment Insurance Statistics</em>, published under the <a href="{LIC_URL}">Statistics Canada Open Licence</a>;
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
        raise SystemExit("usage: build_layoffs_page.py <path-to-14100455.csv>")
    main(sys.argv[1])
