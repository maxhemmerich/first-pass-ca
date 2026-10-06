# -*- coding: utf-8 -*-
"""The paid pack: First Pass - Canada Technical Job Search Pack.
Every number is measured from the 141-posting sample (internal/aggregates.json,
internal/categories.json). No testimonials, no external statistics, no invented results.
"""

URL = "https://maxhemmerich.github.io/first-pass-ca/"

DOC = {
    "title": "Canada Technical Job Search Pack",
    "subtitle": ("The screening questions, the keyword map and the salary|"
                 "scripts, measured from 141 Canadian technical postings.|"
                 "21 pages. Data collected 5 October 2026."),
    "subject": "First Pass - Canadian technical job search pack",
    "cover_footer": "",
    "blocks": [
        # ---------------- p2: how to use ----------------
        ("h1", "How to use this in twenty minutes"),
        ("p", "You do not need to read this pack front to back. It is built so that the two sections that "
              "change outcomes come first."),
        ("num", [
            "<b>Read section 01 (pages 3-4).</b> It is the map: what the form decides, what an employer can "
            "see, and where the decision is actually made. Everything else assumes it.",
            "<b>Go to section 05 and answer the salary question properly.</b> 27 of the 43 postings in the "
            "sample ask about pay, in 25 wordings, usually before a human sees the file. This is the single "
            "question most likely to end your application, and the one most people answer badly by reflex.",
            "<b>Do section 04 against the posting you are applying to now.</b> Take the second column, count "
            "how many of those terms appear in your resume. Under ten and the parse has little to work with.",
            "<b>Keep section 08 open.</b> Keyword table, question list and the checklist are reference.",
        ]),
        ("h3", "Contents"),
        ("grid", ["Section", "What it covers", "Pages"], [
            ["01 How the screen works", "Only what the postings themselves expose", "3-4"],
            ["02 The decision questions", "Ranked, with the answer shape and the failure mode", "5-6"],
            ["03 Work authorization", "The real wordings, and how to answer them", "7-8"],
            ["04 The keyword map", "By role family, with where each term belongs", "9-11"],
            ["05 The salary question", "25 wordings, the anchor rule, three scripts", "12-14"],
            ["06 The screening call", "Twelve questions by level, with the answer shape", "15-16"],
            ["07 Negotiation, Canada", "Bands, counters, bonus components, when to stop", "17-18"],
            ["08 Reference", "Full keyword table, question list, one-page checklist", "19-21"],
        ], [122, 262, 40]),
        ("small", "Every count in this pack comes from the sample described in the method note: 141 Canadian "
                  "technical job postings collected on 5 October 2026, 140 readable in full, 43 that published "
                  "the employer's own screening questions. Where a number appears, it is a count of postings. "
                  "Nothing is estimated and nothing is attributed to a study."),

        ("pb",),
        # ---------------- p3-4: section 01 ----------------
        ("h1", "01. How the screen works, from the outside"),
        ("p", "Nobody outside a hiring vendor can read the software. What you can read is the form, and the form "
              "is where the decision starts. Six signals in this sample do that work, and each one tells you what "
              "to do next."),
        ("h2", "The signals you can actually see"),
        ("h3", "1. The asterisk is a gate, not a score"),
        ("p", "A required field must be filled before the form will submit. In this sample the required fields "
              "are the pay box, the skills grid, degree and work authorization. A blank field does not score "
              "badly, it stops the application. Filling it with something wrong is worse: a single-select answer "
              "that contradicts a stated requirement is a filter, not a judgement call."),
        ("h3", "2. Four knockout questions sit in front of the resume"),
        ("p", "In this sample: work authorization or sponsorship (12 of 43), a completed degree (6 of 43), "
              "location or commuting distance (5 of 43), and salary (27 of 43). Three of those four have an "
              "answer the posting itself defines, so there is nothing to argue about. The fourth, salary, is the "
              "one where the answer is yours and where a careless number costs money for as long as you work "
              "there."),
        ("h3", "3. The same question arrives in many shapes"),
        ("p", "Salary appears in 25 different wordings across 27 postings. Some ask for a minimum, some for a "
              "desired rate, some in USD, one asks for total annual compensation, one asks whether a specific "
              "number works for you. \u201cSalary expectations\u201d is not one question and cannot have one "
              "canned answer."),
        ("h3", "4. Volume and precision are asked for in the same pipeline"),
        ("p", "One posting asks for 41 skills in a grid, each row with a required years value and a required "
              "proficiency value, which is 123 required fields before you have written a sentence. Another "
              "posting asks what you know and caps the answer at 200 characters. The first rewards an inventory, "
              "the second rewards editing. Read the posting for which one you are filling in."),
        ("h3", "5. Keywords are matched, and spelling is free to get right"),
        ("p", "The postings name their tools explicitly, and this sample shows how tightly the vocabulary "
              "clusters around a few terms: Excel in 56 of 140, SQL in 45, Python in 44, Power BI in 36. A "
              "resume that names the same tools in the posting's own spelling gives a parser more to match. The "
              "spelling rule costs you nothing: copy the posting's characters, not your habit."),
        ("h3", "6. A person still reads something"),
        ("p", "Screening software shortlists and ranks, it does not hire. The practical consequence is that "
              "everything in your file has to survive two readings that want different things: the machine wants "
              "the terms present and the fields consistent, the human wants one sentence that says what you did "
              "and what happened. A resume written only for the machine reads like a keyword list to the human, "
              "which is why section 04 gives each term a home on the page rather than a place in a word cloud."),
        ("callout", "The rule that follows from all six: fill every required field honestly, answer the four "
                    "knockout questions in the posting's own terms, put the posting's keywords in their own "
                    "spelling into the most recent role first, and keep one sentence per bullet for the human."),
        ("warn", "What this pack does not claim: it does not know any vendor's internal ranking, it does not "
                 "promise you an interview, and it has no placement results to show because there are none. "
                 "Claims of that kind would be invented, and inventing them is the thing this pack exists to "
                 "replace."),

        ("pb",),
        # ---------------- p5-9: section 02 ----------------
        ("h1", "02. The decision questions"),
        ("p", "Ranked by how often they appear in the 43 postings that published questions. For each one: what "
              "the employer is testing, the answer shape, an example you can copy, and the failure mode that "
              "gets it rejected."),
        ("h2", "Salary expectations - 27 of 43"),
        ("p", "<b>Testing:</b> whether you can place yourself against a published band, and whether your number "
              "is near theirs. <b>Answer shape:</b> one number or a tight range, inside the published band when "
              "there is one, above the midpoint, with the requirement you meet named in the same sentence. "
              "<b>Failure mode:</b> \u201cnegotiable\u201d, \u201copen to discussion\u201d, \u201cmarket "
              "rate\u201d, or a number that ignores a band the posting printed. Section 05 has the three full "
              "scripts."),
        ("h2", "Work authorization or visa sponsorship - 12 of 43"),
        ("p", "<b>Testing:</b> whether hiring you needs paperwork and a wait. <b>Answer shape:</b> your status "
              "in the posting's own vocabulary, plus the fact that decides it: permanent resident, citizen, or "
              "the specific permit you hold and its expiry. <b>Failure mode:</b> a bare \u201cyes\u201d or "
              "\u201cno\u201d to a question with two parts, or leaving it blank because you are unsure. Section "
              "03 lists the real wordings."),
        ("h2", "Years of experience - 10 of 43, and often a required field on every row"),
        ("p", "<b>Testing:</b> whether your years clear a hard minimum, and in the grid version, whether your "
              "years are consistent across the skills you claim. <b>Answer shape:</b> whole years for the "
              "specific tool or duty, not your entire career, and the same number everywhere it appears. "
              "<b>Failure mode:</b> one number in the form and different numbers in the resume, or a proficiency "
              "of expert against one year. The grid in this sample asks for 41 rows; inconsistency across 41 rows "
              "is easy to create and hard to defend."),
        ("h2", "A completed degree - 6 of 43"),
        ("p", "<b>Testing:</b> usually a hard requirement, occasionally a preference. <b>Answer shape:</b> the "
              "credential you hold, exactly as awarded, with the institution named in the resume and not in the "
              "box. <b>Failure mode:</b> selecting the closest option when the question wants a yes or no, or "
              "leaving a required education box empty because your degree is adjacent rather than exact."),
        ("h2", "Technologies, by name - 6 of 43, one capped at 200 characters"),
        ("p", "<b>Testing:</b> whether you can produce the specific tools the team uses, and whether you can "
              "write under pressure. <b>Answer shape:</b> the posting's first tool, your level in their "
              "vocabulary, where you used it, one line of proof. <b>Failure mode:</b> a list of fifteen tools "
              "with no levels and no proof, or spending the cap on adjectives."),
        ("h2", "Location or commuting distance - 5 of 43"),
        ("p", "<b>Testing:</b> whether you can physically be there on the schedule they have in mind. "
              "<b>Answer shape:</b> a plain yes with your city named, or a plan with dates if you are moving. "
              "<b>Failure mode:</b> a general answer about being \u201copen to relocating\u201d with no date, "
              "which reads as no."),
        ("h2", "References or a background check - 4 of 43"),
        ("p", "<b>Testing:</b> consent and lead time. <b>Answer shape:</b> consent, given with the understanding "
              "that a check is normal at offer stage. <b>Failure mode:</b> accepting a release clause without "
              "reading what you are releasing, or naming references before you have warned them. These postings "
              "include release wording; read it before you tick it."),
        ("h2", "Accommodation requests - 3 of 43"),
        ("p", "<b>Testing:</b> nothing about your ability. <b>Answer shape:</b> silence if you need nothing, or "
              "one line describing the adjustment you need in the process, not a diagnosis. <b>Failure mode:</b> "
              "assuming the question is a trap. It is optional in every posting in this sample, and it is "
              "separated from the scored answers by design."),
        ("h2", "French proficiency - 2 of 43"),
        ("p", "<b>Testing:</b> a real requirement for some bilingual posts, and a formality for others. "
              "<b>Answer shape:</b> use their five-level scale honestly; whether the role is designated "
              "bilingual is stated in the posting. <b>Failure mode:</b> inflating the level on the form, then "
              "meeting a French-speaking panel."),
        ("h2", "Start date or availability - 1 of 43"),
        ("p", "<b>Testing:</b> notice period and urgency. <b>Answer shape:</b> a date, and the notice period that "
              "produces it. <b>Failure mode:</b> \u201cimmediately\u201d when you owe two weeks, which becomes a "
              "credibility problem on day one of the offer."),
        ("h3", "Across all ten"),
        ("p", "Consistency is the asset. The same years, the same tool spellings, the same status and the same "
              "number everywhere those values appear, in the form, in the resume and in the call. This sample "
              "includes forms with 123 required fields; nobody re-reads them for you."),
        ("h3", "The four values that have to agree"),
        ("p", "Across the form, the resume and the call, these four values are compared by anyone who bothers to "
              "compare them, and mismatches are the cheapest reason to lose an application:"),
        ("bul", [
            "<b>Years per tool.</b> The same number in the skills grid, in the resume bullet that claims the "
            "tool, and in your answer on the call.",
            "<b>Tool spelling.</b> The posting's exact string, in all three places. Section 04 has the rule.",
            "<b>Work status.</b> The same status, with the same dates, in all three. If your permit expires, "
            "that date appears once and consistently.",
            "<b>The salary number.</b> Whatever you put in the form is the number you will be held to. Write it "
            "down before you type it, because it will be quoted back to you in the call.",
        ]),

        ("pb",),
        # ---------------- p10-11: section 03 ----------------
        ("h1", "03. Work authorization and sponsorship"),
        ("p", "Twelve of the 43 postings ask something about your right to work. The wording decides what the "
              "correct answer is, and the wordings are not equivalent."),
        ("h3", "The wordings found in this sample"),
        ("quote", "Are you legally eligible to work for any employer in Canada?"),
        ("quote", "Will you now or in the future require work visa sponsorship?"),
        ("quote", "Will you need sponsorship for an employment visa?"),
        ("quote", "If you currently hold an Open Work Permit, please provide the validity date (month and year) "
                  "along with the date of issuance."),
        ("quote", "Do you have a valid Canadian Passport OR B1B2 US Visa?"),
        ("quote", "Are you legally authorized to work in the United States?"),
        ("p", "Those are four different questions. The first is about eligibility today, the second and third are "
              "about future sponsorship, the open-permit one wants dates, and the last two are about travel to "
              "the United States. Answering \u201cyes\u201d to all of them, or \u201cno\u201d to all of them, "
              "produces at least one wrong answer."),
        ("h2", "What each answer actually is"),
        ("bul", [
            "<b>Eligible to work in Canada, no sponsorship ever:</b> citizen, or permanent resident. The "
            "sponsorship questions are then a clear no, even though they are worded to sound like a trap.",
            "<b>Eligible now, sponsorship needed later:</b> a work permit with an end date. Eligible answers "
            "yes; the sponsorship question is also yes, and both are true at once. Say so before they find out, "
            "because the permit dates are in the application anyway.",
            "<b>Not eligible without sponsorship:</b> say it plainly and lead with the part that is in your "
            "control, which is the timeline and whether the role is on a pathway that supports it.",
            "<b>Post-graduate work permit:</b> name it as such. It is open, it has dates, and employers "
            "recognise it. Give the expiry.",
        ]),
        ("callout", "Where the rule comes from: eligibility, permits and sponsorship are set by Immigration, "
                    "Refugees and Citizenship Canada, not by the employer or by this pack. If your situation is "
                    "not one of the four above, read the IRCC page for your permit type before you answer, and "
                    "if the stakes are high, get advice from a licensed immigration consultant or lawyer. This "
                    "pack is not immigration advice."),
        ("h3", "What never helps"),
        ("bul", [
            "Leaving it blank. In this sample these are required fields, so a blank is a lost application.",
            "Answering about your passport when the question asked about sponsorship.",
            "Overstating your status. It is discovered at the offer stage, after you have spent the time.",
        ]),
        ("h2", "If you are not in Canada yet"),
        ("p", "The postings in this sample all ask the question in Canadian terms, so answer in Canadian terms. "
              "Your status here is one of a small number of categories, and the honest one to type is the one on "
              "your document: a work permit with dates, a permanent resident card, a study permit with its "
              "conditions, or none of those yet. If the answer is none of those yet, say what would change it "
              "and when, in one line, because that is the only part of the timeline a hiring manager can plan "
              "around. Do not answer a sponsorship question with your passport, and do not answer a Canadian "
              "eligibility question with a US status."),
        ("warn", "Permit types, eligibility and sponsorship are decided by IRCC and by the terms of your own "
                 "document, not by this pack and not by the employer's form. Read the IRCC page for your permit "
                 "type before you answer, and if your situation is not straightforward, take advice from a "
                 "licensed immigration consultant or lawyer. That is a fact stated plainly, not a referral."),

        ("pb",),
        # ---------------- p12-15: section 04 ----------------
        ("h1", "04. The keyword map"),
        ("p", "The counts are how many of the 140 readable postings in the sample name that term. Column three "
              "is placement: a term in a skills list is matched, but a term in a bullet is also read by the "
              "human. Every posting's first tool belongs in your most recent role's first bullet."),
        ("grid", ["Term", "Postings", "Where it belongs"], [
            ["Excel", "56", "Skills line, plus one bullet naming the output it produced"],
            ["SQL", "45", "First bullet of the most recent role, with the query's purpose"],
            ["Python", "44", "Skills line, plus one bullet naming what it built"],
            ["Power BI", "36", "Skills line, plus the audience the report went to"],
            ["stakeholder", "33", "One bullet that names who you reported to or worked with"],
            ["statistics", "32", "A bullet with the method and the sample size"],
            ["data quality", "26", "A bullet with what you found, and what you fixed"],
            ["R", "18", "Skills line only, unless the posting leads with it"],
            ["machine learning", "14", "A bullet with the problem, not the algorithm"],
            ["GCP", "13", "Skills line, in the posting's spelling"],
            ["Azure", "13", "Skills line, in the posting's spelling"],
            ["Snowflake", "13", "Skills line, plus where the data came from"],
            ["Tableau", "12", "Skills line, next to the BI tool you used most recently"],
            ["data warehouse", "10", "A bullet describing what fed it and how often"],
            ["ETL", "9", "A bullet with the source, the destination and the schedule"],
            ["AWS", "9", "Skills line, plus the service you actually used"],
            ["data governance", "8", "A bullet with the policy or standard you applied"],
            ["regression", "8", "A bullet with the outcome it predicted"],
            ["Power Automate", "8", "A bullet with the manual task it removed"],
            ["SAS", "5", "Skills line, only if the posting names it"],
            ["generative AI", "5", "A bullet describing the workflow, not the tool name"],
            ["DAX", "4", "Skills line, beside Power BI, if Power BI is claimed"],
            ["TensorFlow", "4", "Skills line, plus the model's purpose in a bullet"],
        ], [96, 44, 284]),
        ("h2", "By role family"),
        ("p", "The sample's own tagging splits the postings into families. The counts are how many postings in "
              "that family name the term, so read them as a share of a small number, not a market share."),
        ("h3", "Analytics (17 postings)"),
        ("mono", "Python 10 &nbsp; statistics 8 &nbsp; SQL 7 &nbsp; Power BI 5 &nbsp; Snowflake 5 &nbsp; "
                 "Excel 4 &nbsp; data quality 4 &nbsp; data warehouse 4 &nbsp; AWS 3 &nbsp; Git 3 &nbsp; "
                 "Tableau 3 &nbsp; R 3 &nbsp; regression 3"),
        ("p", "Analytics postings in this sample lead with Python and statistics more often than with SQL, which "
              "is the opposite of the general advice. If you are applying to analytics roles, the first two "
              "bullets should show a method and an outcome, and SQL belongs beside them, not instead of them."),
        ("h3", "Business intelligence (5 postings)"),
        ("mono", "Power BI 4 &nbsp; Excel 3 &nbsp; stakeholder 3 &nbsp; Python 2 &nbsp; SQL 2 &nbsp; "
                 "Databricks 1 &nbsp; Azure 1 &nbsp; Power Automate 1 &nbsp; Salesforce 1"),
        ("p", "BI postings in this sample are as interested in who you reported to as in which tool you used. "
              "stakeholder appears in 3 of 5. Write one bullet that names the audience and the decision it fed."),
        ("h3", "Everything else in the sample"),
        ("mono", "clinical data: GCP 3, stakeholder 2 &nbsp;&nbsp; operations analysis: Excel 3, Power BI 2, "
                 "Power Query 1 &nbsp;&nbsp; governance and compliance: Excel 3, data quality 1 &nbsp;&nbsp; "
                 "application support: SAP 3"),
        ("h2", "Worked example: three weak bullets, rewritten"),
        ("p", "The same experience, written twice. The first version has no terms a parser can match and no "
              "outcome a human can use. The second keeps the human sentence and carries the terms from the "
              "sample's top of the list. The years and numbers here are placeholders: put your own measured "
              "ones in."),
        ("h3", "Before"),
        ("mono", "&bull; Responsible for reporting and analysis across the department."),
        ("mono", "&bull; Worked with various stakeholders on data-related projects."),
        ("mono", "&bull; Helped improve data quality."),
        ("h3", "After"),
        ("mono", "&bull; Built and maintained 20+ SQL-backed Power BI reports for operations managers, covering "
                 "Excel and Snowflake sources, used in weekly staffing decisions."),
        ("mono", "&bull; Ran the quarterly KPI pack for 6 stakeholders across operations and finance, and "
                 "documented the definitions so the numbers stopped changing between teams."),
        ("mono", "&bull; Found and fixed a duplicate-record defect affecting 12% of intake rows; the fix removed "
                 "an estimated 6 hours of manual reconciliation per week."),
        ("p", "Both versions describe the same job. The second one names SQL, Power BI, Excel, Snowflake, "
              "stakeholders, KPI and data quality in the posting's spelling, keeps one sentence per bullet, and "
              "ends each bullet with what changed. That is the whole of the technique."),
        ("h2", "The spelling rule"),
        ("p", "Match the posting's characters. Power BI is not PowerBI, Power BI Desktop is not Power BI, and "
              "PL-300 is not a substitute for naming the tool. Take the exact string from the posting's "
              "requirements list and use it in your skills line, in the form, and in the first bullet of the "
              "most recent role. The cost of doing this is one minute per application; the cost of not doing it "
              "is showing up in fewer matches than you earned."),
        ("callout", "Do this test before you submit: open the posting's requirements list, and count how many of "
                    "its named tools appear in your resume, in its spelling. Under ten matches on a technical "
                    "posting means the machine has almost nothing to work with, whatever the resume looks like "
                    "to a person."),

        ("pb",),
        # ---------------- p16-20: section 05 ----------------
        ("h1", "05. The salary question"),
        ("p", "This is the question that most often ends an application and most often sets the number you live "
              "on. In the sample it appears in 27 of 43 postings, in 25 wordings, and on 9 posted bands."),
        ("h2", "The rule, in three parts"),
        ("num", [
            "<b>If the band is published, it is the target and the ceiling.</b> Answer inside it, above the "
            "midpoint, and name the requirement from the posting that justifies your position. This is not "
            "aggression, it is reading the range they printed.",
            "<b>If the band is not published, give a range with a real floor.</b> The floor is the number below "
            "which you would decline, not the number you would accept. Say the range, not a single number, "
            "unless the form only accepts a number.",
            "<b>Never say negotiable, competitive, or market rate.</b> Each one hands the numbering to the other "
            "side and tells them the answer costs you nothing to change.",
        ]),
        ("h2", "The three scripts"),
        ("h3", "Script one: the form that demands one number, with a band published"),
        ("quote", "I am targeting $[number], which sits in the upper half of your posted range of $[band low] to "
                  "$[band high]. That reflects [the named requirement from the posting that you meet, with your "
                  "years]."),
        ("p", "Worked example using a band from the sample, $75,000 to $85,000, midpoint $80,000, for an "
              "analytics role asking for SQL and Power BI: <i>I am targeting $83,000, which sits in the upper "
              "half of your posted range of $75,000 to $85,000. That reflects four years building SQL-backed "
              "Power BI reporting for operations teams, which is the requirement the posting leads with.</i>"),
        ("h3", "Script two: the recruiter call, band published, asked first"),
        ("quote", "Before I give you a number, can I confirm the band for this level? Good. I am targeting "
                  "$[number], which is inside it, and here is why in one line: [the requirement you meet]."),
        ("p", "Asking for the band first is not stalling when the band is published; it is confirming the level "
              "you are being screened against. If the band is not published, this is where you state your range "
              "and stop talking."),
        ("h3", "Script three: the email, before the first call"),
        ("quote", "Thanks for the note. To keep this simple: my range for this scope is $[low] to $[high], and I "
                  "am flexible inside it based on the whole package. If there is a posted band for the level, I "
                  "am happy to work to it."),
        ("p", "The email version works because it gives a range, gives a floor, and leaves the level open. It "
              "also creates a written record of the number, which matters in section 07."),
        ("h2", "The wordings that change what you answer"),
        ("bul", [
            "<i>Please indicate your minimum annual salary expectations</i> - the word minimum means the floor "
            "of your range, not your target. Say the floor you would sign at, and do not round it down.",
            "<i>What is your desired pay rate?</i> - rate language can be hourly. Confirm the unit before you "
            "type a number that reads as an annual figure in an hourly box.",
            "<i>What are your annual salary expectations in USD?</i> - currency is part of the answer. Never "
            "send a CAD figure into a USD box.",
            "<i>Please give your desired total annual compensation</i> - total means base plus bonus plus "
            "anything else you expect. If you give base there, you have given away the bonus.",
            "<i>This position offers an annual base salary of $95k-$105k plus an additional 12% annual bonus. "
            "Does this align with your expectations?</i> - a yes-or-no against a stated number, plus a bonus "
            "component. Answer yes when it works, and put the bonus in your own arithmetic so your number for "
            "later reflects it.",
            "<i>What are your salary expectations for this entry level, hybrid full-time role? Please ensure you "
            "mention your response to be considered further.</i> - the posting is telling you the answer is "
            "required. A blank is an automatic exit.",
        ]),
        ("h2", "When the ceiling is below your floor"),
        ("p", "This happens on wide bands, and it is not a reason to disappear. Answer the form honestly with "
              "your floor, then use the call to ask what is flexible. The script:"),
        ("quote", "The scope here looks closer to [what the role owns], and my floor is $[number]. If the band "
                  "for this level is firm, I understand. Is there flexibility on title, on the bonus component, "
                  "or on a review at six months?"),
        ("p", "Flexibility usually exists in one of those three places, in that order of likelihood, and asking "
              "for the review date costs nothing to grant."),
        ("h2", "The bonus component, and why it is not a rounding error"),
        ("p", "One posting in the sample published its grade band as $66,179 to $77,858 with a 3 to 5% "
              "performance bonus. At $77,000, a 5% bonus is $3,850. That is a raise you can negotiate in a "
              "sentence, and it is also the number that disappears when you give total compensation as base "
              "salary. When a posting separates base from bonus, keep them separate in every answer you give, "
              "and ask what the bonus has actually paid in the last two years."),
        ("h2", "After you have already given a number in the form"),
        ("p", "If you typed a number three applications ago and a recruiter now quotes it back, you have one "
              "opportunity to correct it and no more. Use it once, with a reason that is about scope rather than "
              "about second thoughts:"),
        ("quote", "The number I gave in the form was based on the posting as written. Now that I have seen the "
                  "scope of [the thing the posting did not spell out], my range is $[low] to $[high]."),
        ("p", "One correction is a person thinking. Two is a person who does not know their own number, and the "
              "second correction is the one that costs you the negotiation."),
        ("h2", "The long box: 1,500 characters for your salary answer"),
        ("p", "Some forms give you a proper box. The sample includes a 1,500-character limit alongside the "
              "one-line salary boxes, which is room for a structured answer. Use four short paragraphs, in this "
              "order: the number or range, the evidence, the flexibility you hold, and one question back."),
        ("mono", "Range: $[low] to $[high], inside your posted band of $[band low] to $[band high]. Based on "),
        ("mono", "[the requirement you meet, with years]. Flexible on the base if the bonus or the review "),
        ("mono", "date moves. What percentage is the bonus at this level?"),
        ("p", "That is 210 characters of the box used. The rest of the space is for evidence, not for "
              "enthusiasm, and not for an apology for having a number."),
        ("warn", "Do not let a published band become a legal claim. Every band in this sample was published by "
                 "the employer for its own posting, and the employer may change or withdraw it. This pack is "
                 "information, not legal or financial advice; for a contract dispute, use the law that applies "
                 "in your province and take advice from someone licensed there."),

        ("pb",),
        # ---------------- p21-23: section 06 ----------------
        ("h1", "06. The screening call"),
        ("p", "The first call is usually a recruiter confirming what the form already says, plus a few questions "
              "about scope. These twelve are the ones the postings' own requirements predict, grouped by level. "
              "Answer shapes, not scripts, because the wording will not match."),
        ("h2", "Entry level"),
        ("num", [
            "<b>What did you do in your last role, in two minutes?</b> Shape: what the team produced, your part "
            "of it, and one number. Failure: a chronological story that starts at university.",
            "<b>Which tools did you use daily, and which occasionally?</b> Shape: name the daily ones from the "
            "posting's list first. Failure: claiming everything on the posting at expert level.",
            "<b>Tell me about a time you found a problem in the data.</b> Shape: what you noticed, how you "
            "confirmed it, what you changed. Failure: a story where someone else fixed it.",
            "<b>How do you handle a request that changes while you are working on it?</b> Shape: what you "
            "confirm in writing before the change and who you tell.",
        ]),
        ("h2", "Intermediate"),
        ("num", [
            "<b>Walk me through a report you built end to end.</b> Shape: the question it answered, the source, "
            "the transform, the audience, the decision it changed. Failure: naming the tool three times.",
            "<b>How do you know your numbers are right?</b> Shape: reconciliation, a second method, and a "
            "recorded check. This is the 'data quality' term from the sample, and it is asked as a behaviour.",
            "<b>Who did you deliver to, and how did you know they got it?</b> Shape: name the audience the "
            "posting names, and what happened next.",
            "<b>Tell me about a time you disagreed with a stakeholder.</b> Shape: the evidence you brought, and "
            "what you did when you were overruled.",
        ]),
        ("h2", "Senior"),
        ("num", [
            "<b>Where do you set the boundary between what is asked for and what is right?</b> Shape: a decision "
            "rule you apply, not a principle you admire.",
            "<b>How do you decide whether to fix a pipeline or rebuild it?</b> Shape: cost, risk, frequency, and "
            "who is affected while it is down.",
            "<b>How have you raised the quality bar for a team?</b> Shape: one practice, adopted by others, with "
            "a measurable before and after.",
            "<b>What would you do in your first 90 days here?</b> Shape: what you would learn, from whom, and "
            "the first thing you would change. Never promise a reorganisation you cannot see yet.",
        ]),
        ("callout", "One habit covers all twelve: answer with the situation, the action, then the outcome as a "
                    "number or a change. The sample's postings measure everything else in counts; screeners hear "
                    "hundreds of answers that stop before the outcome."),
        ("h2", "Three questions to ask them"),
        ("num", [
            "<b>What does the successful candidate do in the first three months?</b> The answer tells you the "
            "level they are actually hiring at, which is the level the band is attached to.",
            "<b>Which requirement in the posting is hardest to fill?</b> The answer tells you where your "
            "specific tool or experience is worth naming twice.",
            "<b>What does the team do when the numbers disagree?</b> The answer tells you whether the data "
            "quality work this sample counts in 26 of 140 postings is someone's job or nobody's.",
        ]),
        ("p", "Ask those in the last five minutes, not the first five. If you ask them early the call becomes "
              "about you, and the screener's script expects to finish it in twenty minutes."),

        ("pb",),
        # ---------------- p24-27: section 07 ----------------
        ("h1", "07. Negotiation for the Canadian market"),
        ("p", "Canadian technical offers in this sample rarely arrive as a single salary. They arrive as a band, "
              "a level, and a variable component, and each of those is negotiable separately."),
        ("h2", "The five things that are actually negotiable"),
        ("num", [
            "<b>Placement in the band.</b> When a band is published, ask for the level you can evidence. Wide "
            "bands like $86,379 to $127,288 in this sample almost always mean a level is being placed inside.",
            "<b>Bonus and variable pay.</b> The sample includes a 3 to 5% performance bonus on a published grade "
            "band, and a 12% annual bonus on a $95,000 to $105,000 base. Ask what percentage is standard for "
            "the level, and what it has actually paid out recently.",
            "<b>Start date and review date.</b> A six-month review is often easier to grant than a higher base, "
            "and it moves your next raise forward by half a year.",
            "<b>Title.</b> Costs the employer little, and it sets the band you are placed in at your next move. "
            "Take the title before you take a sign-on you will not repeat.",
            "<b>Flexibility that is not money.</b> Remote days, professional development budget, certification "
            "support. The sample includes postings offering tuition reimbursement and certification pathways "
            "such as PL-300; if that is standard, it belongs in the conversation once, as part of the package.",
        ]),
        ("h2", "The counter, when the offer is below your number"),
        ("quote", "Thank you, I want the role. Based on [the requirement you meet] and the posted band of "
                  "[band], I was expecting [number]. Can we close the gap, or is there room in the bonus or the "
                  "review date?"),
        ("p", "Three properties make that counter work: it accepts the role first, it names evidence rather than "
              "need, and it offers the employer two ways to say yes without changing the base. A counter that "
              "names rent, a mortgage or a competing offer you do not hold is a bluff, and it is the fastest way "
              "to lose an offer you wanted."),
        ("h2", "Ask for the band in writing"),
        ("p", "Before you accept, ask for the band, the level, the bonus target and the review date in writing. "
              "This is a normal request in Canada and it protects both sides. If the band was published in the "
              "posting, compare the offer against the published range before you sign, and ask for the number "
              "in the context of the range they printed."),
        ("h2", "When not to negotiate"),
        ("bul", [
            "When the posting published a band and the offer is inside it with a level you can evidence. Ask "
            "about the review date, then accept.",
            "When the employer has stated the band is fixed, non-negotiable, or set by a collective agreement. "
            "In that case negotiate the title, the review date, or the start date, and do not reopen the base.",
            "When your only leverage is a competing offer you would not take. It reads, it is checked, and it "
            "costs you the role.",
        ]),
        ("h2", "Answering the offer email"),
        ("p", "Offers in this sample arrive as a band, a level and a bonus percentage, so the reply has to "
              "respond to the package rather than the base. Three lines:"),
        ("mono", "Thank you, I am pleased to accept the role in principle. Before I sign: the base of $[number] "),
        ("mono", "sits at [position] in the posted band of $[band]. Based on [the requirement you meet], I was "),
        ("mono", "expecting $[target]. Is there room on the base, the bonus percentage, or a six-month review?"),
        ("p", "Accepting in principle costs nothing and keeps the conversation open. Naming the band shows you "
              "read the posting. Offering three routes to yes means the answer can be yes without the base "
              "moving, which is usually what makes it yes."),
        ("h2", "A competing offer you actually hold"),
        ("p", "If you hold one, name it plainly, with no invented figure and no invented employer, and say which "
              "one you prefer and why. That sentence is worth more than any number: employers negotiate hardest "
              "for the candidate they believe will sign. Do not use an offer as a lever if you would not take "
              "it, and do not repeat it as a threat, because both are discovered at the same stage as an "
              "inflated work status."),
        ("callout", "The pattern behind all of it: the employer printed a range, a level and a bonus percentage, "
                    "which means the decision has already been made to be flexible inside a structure. Your job "
                    "in the negotiation is to place yourself inside that structure with evidence, not to argue "
                    "against it."),
        ("warn", "Nothing in this section is legal, financial or tax advice. Offers, contracts and minimum "
                 "standards vary by province and by employment type. For a contract you are unsure about, read "
                 "it with someone licensed to advise in your province."),

        ("pb",),
        # ---------------- p28-30: section 08 ----------------
        ("h1", "08. Reference"),
        ("h2", "The full measured keyword table"),
        ("p", "Postings out of the 140 readable, naming the term."),
        ("mono", "Excel 56 &nbsp; SQL 45 &nbsp; Python 44 &nbsp; Power BI 36 &nbsp; stakeholder 33 &nbsp; "
                 "statistics 32 &nbsp; data quality 26 &nbsp; R 18 &nbsp; machine learning 14 &nbsp; GCP 13 &nbsp; "
                 "Azure 13 &nbsp; Snowflake 13 &nbsp; Tableau 12 &nbsp; data warehouse 10 &nbsp; ETL 9 &nbsp; "
                 "AWS 9 &nbsp; data governance 8 &nbsp; regression 8 &nbsp; Power Automate 8 &nbsp; "
                 "dashboard 7 &nbsp; Power Query 7 &nbsp; Sigma 7 &nbsp; SAP 7 &nbsp; Agile 6 &nbsp; Git 6 &nbsp; "
                 "Databricks 6"),
        ("mono", "Salesforce 5 &nbsp; SAS 5 &nbsp; generative AI 5 &nbsp; KPI 5 &nbsp; SharePoint 5 &nbsp; "
                 "SPSS 4 &nbsp; DAX 4 &nbsp; TensorFlow 4 &nbsp; Microsoft 365 4 &nbsp; Jira 4 &nbsp; "
                 "Azure Data Factory 3 &nbsp; Spark 3 &nbsp; SQL Server 3 &nbsp; API 3 &nbsp; deep learning 3 &nbsp; "
                 "MySQL 3 &nbsp; JavaScript 3 &nbsp; BigQuery 3"),
        ("h2", "The question list"),
        ("p", "Every category that appeared in the 43 postings that published questions, with the count."),
        ("grid", ["Question", "Postings", "Answer lives in"], [
            ["Salary expectations", "27", "Section 05"],
            ["Work authorization or sponsorship", "12", "Section 03"],
            ["Years of experience", "10", "Section 02"],
            ["A completed degree", "6", "Section 02"],
            ["Technologies, by name", "6", "Page 6 of the free report"],
            ["Location or commuting distance", "5", "Section 02"],
            ["References or a background check", "4", "Section 02"],
            ["Accommodation requests", "3", "Section 02"],
            ["French proficiency", "2", "Section 02"],
            ["Start date or availability", "1", "Section 02"],
        ], [212, 60, 152]),
        ("h2", "The one-page checklist"),
        ("small", "Print this, or keep it on a second screen, and run it before every submission."),
        ("num", [
            "Every required field has an answer, and no answer contradicts a stated requirement.",
            "The posting's tools are named in your resume in the posting's spelling.",
            "Your most recent role's first bullet names the posting's first tool and what it produced.",
            "Salary: inside the published band, above the midpoint, with a reason. No 'negotiable'.",
            "Work authorization answered with your status and the fact that decides it.",
            "Years of experience identical everywhere it appears in the application.",
            "The technologies box is inside its character cap, with a level and one line of proof.",
            "The resume still reads as sentences after the keywords are in it.",
        ]),
        ("h2", "The 30-day tracker"),
        ("p", "Fill this in per application. The fourth column is the test from section 04: count the posting's "
              "named tools that appear in the resume you sent, in the posting's spelling."),
        ("grid", ["Posting", "Band published", "Salary answer given", "Tool matches"], [
            ["", "yes / no", "", "/10"],
            ["", "yes / no", "", "/10"],
            ["", "yes / no", "", "/10"],
            ["", "yes / no", "", "/10"],
            ["", "yes / no", "", "/10"],
            ["", "yes / no", "", "/10"],
            ["", "yes / no", "", "/10"],
            ["", "yes / no", "", "/10"],
        ], [230, 90, 130, 74]),
        ("small", "Two patterns to look for after ten rows: applications with no published band are where your "
                  "salary answer is doing the most work, and applications below ten tool matches are where the "
                  "parse had the least to read."),
        ("h2", "The sample, one more time"),
        ("bul", [
            "141 Canadian technical postings collected on 5 October 2026, 140 readable in full, 43 with the "
            "employer's own questions, 39 with the answer set, 53 scored against a fit rubric.",
            "Ontario-heavy: Toronto, Mississauga, Markham, Oakville, Burlington. Families skew to analytics, "
            "business intelligence, clinical data and operations analysis.",
            "Not a random sample and not a survey of employers. It is one applicant's pipeline, counted.",
        ]),

        ("pb",),
        # ---------------- p31: closing ----------------
        ("h1", "What this pack is not"),
        ("p", "It is a document. It is not a recruiter, not advice, and not a guarantee. It contains no "
              "endorsement from any employer and no placement result, because there are none to report. Every "
              "count in it comes from the 141 postings named above, and the method note travels with the file so "
              "that any number in it can be checked."),
        ("p", "If you find a number that is wrong, or a question shape this sample missed, write to the address "
              "on the page and it goes into the next revision. Corrections are worth more to this document than "
              "compliments are."),
        ("p", "The page: <font face='Courier'>%s</font>" % URL),
        ("small", "First Pass. Data collected 5 October 2026. Canada."),
    ],
}
