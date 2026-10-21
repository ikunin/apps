# Three adversarial rounds

Read the full draft once per round, as that reader, and write every finding
as `# | finding | fix`. Apply all fixes before translating.

## Round 1 — Apple (App Review and Apple's legal)

Walk `apple-eula-map.md` row by row. Typical misses:
- US Government end users and export not mentioned at all.
- No "Apple is not responsible / third-party beneficiary" paragraph.
- No reservation of rights in the app's name and design.
- Nothing against bypassing the free version's limits or the purchase check.
- "Information is for general information only" missing for AI output.
- A specific statute named too narrowly ("Product Liability Act" → "product
  liability law", software is covered by the new EU directive).
- Prices, "free", or another app's name in anything the store shows.

## Round 2 — a consumer-protection lawyer (EU / German standard-terms law)

- "No warranty" → void for consumers: keep statutory rights, limit only the rest.
- Blanket liability exclusion → void (§ 309 No. 7, § 307 BGB): the German form.
- Right of withdrawal: who handles it (Apple's Media Services Terms).
- Price changes vs. buyers at the old price.
- Free-limit changes that could look like taking back what was paid for.
- One-sided changes to the terms by "continued use".
- Merchants' place of jurisdiction; VSBG § 36 statement; no ODR link (gone).
- "Fully compliant" or any guarantee of a legal outcome.

## Round 3 — an unhappy customer (lost notes, a large bill, a bad transcript)

- "We never receive your content" — false if they email support; Apple's
  opt-in crash reports exist even with no crash reporter in the app.
- "Kept on your devices — nowhere else" contradicting the AI-service and
  connection sections.
- A locked folder with a lost recovery password: say nobody can open it.
- "Asks before anything goes to a cloud service" — but link previews and
  connections are not AI services: say "cloud AI service".
- A provider bill caused by an app fault: liability for essential
  obligations stays (fair); the provider's spending limit is the user's tool.
- A platform not on sale still mentioned.
- A UI label that is not the app's real label in that language.
- The privacy policy and the terms disagreeing on any fact (check both, and
  the store descriptions, which repeat the master text).

## Recurring language traps

- German "verkauft" trips `check_claims` (buying + several platforms): use
  "vertrieben".
- Russian/Ukrainian: formal «вы»/«ви» in legal text; inflect link texts for
  their slot; quote app labels as the app writes them.
- Japanese/Korean: one `、`-separated list — insert into `sum_*` summaries by
  the language's own separator, not ", ".
