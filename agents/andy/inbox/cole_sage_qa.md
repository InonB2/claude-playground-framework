# QA Report — LinkedIn Posts (Hebrew)
**Reviewer:** Cole  
**Date:** 2026-05-08  
**Source file:** `owner_inbox/posts/linkedin_posts_refreshed.md`  
**Author:** Sage  
**Subject:** Inon Baasov — CPO-level Israeli tech executive, Hebrew LinkedIn posts

---

## Summary Verdict

3 posts PASS as-is. 2 posts have FLAGS requiring fixes before publishing.  
No post is disqualifying — the voice is generally strong and the Hebrew reads as native. The issues are targeted and correctable.

---

## פוסט 1 — הפיצ'ר שהרגנו

**STATUS: PASS**

The voice is clean and direct. The hook lands hard. The data point (34% vs. 8 minutes) is specific and credible. The emotional resolution — killing something the team believed in — reads as genuinely reflective, not performative humility. The CTA question is open and invites peer engagement.

No flags.

**Note for Inon:** The investors named (Paramount, JVP, Lionsgate) are accurate to his background — good specificity signal for credibility. Confirm the 34% uplift figure is a number Inon is comfortable attributing to TouchE publicly.

---

## פוסט 2 — כשה-AI מתחיל לזכור

**STATUS: FLAG**

The post is conceptually strong and the core insight (continuity over intelligence) is genuinely original. However, two phrases feel like translated English and one paragraph reads as technical documentation rather than a person speaking.

**Issues:**

- **"מס הקשרי" (contextual tax)** — the phrase "מס הקשרי" is a direct calque of the English "context tax." It is not a phrase Israeli tech professionals use naturally. It reads as translated jargon.
  - Original: `ה"מס הקשרי" של כל סשן חדש הולך וקטן, לא גדל`
  - Suggested fix: `העלות של "להסביר את עצמך מחדש" בכל סשן — הולכת וקטנה`

- **Bullet list tone** — The three-bullet paragraph (`דפוסים ומגבלות מועדפות לא נעלמים`, `החלטות פרויקט הופכות לידע`, `ה"מס הקשרי"...`) reads as a product spec, not a person talking. Israeli LinkedIn posts from senior tech leaders rarely use bullet lists mid-post. The flow breaks the conversational register.
  - Suggested fix: Fold into prose. Example: `בפועל: ההחלטות שקיבלתי נשמרות, הדפוסים מצטברים, וכל סשן חדש מתחיל ממה שנגמר — לא מאפס.`

- **"briefing מלא"** — mixing English noun into Hebrew is common in Israeli tech, but "briefing" here sits oddly next to the more formal Hebrew around it. 
  - Original: `agents מעבירים state אחד לשני בלי לעשות briefing מלא בכל פעם`
  - Suggested fix: `agents מעבירים state אחד לשני בלי לחזור על הכל מהתחלה`

---

## פוסט 3 — המסמך מת. יחי השיפוט.

**STATUS: FLAG**

The title is strong. The opening argument about documents as a skill is credible for a CPO voice. But the middle section has two problems: one phrase that is clearly translated English, and one sentence that is structurally awkward in Hebrew.

**Issues:**

- **"לטייט תוכן"** — "לטייט" is a phonetic transliteration of "to tighten" — not used in Israeli Hebrew. This is a direct translation artifact. The word has no natural Hebrew equivalent in this context and will read as off to any Israeli professional.
  - Original: `ניסיתי AI שלא רק עוזר לטייט תוכן`
  - Suggested fix: `ניסיתי AI שלא רק מסייע לחדד ולסדר תוכן`

- **"לא אאוטליינים. לא בולטים. הדליברבל עצמו."** — "אאוטליינים" (outlines) and "הדליברבל" (deliverable) in the same two-word burst is a lot of English-as-Hebrew in a row. One English term in a punchy list is a stylistic choice; two back-to-back reads as lazy transliteration.
  - Original: `לא אאוטליינים. לא בולטים. הדליברבל עצמו.`
  - Suggested fix: `לא טיוטות. לא כיווני כתיבה. הפלט המוכן עצמו.`

**Note:** The closing thought — "שיפוט. הקשר. רף גבוה." — is excellent. Very natural rhythm in Hebrew. Keep exactly as-is.

---

## פוסט 4 — Gemini Files

**STATUS: PASS**

This is the most naturally written post in the set. The story is concrete (receipts, QuickBooks, pie chart), the voice stays personal throughout, and the conclusion — "השיפוט הזה הוא העבודה עכשיו" — lands cleanly without over-explaining. The CTA is specific and invites direct practical engagement.

No flags.

**Note for Inon:** Post 3 and Post 4 are thematically very close — both argue that "the document is now a byproduct" and "judgment is the real skill." If publishing both, consider spacing them 2–3 weeks apart or differentiating the angle more clearly. Post 4 is the stronger of the two due to the concrete story.

---

## פוסט 5 — Ghost.build

**STATUS: PASS**

The technical detail is appropriate for the developer/CPO audience segment and the narrative arc (problem → experiment → result → mental shift) is well-structured. The Hebrew reads naturally, the English technical terms (fork, benchmark, materialized view, quarantine) are exactly what an Israeli engineer would actually write — no over-translation, no awkward calques. The closing CTA ("שווה לנסות אם אתם בונים משהו עם agents כרגע") is peer-to-peer and appropriately low-pressure.

No flags.

**Note for Inon:** This post names a specific tool (Ghost.build) and includes free-tier specs. If this is promotional or sponsored content, Israeli LinkedIn norms and platform policy require disclosure. If it is organic recommendation, it is fine as-is.

---

## Overall Notes Before Publishing

1. **Post 2 and Post 3** require the targeted fixes above before going live. Neither requires a full rewrite — surgical edits only.
2. **Posts 1, 4, and 5** are ready to publish as written.
3. The voice is consistently first-person, appropriately mixes Hebrew and English tech terms at the register a senior Israeli tech executive would use, and avoids the most common AI-generation tells (over-formal sentence structure, passive constructions, absence of opinion).
4. The set as a whole skews heavily toward AI productivity content (Posts 2–5). If Inon's goal is to establish CPO-level product leadership positioning, Post 1 is the anchor piece and should likely go first in the publishing schedule.
