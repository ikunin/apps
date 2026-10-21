# /appsite-legal — Terms of Use and Privacy Policy for an app's site

The legal pages live in the app's appsite (`appstore/site_text_terms.py`,
`appstore/site_text_privacy.py`, `appstore/site_text_ai.py`, the other ten
languages in `appstore/translations/<code>.json`, rendered by
`appstore/make_site_legal.py`, published by `vendor/appsite/publish.py`). No
appsite yet? Run `/appsite` first.

The work is not "write a legal page". It is: **every sentence true for this
app today, nothing Apple's agreement covers left uncovered, nothing a court
would strike, nothing that scares a customer more than it must** — in eleven
languages that say the same thing.

Learned on JustTalk (21 Oct 2026); the reasoning lives in its
`docs/compliance/terms-review.md`.

## 0. Scope, before a word

- **Which platforms are on sale?** Only those go in. A platform not on sale
  (JustTalk's Windows) is left out of the terms entirely and named once as
  "not covered until it is on sale". A sold-out-of-store platform (a licence
  key, not Apple) needs its own complete terms — Apple's EULA does not reach it.
- **Who is the licensor?** Name and address from the Impressum block in
  `appstore/site_config.py`. Its country decides the consumer law that bites
  (Germany → §§ 305 ff., 307, 309 No. 7 BGB).
- **Governing law is the human's decision.** Draft the obvious default (the
  licensor's country, EU consumers keeping their home protections, merchants
  at the licensor's courts), and say on the approval page that it is a default
  to confirm.

## 1. Inventory the facts from the code — not from memory, not from the template

Each line below becomes a sentence somewhere; each must be checked in the repo.

| Fact | Where to read it |
|---|---|
| Trial length, free limits, what Pro unlocks | the licensing spec (`shared/spec/licensing.json` `trial.*`), the `ProFeature` enum |
| One-time or subscription; Family Sharing | `fastlane/iap/*.json` (`familyShareable`), `appstore/purchase_records.json` |
| Separate purchases per platform | the IAP product ids per record |
| What is stored, where, how long | the store / library code, keep rules, Recently deleted |
| What leaves the device, to whom | every network call: AI services, Apple services, model downloads, link previews, connections (Slack, Teams, webhooks, Todoist, calendars) |
| Consent before sending | the consent gate (JustTalk: `AIConsent`) |
| Locks, encryption, recovery | the lock format; what happens when the recovery secret is lost |
| Data the developer can receive | support email, licence requests — and Apple's opt-in crash reports (the app may have no crash reporter, Apple can still share) |
| AI output marking, high-risk scope | the AI statement, the EU AI Act notes |
| UI labels the text quotes | `shared/i18n/<code>.json` — the **app's own word in each language** ("Open-source licenses", not "Acknowledgements"; Russian «Твои слова» even in a formal text) |

Write the inventory down first. A sentence the inventory cannot back does not
go in.

## 2. Map Apple's agreement — every clause answered

Read Apple's Standard EULA live (it changes): `WebFetch
https://www.apple.com/legal/internet-services/itunes/dev/stdeula/` and ask for
every clause a–i with its scope. Then fill the table in
`./apple-eula-map.md`: each Apple clause either applies as written (say so in
one sentence: "Every other clause of the EULA — among them export restrictions
and United States Government end users — applies as written") or has a clause
of ours. Add Apple's **minimum terms for a developer EULA** (also in the map):
Apple not responsible, developer responsible for support and claims,
developer name/address/contact, third-party terms, Apple a third-party
beneficiary.

## 3. Write the terms as one numbered list

Shape that worked (JustTalk, 20 sections): who · Apple's licence agreement ·
what you may do · trial, free version and Pro · purchases, Family Sharing,
refunds · your content and notes · AI services and who pays · results depend
on models and instructions · other services you connect · lawful use (incl.
export) · high-risk uses and publishing AI text · what the apps send · updates
and availability (incl. TestFlight) · statutory rights, no further warranty ·
liability · ending · governing law and disputes · severability · changes ·
contact.

Data shape: `'sections': [[heading, paragraph-html], …]`, placeholders the
renderer fills (`{impressum} {eula} {media} {refund} {privacy} {ai} {support}
{contact}`), rendered by a loop (`subheading(f"{n}. {title}")`,
`p(text.format(**links))`). One list means one shape-check for translations
and no per-platform parts to drift.

Tone rules — reassuring, still binding:
- Say a limit as a choice the user has: "The model you choose, and the mode or
  action you use, decide how accurate, polished and fast … — change either any
  time." Then the legal sentence: "We do not develop, train, operate or control
  these models … not responsible … as far as the law allows."
- `<strong>` only on what protects the user: one-time purchase, you are the
  provider's customer, back up what matters, AI makes mistakes.
- An intro line: "where a sentence limits what we owe you, it says so plainly."
- Never "fully compliant" (unprovable); "made to the transparency rules".

Clauses that must be in the EU-safe form (German law; also safe elsewhere):
- **Warranty**: "If you are a consumer, your statutory rights — including the
  legal guarantee for digital products — are not affected. Beyond them …" A
  bare "no warranty" is void for EU consumers.
- **Liability**: unlimited for intent, gross negligence, life/body/health,
  product liability law, and wherever law forbids a limit; slight negligence
  only for essential obligations ("one that makes the agreement possible at
  all and on which you may rely"), limited to typical, foreseeable damage;
  otherwise excluded — name the app's real risks (data not backed up; results,
  availability and charges of services the user chose). Also for anyone
  acting for us.
- **A cap at the price — only outside EU consumers.** The owner will ask for
  "liability limited to the app's price". For EU/EEA/CH consumers it fails:
  the unlimited cases cannot be capped, a cap below the typical foreseeable
  damage fails § 307 BGB, and an invalid standard-terms clause falls *whole*
  (no reduction to the valid part) — an aggressive cap can leave unlimited
  statutory liability. Add the cap as its own sentence for everyone else:
  "If you are not a consumer living in the EU, EEA or Switzerland, or you use
  the apps for your business, our total liability for slight negligence is
  limited to the price you paid, or 50 US dollars if that is more; the
  unlimited cases stay unlimited." Needed because a "these terms apply where
  they differ" sentence otherwise replaces Apple's own $50 cap for them too.
- **Withdrawal / refunds**: Apple's Media Services Terms govern withdrawal;
  Apple decides refunds (reportaproblem.apple.com).
- **Prices change**; a change never touches a purchase made. **Free limits
  may change**; never what the paid unlock unlocks.
- **Disputes**: German law excl. CISG; EU/EEA/CH consumers keep home
  protections and courts; merchants → licensor's city; VSBG § 36 statement
  ("neither obliged nor willing … consumer arbitration board"). No EU ODR link
  (the platform closed July 2025).
- **Changes to the terms**: announced with the release that brings them (a
  silent "by using you accept" is weak against consumers).

## 4. The privacy policy — the master text every surface repeats

`site_text_privacy.py` is the master: the in-app "Your data & AI" page, store
descriptions and review notes say the same. For each feature in the inventory:
what is stored, where, how long, what leaves, to whom, under whose terms, how
to turn it off, and what Privacy Mode changes. New feature → new `list_keep`
item (JustTalk added "Asking your notes": index on the device, a locked
folder's index encrypted like the folder, only the passages that answer the
question go to the user's service). Bump `updated` in every language. The AI
statement's `list_data` gets the same line ("your question and the passages
that answer it").

## 5. Three adversarial rounds — then fix, then translate

Run them yourself (no subagent fan-out; one careful pass each). The rounds
and the findings that recur are in `./review-rounds.md`. Write findings into
the repo (`docs/compliance/terms-review.md`: #, finding, fix) — it is the
reasoning a later change must respect, and the approval page shows it.

## 6. Eleven languages

- Write all ten from the final English, one JSON per language in the
  scratchpad, then merge into `translations/<code>.json` keeping each
  language's existing `title`/`h`.
- **Formal address in legal text**: Russian «вы», Ukrainian «ви» (the human's
  rule — informal is not appropriate in terms or privacy). French vous,
  Greek εσείς, Japanese/Korean polite are already formal. German du /
  Spanish tú / Italian tu: match the site unless the human asks; flag it.
- Quote UI labels exactly as the app shows them in that language, even when
  the app's word is informal.
- Link texts are inserted mid-sentence: inflect the link text for the slot
  (Russian `согласно {eula}` → dative «Стандартному лицензионному
  соглашению…»; `в {impressum}` → «выходных данных»).
- Verify mechanically before merging: same section count; each section's
  placeholder set and `<strong>` count equal to the English; no informal
  pronouns left (regex per language, the quoted UI labels excepted).

## 7. Check, approve, publish

```sh
make site                      # renders all eleven
python3 appstore/check_site.py # links, alt text, listing URLs, field limits
make check                     # includes check_claims: purchase wording
```

`check_claims.py` fails a text that talks about buying (stems: kauf, achat,
compra, unlock, pro …) and several platforms without one sentence naming the
devices and saying the records are separate. German "verkauft" in "who sells
the app" trips it: say "vertrieben" (distributed) there.

Then the approval page (the app's review artifact, or a new one via the
artifact-design rules): the full English text, the findings table, the
decisions left to the human (governing law; a lawyer's read before launch).
**Do not publish before the human approves.**

After approval:

```sh
git add -- appstore/site_text_*.py appstore/make_site_legal.py appstore/translations/*.json docs/compliance/terms-review.md site
git commit   # no attribution trailers
python3 vendor/appsite/publish.py --app <slug> --site site --dry-run   # touches only <slug>/ + root index/impressum
python3 vendor/appsite/publish.py --app <slug> --site site
curl -sfo /dev/null -w '%{http_code} %{url_effective}\n' https://ikunin.github.io/apps/<slug>/terms.html https://ikunin.github.io/apps/<slug>/ru/privacy.html
```

`git push` of the app repo does **not** publish the site; `publish.py` does.

## 8. Report

Five lines: what changed (sections, languages), the review findings count,
checks green, what is published (or waiting for approval), and the decisions
still the human's.
