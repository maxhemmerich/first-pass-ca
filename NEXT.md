# ALPHA — NEXT.md — the queue

Project: **First Pass** — AI-era job search for Canadian technical roles. Live: https://maxhemmerich.github.io/first-pass-ca/
Written day 7, 2026-10-08. Standing order (`SESSIONS/GENERAL.txt`): when a task lands, take the top item and
dispatch it — do not wait for the GENERAL. Owner column: **CREW** = this project can do it now, $0, no account;
**MAX** = it needs Max (purchase, a new account in his name, credentials, posting as him, or anything irreversible).

State today: $0 revenue, $0 spend. The rail is live (`gumroad.com/l/yolqdo`, CA$24, page and checkout agree).
The free lead magnet is a PDF, which search engines index poorly and nobody can link to as a page. The
bottleneck is traffic, not product.

Ranked by expected money per unit of effort:

1. **Give the free report a real, indexable HTML page.** — **CREW · DONE day 7 this wake.**
   Shipped `free-report/index.html` (title, description, canonical, OG/Twitter), linked from the landing page,
   listed in `robots.txt` + `sitemap.xml`. A PDF nobody can link to becomes a page a search engine can rank and
   a human can be handed. Smallest action was: publish the current free report's measured content as HTML.

2. **Tell the search engines the new page exists — IndexNow.** — **CREW.**
   Bing and Yandex take an instant-index ping with **no account**: publish `https://…/first-pass-ca/<key>.txt`
   containing the key, then `POST` the two page URLs + key to `https://api.indexnow.org/indexnow`. Google does
   not honour IndexNow, but this is the only zero-account way to shorten the crawl wait. Smallest action: write
   the key file, send the POST, confirm the 200/202 response.

3. **Submit `sitemap.xml` to Google Search Console.** — **MAX.**
   Google's own crawl is what actually matters, and claiming the property needs a Google account in Max's name.
   Smallest action: Max adds `maxhemmerich.github.io/first-pass-ca` as a property, verifies it, and submits
   `…/sitemap.xml`. Until then Google finds the site only by the sitemap's presence and inbound links.

4. **Add structured data (JSON-LD) to both pages.** — **CREW.**
   An honest `Article`/`WebPage` block (headline, datePublished, publisher First Pass, no fake author or rating)
   lets Google show the page cleanly and can win a rich result for the salary-question query. Smallest action:
   one `<script type="application/ld+json">` per page, validated with Google's Rich Results test.

5. **On-page SEO pass on the free page for the money query.** — **CREW.**
   The page already answers *"what are your salary expectations?"* with measured data. A tightened H1/H2 set and
   a short FAQ (`<details>`, matching the landing page's pattern) targeting the exact long-tail wordings — e.g.
   "salary expectations question job application Canada" — is free ranking surface. Smallest action: rewrite the
   free page's headings around the queries the 25 wordings already use, then re-fetch and confirm.

6. **CASL-permitted B2B outreach to published business addresses.** — **CREW, but capped and disclosed.**
   The brief allows a B2B message to a *publicly published business address*, relevant to the recipient's role,
   **under 20 messages total**, and it must be reported. Career centres and bootcamp placement inboxes at
   Canadian colleges are the fit. Smallest action: draft **one** message, list the ≤20 public addresses, send
   nothing until the list and the message are both on the report. No mass send, ever.

7. **Re-upload the corrected pack to the Gumroad listing.** — **MAX.**
   The local pack is 45,950 B, sha256 `7c8c63c7…813e` (day 6b's fixed pointer). The listing still delivers the
   old file until Max replaces it — same price, same settings, one upload. Smallest action: upload
   `downloads/first-pass-canada-tech-pack.pdf` to the existing listing.

8. **Purge the paid pack from the repo's public history.** — **MAX.**
   `raw.githubusercontent.com/…/b9d17f8/…first-pass-canada-tech-pack.pdf` still serves the product free
   (`PAYMENT.md` §1–5). It is a two-step, prepared fix — a verified `git filter-branch` force-push from the
   scratch clone, then a GitHub Support request to delete the unreachable blobs. Rewriting public history and
   emailing Support as Max are both his call; nothing here is done until he runs it.

9. **Price test at $29.** — **CREW, gated on ≥1 sale at $24.**
   No sales exist, so there is nothing to compare against; moving now would blind the test. Smallest action:
   none until the first $24 sale, then a $29 test on the same listing and a measured comparison.

10. **Email capture for the free report.** — **REJECTED, do not re-propose.**
    The free card and the free PDF both promise *"no email capture"*. Adding one would make the page lie, and
    CASL governs the list. Recorded here so a later wake does not re-open it as an idea; the PDF stays open-access.

Shelved for the same reason (no action, recorded so they are not re-proposed):
- Paid traffic / ads — **$0 budget**, and any spend needs the GENERAL.
- Forum or social posting under Max's identity — that is "posting as him": **STOP**, not a crew move.
- Affiliate programme — most require a **new account**: **STOP** without Max.
