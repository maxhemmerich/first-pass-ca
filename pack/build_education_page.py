"""Build /tech-education/ — a fifteenth indexable page and the *qualification* side of the lane,
from a dataset no other page uses: Statistics Canada's 2021 Census of Population, table 98-10-0447,
*Occupation unit group by highest level of education, major field of study, age and gender*
(Statistics Canada Open Licence, CSV via the no-account WDS endpoint).

Why this cut. The salary pages say what a role pays (ESDC's *Wages* file); the two vacancy pages and
/job-vacancies-by-industry/ say what employers are trying to fill (Statistics Canada's Job Vacancy
and Wage Survey); /tech-job-projections/ says what the federal model expects (ESDC's COPS);
/tech-layoffs/ says how many have already left (Statistics Canada's EI table 14-10-0455). None of
them says what the people in these jobs *studied* — the qualification side of the same search.
This table does: for the same sixteen NOC 2021 unit groups this lane covers, it counts how much
education the people holding each occupation actually have and which fields of study they came
from. It is a different programme, a different portal resource and a different reference frame from
every source above — the decennial Census, not a monthly survey.

It prints the file's own numbers and nothing else:

  * the sixteen unit groups with a count of people in each 'highest certificate, diploma or degree'
    bucket, from 'no certificate' to 'bachelor's degree or higher';
  * the same sixteen unit groups with a count of people by the major field of study they came from
    (the fields these roles actually cluster in, named, plus the no-postsecondary group).

Hard rules, the same as the siblings: every number on the page is a string copied out of the named
CSV — nothing computed, converted, ranked, summed or averaged here, and **no percentage** (a rate
would be a figure the file does not print); the file's unit is a count of persons and is carried in
the column headings, so each cell is the file's own string; a cell the file leaves empty or
suppresses renders as a dash; no content or figure from the paid pack.

The 98-10-0447 CSV is 22 GB uncompressed, so it is not held in the repo. The rows this page reads
are the file's own lines, filtered once to GEO=Canada, Age=Total, Gender=Total, Statistics=Count:

  curl -s -o 98100447-eng.zip https://www150.statcan.gc.ca/n1/tbl/csv/98100447-eng.zip
  unzip -p 98100447-eng.zip 98100447.csv \
    | grep -E ',Total - Age,Total - Gender,Count,' > 98100447-totalcount.csv

Run:
  py -3.10 pack/build_education_page.py <98100447-totalcount.csv> [98100447-eng.zip]
"""
import csv, os, re, sys, hashlib, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE = {
    "publisher": "Statistics Canada",
    "survey": "Census of Population, 2021",
    "table_title": ("Occupation unit group by highest level of education, major field of study, "
                    "age and gender"),
    "product_id": "98-10-0447",
    "table_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810044701",
    "wds_url": "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/98100447/en",
    "resource_url": "https://www150.statcan.gc.ca/n1/tbl/csv/98100447-eng.zip",
    "resource_zip": "98100447-eng.zip",
    "resource_csv": "98100447.csv",
    "licence": "Statistics Canada Open Licence",
    "licence_url": "https://www.statcan.gc.ca/en/reference/licence",
    "read_date": "2026-10-09",
}
# sha256 of the downloaded archive (verified by sha256sum); overridden when the zip is passed in.
ARCHIVE_SHA = "580a4dd827810947d42c8ac5b9e10327d8880e7e1c91cfe0208b7983a479c887"

# The same sixteen NOC 2021 unit groups the salary, vacancy, projection and layoff pages cover.
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

TOTAL_CIP = "Total - Major field of study - Classification of Instructional Programs (CIP) 2021"
# The seven 'highest certificate, diploma or degree' members, in the file's column order.
EDU = [
    ("Total", "Total - Highest certificate, diploma or degree"),
    ("No certificate, diploma or degree", "No certificate, diploma or degree"),
    ("High (secondary) school", "High (secondary) school diploma or equivalency certificate"),
    ("Apprenticeship or trades", "Apprenticeship or trades certificate or diploma"),
    ("College, CEGEP", "College, CEGEP or other non-university certificate or diploma"),
    ("University below bachelor", "University certificate or diploma below bachelor level"),
    ("Bachelor's degree or higher", "Bachelor's degree or higher"),
]
# The fields-of-study columns printed (each is an exact CIP member name in the file).
CIPS = [
    "No postsecondary certificate, diploma or degree",
    "11. Computer and information sciences and support services",
    "27. Mathematics and statistics",
    "14. Engineering",
    "52. Business, management, marketing and related support services",
    "40. Physical sciences",
    "Other",
]
CODE_RE = re.compile(r"^\s*(\d{4,5})\b\s*(.*)$")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def cell(val, sym):
    """The file's own string, or a dash where the file is empty or suppresses the cell."""
    v = (val or "").strip()
    s = (sym or "").strip().lower()
    if not v or v == "F" or s == "x":
        return '<td class="n dim">&mdash;</td>'
    return '<td class="n">%s</td>' % _html.escape(v)


def main(src, zippath=None):
    codes = {c for c, _ in OCC}
    edu = {}          # code -> [ (val,sym) x7 ]   (CIP = Total)
    fld = {}          # (code, cip) -> (val,sym)   (education = Total)
    names = {}
    with open(src, "r", encoding="utf-8", newline="") as fh:
        for r in csv.reader(fh):
            if len(r) < 9 or r[1] != "Canada":
                continue
            m = CODE_RE.match(r[7])
            if not m or m.group(1) not in codes:
                continue
            code = m.group(1)
            names[code] = m.group(2).strip()
            cip = r[3]
            vals = r[9:]
            pairs = [(vals[2 * k] if 2 * k < len(vals) else "",
                      vals[2 * k + 1] if 2 * k + 1 < len(vals) else "") for k in range(7)]
            if cip == TOTAL_CIP:
                edu[code] = pairs
            if cip in CIPS:
                fld[(code, cip)] = pairs[0]        # education = Total column

    hash_ = sha256_file(zippath) if zippath and os.path.exists(zippath) else ARCHIVE_SHA

    rows1 = []
    for code, title in OCC:
        cells = "".join(cell(v, s) for v, s in edu.get(code, [("", "")] * 7))
        rows1.append('    <tr><td class="noc">%s</td><td class="occ">%s</td>%s</tr>'
                     % (_html.escape(code), _html.escape(title), cells))

    rows2 = []
    for code, title in OCC:
        cells = "".join(cell(*fld.get((code, c), ("", ""))) for c in CIPS)
        rows2.append('    <tr><td class="noc">%s</td><td class="occ">%s</td>%s</tr>'
                     % (_html.escape(code), _html.escape(title), cells))

    src_line = ("%s, <em>%s</em> (%s) \u2014 %s, %s. Read %s. SHA-256 of the archive "
                "<span class=\"mono\">%s</span>." % (
                    SOURCE["publisher"], SOURCE["table_title"], SOURCE["product_id"],
                    SOURCE["survey"], SOURCE["licence"], SOURCE["read_date"], hash_))

    html = PAGE.format(
        TITLE=TITLE, DESC=DESC, ROWS1="\n".join(rows1), ROWS2="\n".join(rows2),
        SOURCE_LINE=src_line, N=len(OCC),
        EHEAD="".join('<th class="n">%s</th>' % _html.escape(lbl) for lbl, _ in EDU),
        CHEAD="".join('<th class="n">%s</th>' % _html.escape(c) for c in CIPS),
        LIC_URL=SOURCE["licence_url"], TABLE_URL=SOURCE["table_url"],
        RES_URL=SOURCE["resource_url"], RES_ZIP=SOURCE["resource_zip"],
        RES_CSV=SOURCE["resource_csv"], HASH=hash_, PRODUCT=SOURCE["product_id"],
    )
    out = os.path.join(ROOT, "tech-education", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(html)
    print("wrote", out, len(html), "bytes")
    print("archive sha256:", hash_)
    print("education rows:", len(rows1), "| field-of-study cells:", len(rows2) * len(CIPS))


TITLE = "Tech education in Canada, counted \u2014 what each technical occupation studied"
DESC = ("How much education Canada's sixteen technical occupations actually hold and which fields "
        "of study they came from, counted by the 2021 Census of Population for each NOC 2021 unit "
        "group this site covers \u2014 Statistics Canada table 98-10-0447 (Statistics Canada Open "
        "Licence). Every figure carries its source and the date it was read.")

PAGE = """<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://maxhemmerich.github.io/first-pass-ca/tech-education/">
<meta property="og:type" content="article">
<meta property="og:site_name" content="First Pass">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="https://maxhemmerich.github.io/first-pass-ca/tech-education/">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="What Canada's tech workers studied, counted by the 2021 Census: the education behind sixteen technical occupations, from Statistics Canada.">
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
  "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-education/#article",
  "url": "https://maxhemmerich.github.io/first-pass-ca/tech-education/",
  "headline": "{TITLE}",
  "description": "{DESC}",
  "inLanguage": "en-CA",
  "datePublished": "2026-10-09",
  "dateModified": "2026-10-09",
  "author": {{"@type": "Organization", "name": "First Pass"}},
  "publisher": {{"@type": "Organization", "name": "First Pass", "url": "https://maxhemmerich.github.io/first-pass-ca/"}},
  "isPartOf": {{"@type": "WebSite", "@id": "https://maxhemmerich.github.io/first-pass-ca/#website", "url": "https://maxhemmerich.github.io/first-pass-ca/", "name": "First Pass"}},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-education/"}},
  "isBasedOn": {{"@type": "Dataset", "name": "Occupation unit group by highest level of education, major field of study, age and gender, table 98-10-0447", "creator": {{"@type": "GovernmentOrganization", "name": "Statistics Canada"}}, "license": "{LIC_URL}", "url": "{TABLE_URL}"}}
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
  <div class="kicker">Canada &middot; 2021 Census &middot; education by occupation</div>
  <h1>What the people in these jobs actually <span>studied</span></h1>
  <p class="lede">The rest of this site measures the market around a technical role &mdash; what it
    pays, how many are open, what the federal model expects, how many have already left. This page
    measures the people who hold the jobs themselves: how much education the sixteen technical
    NOC 2021 unit groups this lane covers actually have, and which fields of study they came from.
    It is the decennial Census of Population, counted by the occupation of the job held, and every
    figure on it is a count the file itself publishes &mdash; no percentage, no rate, nothing
    estimated here.</p>
  <div class="facts mono">
    <span>{N} occupation rows</span><span>counts, not rates</span><span>Statistics Canada</span><span>read 9 October 2026</span>
  </div>
</div></section>

<!-- 01 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">01</div><div>
    <h2>How much education the sixteen technical occupations hold</h2>
    <p class="lede" style="margin-top:12px">Each cell is a count of people, in Canada, whose job at
      the census was that occupation and whose highest certificate, diploma or degree fell in that
      column &mdash; from no certificate at all to a bachelor's degree or higher. Read across a row
      to see the shape of the field's education; the columns are the file's own education buckets,
      in the file's own order.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th>{EHEAD}</tr></thead>
    <tbody id="edu-level">
{ROWS1}
    </tbody>
  </table>
  </div>
  <p class="tcap">Source: {SOURCE_LINE} The unit is persons. A row's buckets sum to slightly less
    than its Total because the Census rounds each count independently to the nearest 5; nothing
    here is summed or adjusted by this page.</p>
</div></section>

<!-- 02 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">02</div><div>
    <h2>What the same sixteen occupations studied</h2>
    <p class="lede" style="margin-top:12px">The same people, counted instead by their major field
      of study. Seven columns are printed &mdash; the broad fields these roles actually cluster in,
      named exactly as the file names them, plus the group with no postsecondary credential at all.
      The file publishes sixty-three fields in all; the ones shown are the ones a reader weighing a
      technical job would look for first.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th>{CHEAD}</tr></thead>
    <tbody id="edu-field">
{ROWS2}
    </tbody>
  </table>
  </div>
  <p class="tcap">The rows do not add to the first table's Total: a person's field of study is
    recorded for those with a postsecondary credential, so the sixteen columns here are a different
    slice of the same population, not a breakdown of one number. Read down a column to compare
    occupations, and across a row to see where one occupation's people came from.</p>
</div></section>

<!-- 03 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">03</div><div>
    <h2>What this page counts, and what it does not</h2>
  </div></div>
  <ul class="limits">
    <li><b>One table, one census.</b> Everything above comes from a single Statistics Canada table,
      <span class="mono">{PRODUCT}</span>, from the 2021 Census of Population and published under the
      <a href="{LIC_URL}">Statistics Canada Open Licence</a>. The CSV read here
      (<span class="mono">{RES_CSV}</span>, unpacked from <span class="mono">{RES_ZIP}</span>) hashes to
      the archive digest <span class="mono">{HASH}</span>; <a href="{TABLE_URL}">the table page</a> and
      <a href="{RES_URL}">the download</a> are where a reader can confirm every figure.</li>
    <li><b>Counts, not rates.</b> The file prints counts of people; it does not print a share, and
      none is derived here. A reader who wants "the percentage with a degree" has to divide two
      counts this page prints side by side, because that is the only honest way to get one.</li>
    <li><b>A snapshot of one year.</b> The census is taken once a decade and the 2021 counts describe
      2021. Fields of study and hiring preferences move between censuses, so treat this as the last
      measured picture, not this year's.</li>
    <li><b>The occupation is the job held at the census.</b> A person is counted under the job they
      were in when the census was taken, so someone who has since moved between fields appears under
      the old one. This is where people were, not where they are.</li>
    <li><b>The columns are chosen, the figures are not.</b> Section 02 prints seven of the file's
      sixty-three fields of study, picked by name because they are the ones these roles cluster in;
      the choice of columns is this page's, but every count printed is the file's own. Nothing was
      ranked, averaged, rounded again or converted.</li>
    <li><b>The picture, and nothing borrowed from the pack.</b> These are counts of occupations in
      a country rather than of any employer or posting, and the page offers no guidance on what to do
      with them. Nothing in the paid document feeds a figure here, and no figure here is drawn from it.</li>
  </ul>
  <div class="pull">
    <p>This is the qualification side of the same search. What the roles <em>pay</em> is on the
      <a href="../tech-salaries/">salary page</a>; how many are <em>open</em> on the
      <a href="../tech-vacancies-by-occupation/">vacancy page</a>; what the model
      <em>expects</em> on the <a href="../tech-job-projections/">projection page</a>; and who has
      <em>left</em> on the <a href="../tech-layoffs/">layoffs page</a>. The whole of the figures
      above is one open-licensed census table, reproduced with the attribution the licence asks
      for.</p>
  </div>
</div></section>

<!-- 04 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">04</div><div>
    <h2>Where this sits</h2>
    <p class="lede" style="margin-top:12px">What the same roles pay, how many are open, what the
      screen asks and who holds them are the pages beside this one.</p>
  </div></div>
  <p style="color:#CFCBC1;font-size:14.5px;margin-bottom:22px">Paid wages by occupation:
    <a href="../tech-salaries/">tech salaries across Canada &rarr;</a> &middot; the same roles by urban
    region: <a href="../tech-salaries-by-city/">tech salaries by city &rarr;</a> &middot; the file's
    average column: <a href="../tech-average-pay/">average pay, by occupation &rarr;</a> &middot; what
    employers are trying to fill, by industry: <a href="../job-vacancies-by-industry/">job vacancies by industry &rarr;</a> &middot; the same demand by occupation: <a href="../tech-vacancies-by-occupation/">tech job vacancies by occupation &rarr;</a> &middot; the decade ahead: <a href="../tech-job-projections/">projected technical job openings to 2033 &rarr;</a> &middot; who has already left: <a href="../tech-layoffs/">tech layoffs in Canada, counted &rarr;</a></p>
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
      <p style="padding:14px 18px;margin:0;font-size:14.5px;color:#CFCBC1">Knowing what a field
        studies is not the same as getting through its screen. The pack carries the keyword map for
        the role, an answer shape for every screening question, three salary scripts and a Canadian
        negotiation section, in 21 pages.</p>
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
  <div class="fnote">Education and field-of-study figures are reproduced from Statistics Canada's
    <em>Census of Population, 2021</em>, published under the <a href="{LIC_URL}">Statistics Canada Open Licence</a>;
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
      replacement.textContent = "Get the pack — $24 CAD";
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
        raise SystemExit("usage: build_education_page.py <98100447-totalcount.csv> [98100447-eng.zip]")
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
