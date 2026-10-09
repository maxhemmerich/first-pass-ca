"""Build /tech-salaries-by-city/ — the city-level cut of the SAME single source the /tech-salaries/ page
uses: Employment and Social Development Canada's open-data "Wages" file (Open Government Licence - Canada).

Where /tech-salaries/ prints the national row and the province row for each occupation, this page prints
the file's *economic-region* rows only — the rows whose ER_Name is neither "Canada" nor a province name.
The two pages therefore share a source but not a single row of it.

Selection is derived from the file, not chosen by taste: the table carries every economic region for which
the file publishes a median for at least 15 of the 16 occupations. That rule lands on the country's large
urban labour markets (Toronto, Ottawa, Montreal, the Lower Mainland, Calgary, Edmonton, ...).

Hard rules: every number on the page is a string copied out of the named CSV — nothing computed,
converted or averaged; a cell the file leaves empty renders as a dash; no content or figure from the paid
pack.

Run:
  py -3.10 pack/build_city_salary_page.py <path-to-wages-csv>
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

# The same sixteen NOC 2021 unit groups as /tech-salaries/: (code, full title, short table label)
OCC = [
    ("21232", "Software developers and programmers", "Software devs"),
    ("21231", "Software engineers and designers", "Software eng"),
    ("21230", "Computer systems developers and programmers", "Systems devs"),
    ("21211", "Data scientists", "Data sci"),
    ("21223", "Database analysts and data administrators", "DB analysts"),
    ("21222", "Information systems specialists", "IS specialists"),
    ("21221", "Business systems specialists", "Business sys"),
    ("21220", "Cybersecurity specialists", "Cyber sec"),
    ("21311", "Computer engineers (except software engineers and designers)", "Computer eng"),
    ("21234", "Web developers and programmers", "Web devs"),
    ("21233", "Web designers", "Web design"),
    ("21210", "Mathematicians, statisticians and actuaries", "Math/stat"),
    ("22220", "Computer network and web technicians", "Network tech"),
    ("22222", "Information systems testing technicians", "Test tech"),
    ("22221", "User support technicians", "User support"),
    ("20012", "Computer and information systems managers", "IS managers"),
]

# West to east; only provinces that appear in the selection are rendered.
PROV = [
    ("BC", "British Columbia"), ("AB", "Alberta"), ("SK", "Saskatchewan"), ("MB", "Manitoba"),
    ("ON", "Ontario"), ("QC", "Quebec"), ("NB", "New Brunswick"), ("NS", "Nova Scotia"),
    ("PEI", "Prince Edward Island"), ("NL", "Newfoundland and Labrador"),
]
PROV_FULL = dict(PROV)
PROVNAMES = set(PROV_FULL.values()) | {"Canada"}

MIN_OCC = 15  # "at least 15 of the 16 occupations" — the file-derived selection rule

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
    """Economic-region rows only: ER_Name is neither 'Canada' nor a province name."""
    by_reg = collections.defaultdict(dict)   # (prov, ercode) -> {noc: row}
    names = {}
    for r in rows:
        c = code_of(r)
        if c not in {o[0] for o in OCC}:
            continue
        if r["ER_Name"].strip() in PROVNAMES:
            continue
        k = (r["prov"].strip(), r["ER_Code_Code_RE"].strip())
        by_reg[k][c] = r
        names[k] = r["ER_Name"].strip()

    # selection: regions with a published median for at least MIN_OCC occupations
    selected = []
    for k, cells in by_reg.items():
        have = sum(1 for c, r in cells.items() if r["Median_Wage_Salaire_Median"].strip())
        if k[0] in PROV_FULL and have >= MIN_OCC:
            selected.append((k, have))
    order = {p: i for i, (p, _f) in enumerate(PROV)}
    selected.sort(key=lambda x: (order[x[0][0]], x[0][1]))
    return selected, by_reg, names


def money(v, mark):
    v = (v or "").strip()
    return "&mdash;" if not v else "$%s%s" % (_html.escape(v), mark)


def build(rows):
    selected, by_reg, names = collect(rows)

    head = "".join(
        '<th class="n"><span class="hc">%s</span>%s</th>' % (code, short) for code, _f, short in OCC
    )
    body = []
    dash_cells = []
    srcs = collections.Counter()
    marks = collections.Counter()
    for (prov, erc), have in selected:
        cells = []
        for code, _full, _short in OCC:
            r = by_reg[(prov, erc)].get(code)
            if r is None or not r["Median_Wage_Salaire_Median"].strip():
                cells.append('<td class="n dim">&mdash;</td>')
                dash_cells.append((prov, erc, code))
                continue
            s = r["Data_Source_E"].strip()
            srcs[s] += 1
            mk = SRC_MARK.get(s, "?")
            marks[mk] += 1
            cells.append('<td class="n">%s</td>' % money(r["Median_Wage_Salaire_Median"], mk))
        body.append(
            '    <tr><td class="prov">%s</td><td class="reg">%s</td>%s</tr>'
            % (prov, names[(prov, erc)], "".join(cells))
        )

    reg_list = "".join(
        '<li><span class="mono pv">%s</span> <b>%s</b> <span class="mono rc">%s</span>'
        '<span class="hav">%d of %d</span></li>'
        % (prov, names[(prov, erc)], erc, have, len(OCC))
        for (prov, erc), have in selected
    )
    occ_list = "".join(
        '<li><span class="mono">%s</span> &middot; %s</li>' % (code, _html.escape(full))
        for code, full, _short in OCC
    )

    src_line = ("%s, <em>%s</em>, %s \u2014 %s. Read %s. sha256 of the file: "
                "<span class=\"mono\">%s</span>." % (
                    SOURCE["publisher"], SOURCE["dataset_title"], SOURCE["resource_name"],
                    SOURCE["licence"], SOURCE["read_date"], HASH))

    html = PAGE.format(
        TITLE=TITLE, DESC=DESC, HEAD=head, BODY="\n".join(body),
        REG_LIST=reg_list, OCC_LIST=occ_list, NREG=len(selected), NOCC=len(OCC),
        SOURCE_LINE=src_line, DATASET_URL=SOURCE["dataset_url"], RES_URL=SOURCE["resource_url"],
        LIC_URL=SOURCE["licence_url"], RES_FILE=SOURCE["resource_file"],
        RES_PUB=SOURCE["resource_published"], HASH=HASH,
    )
    return html, selected, dash_cells, srcs, marks


TITLE = "Canadian tech pay by city \u2014 16 technical roles across 20 economic regions"
DESC = ("Median hourly pay for 16 Canadian software, data, IT and computer-engineering occupations in 20 "
        "urban economic regions \u2014 Toronto, Ottawa, Montr\u00e9al, the Lower Mainland, Calgary and more \u2014 "
        "taken from Employment and Social Development Canada's published wage file "
        "(Open Government Licence \u2013 Canada). Every figure carries its source and the date it was read.")

PAGE = """<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://maxhemmerich.github.io/first-pass-ca/tech-salaries-by-city/">
<meta property="og:type" content="article">
<meta property="og:site_name" content="First Pass">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="https://maxhemmerich.github.io/first-pass-ca/tech-salaries-by-city/">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="16 Canadian technical occupations, median per hour, in 20 urban economic regions. Every figure from the government's own wage file.">
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
  table{{width:100%;border-collapse:collapse;font-size:13.5px}}
  th,td{{padding:9px 10px;border-bottom:1px solid var(--rule2);text-align:left;white-space:nowrap}}
  thead th{{font-family:var(--mono);font-size:11px;letter-spacing:.06em;color:var(--muted);
    border-bottom:1px solid var(--rule);font-weight:600;vertical-align:bottom}}
  thead th .hc{{display:block;font-size:10px;color:var(--muted);opacity:.75}}
  td.n,th.n{{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right}}
  td.dim{{color:#4A4A50}}
  td.prov{{font-family:var(--mono);font-size:11.5px;color:var(--muted)}}
  td.reg{{color:#CFCBC1;font-size:13px}}
  .tcap{{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin:14px 0 0;max-width:84ch;white-space:normal}}

  .limits{{list-style:none;margin:0;padding:0}}
  .limits li{{padding:10px 0;border-bottom:1px solid var(--rule2);color:#CFCBC1;font-size:14.5px}}
  .limits li b{{color:var(--ink);font-weight:400}}

  .regs{{list-style:none;margin:0;padding:0;columns:2;column-gap:34px}}
  @media (max-width:720px){{.regs{{columns:1}}}}
  .regs li{{padding:8px 0;border-bottom:1px solid var(--rule2);color:#CFCBC1;font-size:14px;
    break-inside:avoid}}
  .regs .pv{{color:var(--accent);font-size:11.5px;margin-right:6px}}
  .regs b{{color:var(--ink);font-weight:400}}
  .regs .rc{{color:var(--muted);font-size:11.5px;margin-left:6px}}
  .regs .hav{{float:right;color:var(--muted);font-size:11.5px;font-family:var(--mono)}}
  .occ{{list-style:none;margin:0;padding:0;columns:2;column-gap:34px}}
  @media (max-width:720px){{.occ{{columns:1}}}}
  .occ li{{padding:6px 0;color:#CFCBC1;font-size:13.5px;break-inside:avoid}}
  .occ .mono{{color:var(--muted);font-size:12px;margin-right:6px}}

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
  "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-salaries-by-city/#article",
  "url": "https://maxhemmerich.github.io/first-pass-ca/tech-salaries-by-city/",
  "headline": "{TITLE}",
  "description": "{DESC}",
  "inLanguage": "en-CA",
  "datePublished": "2026-10-09",
  "dateModified": "2026-10-09",
  "author": {{"@type": "Organization", "name": "First Pass"}},
  "publisher": {{"@type": "Organization", "name": "First Pass", "url": "https://maxhemmerich.github.io/first-pass-ca/"}},
  "isPartOf": {{"@type": "WebSite", "@id": "https://maxhemmerich.github.io/first-pass-ca/#website", "url": "https://maxhemmerich.github.io/first-pass-ca/", "name": "First Pass"}},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-salaries-by-city/"}},
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
  <div class="kicker">Canada &middot; official wage data &middot; 20 urban regions</div>
  <h1>The same technical roles, priced <span>city by city</span></h1>
  <p class="lede">The federal wage file publishes a row for every economic region in the country, not just
    for each province. This page takes <b>{NOCC}</b> software, data, IT and computer-engineering occupations
    and prints the file's own median pay per hour for each of the <b>{NREG}</b> urban labour markets where
    the file carries a figure for almost all of them. Nothing here is estimated or converted: every number
    is the file's, and it is the region's own row, not the province's.</p>
  <div class="facts mono">
    <span>{NREG} urban regions</span><span>{NOCC} occupations</span><span>ESDC open data</span><span>read 9 October 2026</span>
  </div>
</div></section>

<!-- 01 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">01</div><div>
    <h2>Median pay per hour, region by region</h2>
    <p class="lede" style="margin-top:12px">Canadian dollars per hour, exactly as the file publishes them.
      One row per economic region; one column per occupation. A dash is a cell the file leaves empty &mdash;
      no figure is published for that occupation in that region, and none is filled in here.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>Prov</th><th>Economic region</th>{HEAD}</tr></thead>
    <tbody>
{BODY}
    </tbody>
  </table>
  </div>
  <p class="tcap">Every figure above is a cell of the 2025 <em>Wages</em> file published by Employment and
    Social Development Canada under the Open Government Licence &ndash; Canada; the file was read on
    9 October 2026 and its sha256 is <span class="mono">{HASH}</span>. The file reports pay per hour and by
    the hour it is kept. Cell marks name the survey behind that particular cell: plain is the Labour Force
    Survey, &dagger; a small-area estimate, &ddagger; an Employment Insurance survey figure, &sect; the 2021
    Census. NOC 2021 codes.</p>
</div></section>

<!-- 02 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">02</div><div>
    <h2>Why these twenty regions</h2>
    <p class="lede" style="margin-top:12px">The file carries 75 economic regions. Most publish a figure for
      only a handful of these occupations, and many publish none at all, so a table of all 75 would be mostly
      dashes. This page instead keeps every region where the file publishes a median for at least 15 of the
      16 occupations &mdash; a rule taken from the file's own coverage rather than from a judgement about
      which cities matter. It lands on the country's large urban labour markets.</p>
  </div></div>
  <ul class="regs">
{REG_LIST}
  </ul>
  <p class="tcap" style="margin-top:18px">The file names regions after Statistics Canada's economic geography
    rather than after cities: the Vancouver area is carried as <b>Lower Mainland</b>, the region holding
    Victoria as <b>Vancouver Island and Coast</b>, the Quebec City area as <b>Capitale-Nationale</b>, and the
    Gatineau side of the Ottawa river as <b>Outaouais</b>. Halifax, Windsor, London and Regina are named
    directly. Region names above are printed exactly as the file spells them, including its double-hyphen
    separators.</p>
</div></section>

<!-- 03 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">03</div><div>
    <h2>Reading the table honestly</h2>
  </div></div>
  <ul class="limits">
    <li><b>The file.</b> One document stands behind this page and nothing else: Employment and Social
      Development Canada's open-data <em>Wages</em> release for 2025, published 19 November 2025 under the
      <a href="{LIC_URL}">Open Government Licence &ndash; Canada</a>. Its CSV
      (<span class="mono">{RES_FILE}</span>) was read on 9 October 2026 and hashes to
      <span class="mono">{HASH}</span>; <a href="{DATASET_URL}">the dataset page</a> and
      <a href="{RES_URL}">the download</a> are the links to check it against.</li>
    <li><b>Paid, not offered.</b> The file's own note is that these are wages <em>paid</em>, not wages
      advertised, so a median here is the middle of what workers in that region were actually paid. Each
      cell is the file's number moved into this table without alteration.</li>
    <li><b>A region is not a city.</b> An economic region is a Statistics Canada boundary, and several of
      them cover a city together with its surrounding counties &mdash; Lower Mainland and
      Hamilton&ndash;Niagara Peninsula are wider than the metropolitan area at their centre. A figure
      describes the region's own rows, so a given employer, seniority level or office can sit above or below
      it.</li>
    <li><b>Periods differ by cell.</b> Not every cell was measured in the same year, so a mark in the table
      is part of the number: the small-area estimates rest on 2024, the single marked Census cell on 2021,
      and the unmarked cells on the Labour Force Survey's 2023&ndash;2024 window.</li>
    <li><b>Hourly stays hourly.</b> The file reports these occupations by the hour and this page keeps them
      that way. Turning an hourly rate into a yearly salary would need a paid-hours figure the file does not
      publish, so no annual figure is offered.</li>
    <li><b>Not advice, not a posting.</b> This is a reference table, not a vacancy, a recruiter or guidance,
      and it is built from government data rather than from this site's own gathered sample. It carries
      nothing from the paid pack.</li>
  </ul>
  <h3 style="margin-top:34px">The sixteen occupations</h3>
  <ul class="occ" style="margin-top:14px">
{OCC_LIST}
  </ul>
</div></section>

<!-- 04 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">04</div><div>
    <h2>Where this sits</h2>
    <p class="lede" style="margin-top:12px">Read this page for <em>place</em>. For the same roles measured
      across the whole country and in each province, the salary page is the companion; for what employers
      actually asked and how to answer it, the free report and the pack are the other half.</p>
  </div></div>
  <p style="color:#CFCBC1;font-size:14.5px;margin-bottom:22px">The same sixteen roles, nationally and by
    province: <a href="../tech-salaries/">tech salaries across Canada &rarr;</a></p>
  <div class="two">
    <div class="free">
      <div class="kicker">Free to read &middot; no email</div>
      <h3 style="margin-top:10px">The Screen Report</h3>
      <p style="color:#CFCBC1;font-size:14.5px;margin-top:10px">What 141 postings asked: the ranked screening
        questions, the twenty salary wordings, and the bands employers printed in the ads.</p>
      <a class="btn ghost" href="../free-report/">Open the free report &rarr;</a>
    </div>
    <div class="paid">
      <div class="paid-head"><h3>The First Pass pack</h3><span class="p mono">$24 CAD</span></div>
      <p style="padding:14px 18px;margin:0;font-size:14.5px;color:#CFCBC1">The 21-page working half: a keyword
        map per role, an answer shape for each screening question, three salary scripts and a negotiation
        section written for Canada.</p>
      <p style="padding:12px 18px;margin:0;border-top:1px solid var(--rule);font-size:13.5px"><a href="../whats-in-the-pack/">Its eight sections, with page numbers &rarr;</a></p>
      <div class="paid-foot">
        <a class="btn sm" data-buy href="https://maxhemmerich.gumroad.com/l/yolqdo" target="_blank" rel="noopener">Get the pack</a>
        <span class="mono" style="color:var(--muted);font-size:11.5px">One PDF &middot; $24 CAD, paid once</span>
      </div>
    </div>
  </div>
</div></section>

<footer><div class="wrap">
  <div class="mono">FIRST PASS &middot; Canada &middot; region pay read 9 October 2026 &middot; <a href="../" style="border-bottom:0">the full page</a> &middot; <a href="../free-report/" style="border-bottom:0">the Screen Report</a></div>
  <div class="fnote">Median pay figures are reproduced from Employment and Social Development Canada's
    <em>Wages</em> open data, which is published under the <a href="{LIC_URL}">Open Government Licence
    &ndash; Canada</a>; this page carries that information with attribution and is neither endorsed by nor
    affiliated with ESDC. Questions, refunds or corrections:
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
    path = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ALPHA_WAGES_CSV")
    if not path:
        raise SystemExit("usage: build_city_salary_page.py <wages.csv>")
    HASH = hashlib.sha256(open(path, "rb").read()).hexdigest()
    rows = load(path)
    html, selected, dash_cells, srcs, marks = build(rows)
    out = os.path.join(ROOT, "tech-salaries-by-city", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(html)
    print("wrote", out, len(html), "bytes")
    print("source rows in file:", len(rows))
    print("regions selected (>= %d of %d):" % (MIN_OCC, len(OCC)), len(selected))
    for (prov, erc), have in selected:
        print("   %-4s %-7s %d/16" % (prov, erc, have))
    print("cells with a published median:", sum(1 for _ in [0]) and (len(selected) * len(OCC) - len(dash_cells)))
    print("dash cells:", len(dash_cells), dash_cells)
    print("source mix:", dict(srcs))
    print("mark mix:", dict(marks))
