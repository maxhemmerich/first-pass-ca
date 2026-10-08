# -*- coding: utf-8 -*-
"""Free lead magnet: The Screen Report. Every number is measured (see internal/*.json).

Day 6 (8 October 2026): the how-to-answer material was removed so the free report is the measured
result only. The anchor-rule scripts and the 200-character template moved out, because the paid
pack's sections 02 and 05 are built on exactly those answers and were being delivered free. What
stays is the counted data: the ranked questions, the 25 salary wordings and the published bands.
"""

DOC = {
    "title": "The Screen Report",
    "subtitle": ("What 141 Canadian technical job postings ask|"
                 "before a person reads your resume.|"
                 "Free. The paid pack is 21 pages."),
    "subject": "Measured screening questions from 141 Canadian technical job postings",
    "cover_footer": "",
    "blocks": [
        # ---------------- page 2: method ----------------
        ("h1", "Method"),
        ("p", "Between 24 September and 5 October 2026, 141 Canadian job postings for technical roles were "
              "collected: data analyst, business intelligence, data engineering, machine learning, clinical "
              "data and software roles, almost all of them in Ontario. 140 were readable in full."),
        ("p", "43 of those postings published the employer's own application questions together with the form "
              "fields, so those 43 could be counted instead of guessed at. 39 published the answer set that "
              "went with them. 53 were scored against a written fit rubric. Across the 43, there are 224 "
              "distinct question strings."),
        ("h3", "What this is not"),
        ("bul", [
            "It is not a random sample of the Canadian market and it is not a survey of employers. It is one "
            "applicant's pipeline, counted.",
            "It is not a description of how any named company's screening software works internally. Nothing "
            "here comes from inside a vendor's system.",
            "It asserts nothing about hiring outcomes. No placement result is claimed anywhere in this document.",
        ]),
        ("h3", "How to read a number in this report"),
        ("p", "Every count is a match against those posting texts. <font face='Courier'>Excel 56</font> means 56 "
              "of the 140 readable postings contain the word Excel. <font face='Courier'>salary 27 / 43</font> "
              "means 27 of the 43 postings that published questions ask something about pay. Where a claim "
              "about the screening process appears, it is written as what the posting itself exposes: a "
              "required field, a knockout question, a character limit, a published band."),
        ("callout", "Announcements about artificial intelligence in hiring describe software nobody outside the "
                    "vendor can inspect. What you can inspect is the form you are being asked to fill in. That "
                    "form is where the decision starts, and it is the only part of the process you can read "
                    "before you are rejected."),

        ("pb",),
        # ---------------- page 3: ranked questions ----------------
        ("h1", "The questions employers actually ask"),
        ("p", "Counted from the 43 postings that published their own screening questions. The bar shows the "
              "share of those 43."),
        ("bars", [
            ("Salary expectations", 27, 43, "asked in 25 different wordings"),
            ("Work authorization or visa sponsorship", 12, 43, "wording varies: eligible, authorized, require sponsorship"),
            ("Years of experience", 10, 43, "often a required field on every row of a skills grid"),
            ("A completed degree", 6, 43, "bachelor, master, or post-secondary"),
            ("Technologies, by name", 6, 43, "one caps the answer at 200 characters"),
            ("Location or commuting distance", 5, 43, "Greater Toronto Area or reasonable commute"),
            ("References or a background check", 4, 43, "consent wording included with the application"),
            ("Accommodation requests", 3, 43, "an offer to state needs, optional"),
            ("French proficiency", 2, 43, "a five-level scale, not a yes or no"),
            ("Start date or availability", 1, 43, "notice period"),
        ]),
        ("h3", "The two extremes in one sample"),
        ("p", "One posting asks you to fill a grid of <font face='Courier'>41</font> skills, and every single row "
              "carries its own required <font face='Courier'>Years of experience*</font> and "
              "<font face='Courier'>Proficiency*</font> value. Another posting asks what technologies you know and "
              "stops you at <font face='Courier'>200 characters</font>. One wants structured volume, the other "
              "wants editing. Answering both the same way loses one of them."),
        ("callout", "A required field with an asterisk is the first screen, and it is not scored on quality. If it "
                    "is blank, the form does not submit. If it contradicts a hard requirement in the posting, no "
                    "amount of resume quality reverses it."),

        ("pb",),
        # ---------------- page 4: the salary wordings ----------------
        ("h1", "The same question, 25 wordings"),
        ("p", "Verbatim from the postings that ask about pay, punctuation as published. The count on the left is "
              "how many postings used that exact wording."),
        ("mono", "3&nbsp;&nbsp; Please indicate your minimum annual salary expectations (Non-Union positions only):"),
        ("mono", "3&nbsp;&nbsp; What are your salary expectations?"),
        ("mono", "2&nbsp;&nbsp; What is your desired pay rate?"),
        ("mono", "2&nbsp;&nbsp; What are your base salary expectations?"),
        ("mono", "2&nbsp;&nbsp; What is your expected salary?"),
        ("mono", "1&nbsp;&nbsp; What is your desired salary?"),
        ("mono", "1&nbsp;&nbsp; What is your desired annual salary?"),
        ("mono", "1&nbsp;&nbsp; what is your desired annual base salary?"),
        ("mono", "1&nbsp;&nbsp; What are your salary expectations for this position?"),
        ("mono", "1&nbsp;&nbsp; What are your salary expectations for the position?"),
        ("mono", "1&nbsp;&nbsp; What are your annual salary expectations for this position?"),
        ("mono", "1&nbsp;&nbsp; What are your annual salary expectations in CAD?"),
        ("mono", "1&nbsp;&nbsp; What are your annual salary expectations in USD?"),
        ("mono", "1&nbsp;&nbsp; What is your target salary expectation (specific figure or range) for this position?"),
        ("mono", "1&nbsp;&nbsp; Please give your desired total annual compensation"),
        ("mono", "1&nbsp;&nbsp; What are your salary expectations for this entry level, hybrid full-time role? Please ensure you mention your response to be considered further."),
        ("mono", "1&nbsp;&nbsp; What are your salary expectations for this entry-level, hybrid full-time role? Please refer to the salary range listed in the job posting when providing your response."),
        ("mono", "1&nbsp;&nbsp; What is your desired salary for this position? (You may include a single number or a range.) USD."),
        ("mono", "1&nbsp;&nbsp; The poster outlines our salary band at the job grade 13 level ($66,179 - 77,858) along with more details on a potential performance bonus (3-5%)"),
        ("mono", "1&nbsp;&nbsp; This position offers an annual base salary of $95k-$105k + an additional 12% annual bonus. Does this align with your expectations?"),
        ("p", "Read those three at the bottom again. One tells you the band and the bonus before you answer. One "
              "tells you to read the band on the posting before you answer. One asks whether a specific number "
              "works for you, which is a yes-or-no, not a negotiation. Those three are answered differently, and "
              "none of them is answered with the word competitive."),
        ("callout", "27 of 43 postings ask about money. The answer you type into the form is the number you are "
                    "later anchored to. That is the whole reason the paid pack puts the salary section before the "
                    "interview section."),

        ("pb",),
        # ---------------- page 5: what the posting exposes ----------------
        ("h1", "What the posting tells you before a human reads anything"),
        ("num", [
            "<b>The asterisk.</b> Required fields are the first screen. In this sample they are the pay box, the "
            "years-of-experience box and the skills grid.",
            "<b>The knockout questions.</b> Work authorization and sponsorship (12 of 43), a completed degree "
            "(6 of 43), and location or commute (5 of 43). These are single-select, and a wrong answer is not a "
            "judgement call, it is a filter.",
            "<b>The character limit.</b> A published cap of 200 characters for a technologies answer. A cap is a "
            "test of editing, not of knowledge.",
            "<b>The skills grid.</b> A row per skill, with required years and proficiency. One posting in the "
            "sample has 41 rows.",
            "<b>The consent box.</b> Background checks and reference release appear in 4 of 43 postings, with "
            "release wording you accept before you can submit.",
            "<b>The published band.</b> Seven salary bands and two hourly rates in this sample. Where one exists, "
            "it is the number to anchor to.",
        ]),
        ("h3", "The published bands in this sample"),
        ("grid", ["Band as published", "Kind"], [
            ["$45,000 – $55,000", "annual"],
            ["$50,000 – $60,000", "annual"],
            ["$63,700 – $74,900", "annual"],
            ["$65,000 – $75,000", "annual"],
            ["$75,000 – $85,000", "annual"],
            ["$86,379 – $127,288", "annual"],
            ["$110,000 – $130,000", "annual"],
            ["$37.47 – $46.84", "hourly"],
            ["$40.49 – $60.73", "hourly"],
        ], [230, 120]),
        ("small", "Quoted from postings that chose to publish a band, so these are examples from this sample, "
                  "not a market range."),
        ("callout", "One employer published its grade structure with the range: job grade 13 level, $66,179 to "
                    "77,858, plus a 3-5% performance bonus."),

        ("pb",),
        # ---------------- page 6: the pack ----------------
        ("h1", "What the paid pack adds"),
        ("p", "The Screen Report is the measured result. The pack, <b>First Pass</b>, is 21 pages of what to do "
              "with it: the answer shape for every question in the ranked list, the keyword map by role family, "
              "the salary scripts in full, twelve screening-call questions with model answers, the negotiation "
              "section written for the Canadian market, and the reference tables."),
        ("grid", ["Section", "What it gives you", "Pages"], [
            ["01 How the screen works", "The observable signals, and what is not observable", "3-4"],
            ["02 The decision questions", "Each question, what it tests, the answer shape, the failure mode", "5-6"],
            ["03 Work authorization", "The real wordings, and what a Canadian applicant answers", "7-8"],
            ["04 Keyword map", "By role family, with where each term belongs on the page", "9-11"],
            ["05 The salary question", "25 wordings, the anchor rule, three complete scripts", "12-14"],
            ["06 The screening call", "12 questions by level, with the answer shape", "15-16"],
            ["07 Negotiation, Canada", "Bands, counters, bonus components, when to stop", "17-18"],
            ["08 Reference", "Full keyword table, question list, one-page checklist", "19-21"],
        ], [116, 268, 40]),
        ("h3", "Where to get it"),
        ("p", "The pack is CA$24 plus tax at checkout, and the page is <font face='Courier'>%s</font>. The checkout is live: "
              "Gumroad takes the card and delivers the pack. Price checked 8 October 2026. Corrections to "
              "its data are welcome." % ("https://maxhemmerich.github.io/first-pass-ca/")),
        ("h3", "Limits, once more, on the last page where you can still read them"),
        ("bul", [
            "141 postings, Ontario-heavy, collected on 5 October 2026. Not a market survey.",
            "This document is information, not advice, not legal or immigration or tax advice, and not a "
            "promise of an interview or a job.",
            "No employer endorsed this document or supplied anything in it.",
        ]),
    ],
}
