"""ALPHA page counter — the one build path that writes the Abacus hit counter into every
published page and regenerates the /stats/ reader from the same key map.

Service: Abacus (https://abacus.jasoncameron.dev) — free, no account, no API key, CORS enabled.
  GET /hit/<ns>/<key>  increments, returns {"value": N}
  GET /get/<ns>/<key>  reads, returns {"value": N} or 404 {"error":"Key not found"}
Keys cannot contain "/" (the service 301-redirects those), so each page carries one flat key.
No cookie is set by the service and no per-visitor data is stored — only an integer per key.

Run:
  py -3.10 pack/counter.py inject   # write the snippet into every page (idempotent)
  py -3.10 pack/counter.py stats    # regenerate stats/index.html (embeds a live-read snapshot)
  py -3.10 pack/counter.py read     # print the current count of every key
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = "maxhemmerich.github.io"          # same namespace GAMMA uses, so the fleet can be read together
BASE = "https://abacus.jasoncameron.dev"
KEY_PREFIX = "first-pass-ca-"

# one flat key per published page (Abacus rejects "/" in keys)
PAGES = [
    ("index.html", "home"),
    ("free-report/index.html", "free-report"),
    ("ats-keywords/index.html", "ats-keywords"),
    ("whats-in-the-pack/index.html", "whats-in-the-pack"),
    ("pack-sample/index.html", "pack-sample"),
    ("buying/index.html", "buying"),
    ("tech-salaries/index.html", "tech-salaries"),
    ("tech-salaries-by-city/index.html", "tech-salaries-by-city"),
    ("tech-average-pay/index.html", "tech-average-pay"),
    ("job-vacancies-by-industry/index.html", "job-vacancies-by-industry"),
    ("tech-vacancies-by-occupation/index.html", "tech-vacancies-by-occupation"),
    ("stats/index.html", "stats"),
]

MARK = "<!-- ALPHA page counter (Abacus"
BLOCK_RE = re.compile(r"<!-- ALPHA page counter.*?</script>\n", re.S)


def key(slug):
    return KEY_PREFIX + slug


def snippet(slug):
    url = "%s/hit/%s/%s" % (BASE, NS, key(slug))
    return (
        MARK + " \u2014 one anonymous hit per load, no cookie, no identifier; reader at /stats/ -->\n"
        "<script>\n"
        "(function(){try{\n"
        '  fetch("' + url + '", {mode:"no-cors",cache:"no-store",keepalive:true}).catch(function(){});\n'
        "}catch(e){}})();\n"
        "</script>\n"
    )


def inject():
    """Write/refresh the counter snippet in every page. Idempotent."""
    for rel, slug in PAGES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print("skip (absent):", rel)
            continue
        with open(path, "r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        had = MARK in text
        text = BLOCK_RE.sub("", text)
        if "</body>\n" in text:
            text = text.replace("</body>\n", snippet(slug) + "</body>\n", 1)
        elif "</body>" in text:
            text = text.replace("</body>", snippet(slug) + "</body>", 1)
        else:
            print("WARN no </body> in", rel)
            continue
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print(("refreshed " if had else "injected  ") + rel, "->", key(slug))


def read_key(slug):
    """Return the current integer for a key, or None when the key does not exist yet."""
    url = "%s/get/%s/%s" % (BASE, NS, key(slug))
    req = urllib.request.Request(url, headers={"User-Agent": "first-pass-counter/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return int(json.loads(r.read().decode("utf-8"))["value"])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def page_url(rel):
    slug = rel[:-len("index.html")] if rel.endswith("index.html") else rel
    return "https://maxhemmerich.github.io/first-pass-ca/" + slug


def render_stats():
    rows = []
    for rel, slug in PAGES:
        try:
            n = read_key(slug)
        except Exception as e:                       # network hiccup: say so, don't invent
            n = "error: %s" % e
        shown = "not yet" if n is None else n
        rows.append(
            '    <tr><td class="p"><a href="%s">/%s</a></td>'
            '<td class="k mono">%s</td>'
            '<td class="n mono" data-slug="%s">%s</td></tr>'
            % (page_url(rel), rel[:-len("index.html")].rstrip("/"), key(slug), slug, shown)
        )
    body = "\n".join(rows)
    html = (STATS_HTML.replace("<!--ROWS-->", body)
                     .replace("__NS__", NS)
                     .replace("<!--COUNTER-->", snippet("stats")))
    out = os.path.join(ROOT, "stats", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(html)
    print("wrote", out)


STATS_HTML = """<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>First Pass — page view counts</title>
<meta name="robots" content="noindex">
<meta name="description" content="Internal: the anonymous per-page view count for the First Pass pages.">
<style>
  :root{--bg:#0B0B0C;--panel:#131316;--ink:#F2F0EA;--muted:#9A968C;--rule:#2A2A2F;--accent:#FFB020;
        --mono:Consolas,'SF Mono',ui-monospace,monospace}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
       font-family:'Segoe UI',-apple-system,Helvetica,Arial,sans-serif;line-height:1.5}
  .wrap{max-width:760px;margin:0 auto;padding:48px 20px 80px}
  h1{font-family:Georgia,'Times New Roman',serif;font-size:30px;margin:0 0 6px}
  .lede{color:var(--muted);margin:0 0 28px;font-size:15px}
  table{width:100%;border-collapse:collapse;border-top:1px solid var(--rule)}
  th,td{text-align:left;padding:10px 8px;border-bottom:1px solid var(--rule);font-size:14.5px}
  th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
  .mono{font-family:var(--mono)}
  td.n{text-align:right;color:var(--accent);font-size:16px}
  td.k{color:var(--muted);font-size:12.5px}
  a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule)}
  a:hover{border-bottom-color:var(--accent)}
  .fnote{color:var(--muted);font-size:12.5px;margin-top:26px}
</style>
</head>
<body>
<div class="wrap">
  <h1>Page view counts</h1>
  <p class="lede">One anonymous hit per page load. No cookie, no identifier, no per-visitor data —
    each row is a single integer read from Abacus (no account, no API key). Values refresh live on
    load; the printed number is the reading at build time.</p>
  <table>
    <thead><tr><th>Page</th><th>Key</th><th style="text-align:right">Views</th></tr></thead>
    <tbody>
<!--ROWS-->
    </tbody>
  </table>
  <p class="fnote">FIRST PASS · internal reader · not linked from the site and not in sitemap.xml.</p>
</div>
<script>
(function(){
  document.querySelectorAll("td.n[data-slug]").forEach(function(td){
    var u="https://abacus.jasoncameron.dev/get/__NS__/first-pass-ca-" + td.getAttribute("data-slug");
    fetch(u,{cache:"no-store"}).then(function(r){return r.json();}).then(function(j){
      if (j && typeof j.value === "number") td.textContent = j.value;
    }).catch(function(){});
  });
})();
</script>
<!--COUNTER-->
</body>
</html>
"""


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "inject"
    if cmd == "inject":
        inject()
    elif cmd == "stats":
        render_stats()
    elif cmd == "read":
        for rel, slug in PAGES:
            print("%-28s %-34s %s" % (rel, key(slug), read_key(slug)))
    else:
        print(__doc__)
