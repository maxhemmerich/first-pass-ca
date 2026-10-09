"""Build /tech-job-projections/ — a sixth citable Canadian reference, and the lane's first page from
neither the ESDC *Wages* file nor Statistics Canada's Job Vacancy and Wage Survey: ESDC's own
*Canadian Occupational Projection System* (COPS), 2024-2033 projections (Open Government Licence -
Canada, CSV via the no-account open.canada.ca download endpoint).

Why this cut. The three salary pages rest on ESDC's *Wages* file and answer what a role is *paid*.
/job-vacancies-by-industry/ and /tech-vacancies-by-occupation/ rest on Statistics Canada's Job
Vacancy and Wage Survey and answer what employers are *trying to hire right now*. This page answers
the forward question on a third dataset: how many openings the federal projection model expects over
the next decade for the same sixteen NOC 2021 technical unit groups, how many seekers it expects to
meet them, and the labour-market condition ESDC itself assigns. It prints the file's own numbers and
strings and nothing else:

  * the sixteen unit groups: employment in 2023, the projected components of job openings
    (expansion demand, retirements, other replacement) and their total, 2024-2033;
  * the same sixteen: the projected components of job seekers (school leavers, immigration, other
    seekers) and their total, 2024-2033, plus ESDC's own recent and projected labour-market condition.

Hard rules, the same as the siblings: every number and condition on the page is a string copied out of
the named CSV — nothing computed, converted, ranked or averaged here; the file's units (a count of
jobs or people, a text condition) are carried in the column headings, so each cell is the file's own
string; a cell the file leaves empty renders as a dash; no content or figure from the paid pack.

Run:
  py -3.10 pack/build_projected_openings_page.py <path-to-summary_sommaire_2024_2033_noc2021.csv>
"""
import csv, os, sys, hashlib, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE = {
    "publisher": "Employment and Social Development Canada",
    "system": "Canadian Occupational Projection System (COPS)",
    "dataset_title": "Canadian Occupational Projection System (COPS) \u2014 2024 to 2033 projections",
    "resource_title": "Summary of the Components (Job Openings and Job Seekers), 2024-2033 by Occupation",
    "dataset_url": "https://open.canada.ca/data/en/dataset/e80851b8-de68-43bd-a85c-c72e1b3a3890",
    "resource_url": ("https://open.canada.ca/data/dataset/e80851b8-de68-43bd-a85c-c72e1b3a3890/"
                     "resource/7c4767a5-f807-441d-9776-a0074b5870a0/download/"
                     "summary_sommaire_2024_2033_noc2021.csv"),
    "resource_file": "summary_sommaire_2024_2033_noc2021.csv",
    "licence": "Open Government Licence \u2013 Canada",
    "licence_url": "https://open.canada.ca/en/open-government-licence-canada",
    "read_date": "2026-10-09",
}

# The same sixteen NOC 2021 unit groups the salary pages cover and the occupation vacancy page prints.
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

# column names exactly as the file spells them
C_EMP = "Employment_emploi_2023"
C_GROWTH = "Employment_Growth_croissance_emploi"
C_RET = "Retirements_retraites"
C_OTHER_OPEN = "Other_Replacement_autre_remplacement"
C_TOTAL_OPEN = "Total_Job_Openings_Perspective_d'emploi"
C_SCHOOL = "School_Leavers_Sortants_scolaires"
C_IMM = "Immigration"
C_OTHER_SEEK = "Other_Seekers_autres_chercheurs"
C_TOTAL_SEEK = "Job_Seekers_Chercheurs_emploi"
C_RECENT = "Recent_Labour_Market_Conditions"
C_FUTURE = "Future_Labour_Market_Conditions"

OPEN_COLS = [C_EMP, C_GROWTH, C_RET, C_OTHER_OPEN, C_TOTAL_OPEN]
SEEK_COLS = [C_SCHOOL, C_IMM, C_OTHER_SEEK, C_TOTAL_SEEK]


def load(path):
    rows = {}
    with open(path, "r", encoding="cp1252", newline="") as fh:
        for r in csv.DictReader(fh):
            rows[r["Code"]] = r
    return rows


def cell(v):
    v = (v or "").strip()
    if not v:
        return '<td class="n dim">&mdash;</td>'
    return '<td class="n">%s</td>' % _html.escape(v)


def cond(v):
    v = (v or "").strip()
    if not v:
        return '<td class="dim">&mdash;</td>'
    cls = "cond"
    if "Shortage" in v:
        cls = "cond short"
    elif "Surplus" in v:
        cls = "cond surplus"
    return '<td class="%s">%s</td>' % (cls, _html.escape(v))


def main(path):
    rows = load(path)
    HASH = hashlib.sha256(open(path, "rb").read()).hexdigest()

    # 01 — job openings, 2024-2033, occupation by occupation
    rows1 = []
    for code, title in OCC:
        r = rows.get(code, {})
        cells = "".join(cell(r.get(c)) for c in OPEN_COLS)
        rows1.append(
            '    <tr><td class="noc">%s</td><td class="occ">%s</td>%s</tr>'
            % (_html.escape(code), _html.escape(title), cells)
        )

    # 02 — job seekers, 2024-2033, and the condition ESDC assigns
    rows2 = []
    for code, title in OCC:
        r = rows.get(code, {})
        cells = "".join(cell(r.get(c)) for c in SEEK_COLS)
        rows2.append(
            '    <tr><td class="noc">%s</td><td class="occ">%s</td>%s%s%s</tr>'
            % (_html.escape(code), _html.escape(title), cells,
               cond(r.get(C_RECENT)), cond(r.get(C_FUTURE)))
        )

    src_line = ("%s, <em>%s</em> \u2014 %s, %s \u2014 %s. Read %s. SHA-256 "
                "<span class=\"mono\">%s</span>." % (
                    SOURCE["publisher"], SOURCE["system"], SOURCE["resource_title"],
                    SOURCE["licence"], SOURCE["resource_file"], SOURCE["read_date"], HASH))

    html = PAGE.format(
        TITLE=TITLE, DESC=DESC, ROWS1="\n".join(rows1), ROWS2="\n".join(rows2),
        SOURCE_LINE=src_line, N=len(OCC),
        LIC_URL=SOURCE["licence_url"], DATASET_URL=SOURCE["dataset_url"],
        RES_URL=SOURCE["resource_url"], RES_FILE=SOURCE["resource_file"],
        HASH=HASH, SYSTEM=SOURCE["system"],
    )
    out = os.path.join(ROOT, "tech-job-projections", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(html)
    print("wrote", out, len(html), "bytes")
    print("csv sha256:", HASH)
    print("occupation rows:", len(OCC))


TITLE = "Projected Canadian tech job openings to 2033 \u2014 ESDC's COPS, occupation by occupation"
DESC = ("The job openings and job seekers the federal projection model expects for the sixteen "
        "technical NOC 2021 unit groups this site covers, 2024-2033, with the labour-market condition "
        "ESDC assigns to each. From the Canadian Occupational Projection System (Open Government "
        "Licence \u2013 Canada). Every figure carries its source and the date it was read.")

PAGE = """<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://maxhemmerich.github.io/first-pass-ca/tech-job-projections/">
<meta property="og:type" content="article">
<meta property="og:site_name" content="First Pass">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="https://maxhemmerich.github.io/first-pass-ca/tech-job-projections/">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="How many openings Canada's projection model expects for software, data, security and IT roles to 2033, and how many people it expects to compete for them.">
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
  td.cond{{font-family:var(--mono);font-size:12.5px;color:#CFCBC1}}
  td.cond.short{{color:var(--green)}}
  td.cond.surplus{{color:var(--red)}}
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
  "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-job-projections/#article",
  "url": "https://maxhemmerich.github.io/first-pass-ca/tech-job-projections/",
  "headline": "{TITLE}",
  "description": "{DESC}",
  "inLanguage": "en-CA",
  "datePublished": "2026-10-09",
  "dateModified": "2026-10-09",
  "author": {{"@type": "Organization", "name": "First Pass"}},
  "publisher": {{"@type": "Organization", "name": "First Pass", "url": "https://maxhemmerich.github.io/first-pass-ca/"}},
  "isPartOf": {{"@type": "WebSite", "@id": "https://maxhemmerich.github.io/first-pass-ca/#website", "url": "https://maxhemmerich.github.io/first-pass-ca/", "name": "First Pass"}},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://maxhemmerich.github.io/first-pass-ca/tech-job-projections/"}},
  "isBasedOn": {{"@type": "Dataset", "name": "Canadian Occupational Projection System (COPS) - 2024 to 2033 projections", "creator": {{"@type": "GovernmentOrganization", "name": "Employment and Social Development Canada"}}, "license": "{LIC_URL}", "url": "{DATASET_URL}"}}
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
  <div class="kicker">Canada &middot; COPS projections 2024&ndash;2033 &middot; by occupation</div>
  <h1>Canada's technical job openings, <span>projected to 2033</span></h1>
  <p class="lede">The salary pages ask what a technical role <em>pays</em>; the vacancy pages ask how
    many are <em>open today</em>. This one asks a third question: how many openings the federal
    projection model expects over the next decade, and how many people it expects to compete for
    them. It reads the sixteen technical NOC 2021 unit groups this site already covers out of ESDC's
    <b>Canadian Occupational Projection System</b> &mdash; a projection model on its own dataset, not
    the wage file and not the vacancy survey &mdash; with the source and the read date on every
    figure.</p>
  <div class="facts mono">
    <span>{N} occupation rows</span><span>2024&ndash;2033, national</span><span>ESDC COPS</span><span>read 9 October 2026</span>
  </div>
</div></section>

<!-- 01 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">01</div><div>
    <h2>The openings, occupation by occupation</h2>
    <p class="lede" style="margin-top:12px">Every column is a number of jobs, summed by ESDC over the
      ten projection years 2024&ndash;2033 for each of the sixteen technical unit groups. The three
      components add to the total on the right: expansion demand is job creation, retirements and
      other replacement are the posts vacated and refilled.</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th><th class="n">Employment 2023</th>
      <th class="n">Expansion demand</th><th class="n">Retirements</th>
      <th class="n">Other replacement</th><th class="n">Total openings</th></tr></thead>
    <tbody id="proj-openings">
{ROWS1}
    </tbody>
  </table>
  </div>
  <p class="tcap">Source: {SOURCE_LINE} These are ESDC's modelled projections for 2024&ndash;2033, not
    counts of postings; a total is the sum of its own three components and of nothing else. Columns are
    the file's own; the units are jobs.</p>
</div></section>

<!-- 02 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">02</div><div>
    <h2>The seekers, and the outlook ESDC assigns</h2>
    <p class="lede" style="margin-top:12px">The same sixteen unit groups, with the projected number of
      people expected to enter them over 2024&ndash;2033 and ESDC's own labour-market condition for
      each &mdash; the recent assessment (2021&ndash;2023) beside the projected one (2024&ndash;2033).</p>
  </div></div>
  <div class="scroll">
  <table>
    <thead><tr><th>NOC</th><th>Occupation</th><th class="n">School leavers</th>
      <th class="n">Immigration</th><th class="n">Other seekers</th><th class="n">Total seekers</th>
      <th>Recent 2021&ndash;23</th><th>Projected 2024&ndash;33</th></tr></thead>
    <tbody id="proj-seekers">
{ROWS2}
    </tbody>
  </table>
  </div>
  <p class="tcap">The three seeker components add to the total; <span class="mono">Other seekers</span>
    is a net figure (occupational mobility, re-entries, working students) and can be negative, exactly
    as the file prints it. <span class="mono">Balance</span>, <span class="mono">Shortage</span> and
    <span class="mono">Surplus</span> are ESDC's own words for its assessment, not this site's; a
    shortage is projected labour demand outpacing supply, a surplus the reverse.</p>
</div></section>

<!-- 03 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">03</div><div>
    <h2>Scope, source, and what it is not</h2>
  </div></div>
  <ul class="limits">
    <li><b>One dataset, quoted.</b> Every cell above is a string out of a single ESDC dataset,
      <span class="mono">{SYSTEM}</span>, 2024&ndash;2033 projections, published under the
      <a href="{LIC_URL}">Open Government Licence &ndash; Canada</a>. The CSV read here
      (<span class="mono">{RES_FILE}</span>) hashes to <span class="mono">{HASH}</span>;
      <a href="{DATASET_URL}">the dataset page</a> and <a href="{RES_URL}">the download</a> are where a
      reader can confirm it.</li>
    <li><b>Sixteen codes, shown and cited.</b> The rows are the NOC unit groups this site already
      prices, chosen to line up with the salary pages and printed with their codes so the pick is
      checkable. The file carries hundreds of occupations; this is one slice of them.</li>
    <li><b>A projection, not a count.</b> These figures come from a model that projects flows of job
      openings and job seekers ten years forward from assumptions about growth, retirement and
      immigration. They are not observed openings and not a promise; the vacancy pages print what
      employers were advertising on a real date.</li>
    <li><b>Openings are not adverts.</b> An opening here is a post the model expects to be created or
      vacated over the decade, including replacement for retirements and emigration. It is not the
      same as a vacancy an employer is trying to fill this quarter.</li>
    <li><b>Conditions are ESDC's.</b> The <span class="mono">Shortage</span>,
      <span class="mono">Balance</span> and <span class="mono">Surplus</span> labels are the model's own
      assessment of labour-market tightness for the occupation, carried verbatim; they are not advice
      and not this site's judgement.</li>
    <li><b>A trade and a decade, not a job ad.</b> Nothing here names an employer or a single
      opening, and none of it is a promise of work. Nothing on this page is lifted from the paid
      pack.</li>
  </ul>
  <div class="pull">
    <p>The same sixteen occupations, priced today, are on
      <a href="../tech-salaries/">tech salaries across Canada</a> and
      <a href="../tech-average-pay/">average pay, by occupation</a>; what is <em>open</em> right now is
      on <a href="../tech-vacancies-by-occupation/">job vacancies by occupation</a> and
      <a href="../job-vacancies-by-industry/">job vacancies by industry</a>. This page is the decade
      ahead, from a different dataset again.</p>
  </div>
</div></section>

<!-- 04 -->
<section><div class="wrap">
  <div class="sec-head"><div class="sec-num">04</div><div>
    <h2>Where this sits</h2>
    <p class="lede" style="margin-top:12px">This page is the forward look, by occupation. What the same
      roles pay, and what is open now, are the other three cuts; what employers asked and how to answer
      is the free report and the pack.</p>
  </div></div>
  <p style="color:#CFCBC1;font-size:14.5px;margin-bottom:22px">Paid wages by occupation:
    <a href="../tech-salaries/">tech salaries across Canada &rarr;</a> &middot; the same roles by urban
    region: <a href="../tech-salaries-by-city/">tech salaries by city &rarr;</a> &middot; the file's
    average column: <a href="../tech-average-pay/">average pay, by occupation &rarr;</a> &middot; open
    now, by occupation: <a href="../tech-vacancies-by-occupation/">job vacancies by occupation &rarr;</a></p>
  <div class="two">
    <div class="free">
      <div class="kicker">Free &middot; no email</div>
      <h3 style="margin-top:10px">The Screen Report</h3>
      <p style="color:#CFCBC1;font-size:14.5px;margin-top:10px">The measured other half of a search:
        the screening questions the postings asked, and every salary band they printed.</p>
      <a class="btn ghost" href="../free-report/">Read the Screen Report &rarr;</a>
    </div>
    <div class="paid">
      <div class="paid-head"><h3>The First Pass pack</h3><span class="p mono">$24 CAD</span></div>
      <p style="padding:14px 18px;margin:0;font-size:14.5px;color:#CFCBC1">The pack turns these
        figures into a working search: keywords per role, a shape for each screening question, three
        salary scripts and a Canadian negotiation section, across 21 pages.</p>
      <p style="padding:12px 18px;margin:0;border-top:1px solid var(--rule);font-size:13.5px"><a href="../whats-in-the-pack/">See what is inside, section by section &rarr;</a></p>
      <div class="paid-foot">
        <a class="btn sm" data-buy href="https://maxhemmerich.gumroad.com/l/yolqdo" target="_blank" rel="noopener">Get the pack</a>
        <span class="mono" style="color:var(--muted);font-size:11.5px">One PDF &middot; $24 CAD, paid once</span>
      </div>
    </div>
  </div>
</div></section>

<footer><div class="wrap">
  <div class="mono">FIRST PASS &middot; sixteen technical occupations, projected 2024&ndash;2033, read 9 October 2026 &middot; <a href="../" style="border-bottom:0">the full page</a> &middot; <a href="../free-report/" style="border-bottom:0">the Screen Report</a></div>
  <div class="fnote">Projection figures are reproduced from Employment and Social Development Canada's
    <em>Canadian Occupational Projection System</em>, which is published under the
    <a href="{LIC_URL}">Open Government Licence &ndash; Canada</a>; this page carries that information
    with attribution and is neither endorsed by nor affiliated with the Government of Canada.
    Questions, refunds or corrections: <a href="mailto:maxhemmerich@gmail.com">maxhemmerich@gmail.com</a>.
    No tracking of individuals. No cookies. No personal data. Page views are counted in aggregate
    &mdash; one number per page, no identifier.</div>
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
        raise SystemExit("usage: build_projected_openings_page.py <path-to-summary.csv>")
    main(sys.argv[1])
