# /appsite-legal — Terms of Use and Privacy Policy for an app's site

The legal pages live in the app's appsite: `appstore/site_text_terms.py`,
`appstore/site_text_privacy.py` (and `site_text_ai.py` where the app uses AI),
the other ten languages in `appstore/translations/<code>.json` (or inline,
depending on the app), rendered by `appstore/make_site_legal.py`, published by
`vendor/appsite/publish.py`. No appsite yet? Run `/appsite` first. Read the
kit's `AGENTS.md` before touching anything.

The work is not "write a legal page". It is: **every sentence true for this
app today, nothing Apple's agreement covers left uncovered, nothing a court
would strike, nothing that scares a customer more than it must** — in eleven
languages that say the same thing.

Two rules from the kit that this skill exists to keep:
- **Never copy a privacy or terms sentence from one app to another**, nor a
  section from JustTalk's terms (the worked example). Every app collects,
  sends and sells something different; a copied claim is a false statement.
- **A change to the kit lands on every app.** A renderer change belongs in the
  kit only after every app re-renders byte-identically (`make site` in each,
  `git diff --stat site/`).

Learned on JustTalk (21 Oct 2026; reasoning in its
`docs/compliance/terms-review.md`).

## 0. Scope, before a word

- **Which platforms are on sale?** Only those go in. A platform not on sale is
  left out and named once: "not covered until it is on sale". A platform sold
  outside Apple (a licence key) needs complete terms of its own — Apple's EULA
  does not reach it.
- **Who is the licensor?** Name and address from the `impressum` block in
  `appstore/site_config.py`. Its country decides the consumer law (Germany →
  §§ 305 ff., 307, 309 No. 7 BGB).
- **Decisions that are the human's**, asked once, early, with AskUserQuestion
  and a recommended default: governing law and courts (default: the licensor's
  country, EU/EEA/CH consumers keeping home protections, merchants at the
  licensor's city); the form of address where the site is informal (default:
  formal in legal text — "informal wording would not be appropriate in this
  context", the owner's words about Russian, 21 Oct 2026).

## 1. Inventory the facts from the code — not from memory, not from the template

Write a fact sheet first (scratchpad). Each fact gets the file it was read
from. A sentence the sheet cannot back does not go in. Find these in *this*
app (JustTalk's places in brackets, as examples only):

| Fact | Where to look |
|---|---|
| Trial, free limits, what the paid unlock unlocks | the licensing config and its feature gate (JustTalk: `shared/spec/licensing.json` `trial.*`, the `ProFeature` enum) |
| One-time or subscription; Family Sharing; separate records per platform | `fastlane/iap/*.json` or `*.storekit` (`familyShareable`), `appstore/purchase_records.json` |
| What is stored, where, for how long, how it is deleted | the persistence code, retention and purge rules |
| Everything that leaves the device, to whom, when | every network call: AI services, Apple services, downloads, previews, integrations |
| Consent before sending to a third party (AI or not) | the consent gate, and where it can be revoked |
| Encryption, locks, recovery — and what happens when a secret is lost | the crypto / lock code |
| What can reach the developer | support email, licence requests; **Apple's opt-in crash reports and analytics shared with developers** (true even when the app has no crash reporter — App Store Connect shows whether any arrive) |
| Third-party code and content licences | the app's acknowledgements list |
| AI output marking and high-risk scope (AI apps) | the AI statement, the EU AI Act notes |
| Age rating, children | App Store Connect, `site_config` |
| The words the text quotes | `shared/i18n/<code>.json` or the app's catalogs — **the app's own label in each language** (JustTalk: "Open-source licenses", not "Acknowledgements") |
| What the App Privacy label and `PrivacyInfo.xcprivacy` declare | both — the policy must agree with them |

## 2. Map Apple's agreement — every clause answered

`WebFetch https://www.apple.com/legal/internet-services/itunes/dev/stdeula/`
(it changes) and ask for every clause a–i with its scope. Fill the table in
`./apple-eula-map.md` for this app: each Apple clause either applies as
written (one sentence names those) or has a clause of ours. Add Apple's
minimum terms for a developer EULA and the App Review guidelines on privacy
(both in the map).

## 3. Draft the English terms — shaped by this app

A numbered list of sections is the shape that worked: one list means one
shape-check for translations and no per-platform parts to drift. JustTalk's
renderer (`appstore/make_site_legal.py` `terms()`: `'sections': [[heading,
html], …]`, placeholders `{impressum} {eula} {media} {refund} {privacy} {ai}
{support} {contact}`, `subheading(f"{n}. {title}")`) is not in the kit yet;
copy it into the app, or move it into the kit under the rule above. The kit
template's keyed shape (`p_eula`, `h_purchases`, …) still works for a simple
app — the content rules below matter, not the shape.

Sections, **only those the fact sheet supports** (JustTalk's 20 are a
checklist, not a template): who · Apple's licence agreement · what you may do
· free version and paid unlock · purchases, Family Sharing, refunds · your
content and data · third-party services the user chooses and who pays ·
quality depends on the user's choices (AI apps) · connected services ·
lawful use (incl. export) · high-risk uses and publishing AI text (AI apps) ·
what the app sends · updates and availability (incl. TestFlight) · statutory
rights, no further warranty · liability · ending · law and disputes ·
severability · changes · contact.

Tone — reassuring, still binding:
- A limit said as the user's choice, then the binding sentence ("The model you
  choose … decide how accurate … — change either any time." / "We do not …
  control these models … not responsible … as far as the law allows").
- `<strong>` only on what protects the user (one-time purchase, you are the
  provider's customer, back up what matters, AI makes mistakes).
- Intro: "where a sentence limits what we owe you, it says so plainly."
- Never "fully compliant" or any promised legal outcome.

Clauses in the EU-safe form (German law; safe elsewhere):
- **Warranty**: statutory rights — incl. the legal guarantee for digital
  products — unaffected; beyond them "as they are and as available". A bare
  "no warranty" is void for EU consumers.
- **Liability**: unlimited for intent, gross negligence, life/body/health,
  product liability law and wherever law forbids a limit; slight negligence
  only for essential obligations, limited to typical, foreseeable damage;
  otherwise excluded, naming the app's real risks. Also for anyone acting for
  us.
- **A cap at the price — only outside EU consumers.** For EU/EEA/CH consumers
  it fails (the unlimited cases cannot be capped; a cap below foreseeable
  damage fails § 307; an invalid standard-terms clause falls *whole*, leaving
  unlimited statutory liability). As its own sentence for everyone else: "If
  you are not a consumer living in the EU, EEA or Switzerland, or you use the
  apps for your business, our total liability for slight negligence is limited
  to the price you paid, or 50 US dollars if that is more; the unlimited cases
  stay unlimited." Needed whenever the terms say "these terms apply where they
  differ from the EULA" — that sentence otherwise drops Apple's $50 cap.
- **Withdrawal / refunds**: Apple's Media Services Terms govern withdrawal;
  Apple decides refunds (reportaproblem.apple.com).
- **Prices change** without touching a purchase made; **free limits may
  change**, never what the paid unlock unlocks.
- **Disputes**: the chosen law excl. CISG; EU/EEA/CH consumers keep home
  protections and courts; merchants → the licensor's city; the VSBG § 36
  statement (German licensor); no EU ODR link (the platform closed July 2025).
- **Changes**: announced with the release that brings them; bump `updated`.
- Flag for the lawyer, do not decide: the kit's "the English version governs"
  line on translations, against consumers who read only their language.

## 4. Draft the English privacy policy — the master text

`site_text_privacy.py` is the master: the in-app privacy page, the store
descriptions and the review notes repeat it. Walk `./privacy-checklist.md`
(GDPR Art. 13, Apple 5.1.1/5.1.2, the App Privacy label) against the fact
sheet. Each feature: what is stored, where, how long, what leaves, to whom,
under whose terms, how to turn it off or delete it, what a privacy mode
changes. A new feature gets its own item (JustTalk's "Asking your notes":
index on the device, a locked folder's index encrypted like the folder, only
the passages that answer go to the user's service); an AI app's AI statement
gets the same line. Bump `updated`.

## 5. Adversarial rounds on the English — then the approval page

Run the rounds in `./review-rounds.md` yourself, one careful pass each — no
subagent fan-out (the owner pays for tokens). Log every finding in the app
repo (`docs/compliance/terms-review.md`: #, finding, fix); it is the reasoning
a later change must respect.

Then **the approval page, English only**: the full terms, the privacy
changes, the findings table, and the open decisions (law, address form, a
lawyer's read before launch). Do not translate before the English is
approved — every later wording change would be made eleven times.

## 6. Eleven languages — after approval

- Write the ten from the approved English, one JSON per language in the
  scratchpad, then merge, keeping each language's existing `title`/`h`.
- **Formal address** (unless the human chose otherwise): Russian «вы»,
  Ukrainian «ви», German «Sie», Spanish «usted», Italian «Lei», Portuguese
  (Brazil) «você» in a neutral legal register, French «vous», Greek «εσείς», Japanese/Korean polite.
- Quote UI labels exactly as the app shows them, even when the app's word is
  informal (Russian «Твои слова» inside a formal text).
- Inflect link texts for their slot (Russian `согласно {eula}` → dative;
  `в {impressum}` → «выходных данных»); a Japanese/Korean list joins with `、`.
- Verify mechanically: same section/key count; each paragraph's placeholder
  set and `<strong>` count equal to the English; no informal pronouns left
  (per-language regex, quoted labels excepted).

## 7. Check

```sh
make site                                              # renders all eleven
python3 appstore/check_site.py                         # links, alt text, listing URLs, field limits
python3 vendor/appsite/check_text.py --texts appstore  # wrong-script characters, another app's vocabulary
make check                                             # where the app has it: check_claims (purchase wording)
```

`check_claims.py` fails a text that mentions buying (stems: kauf, achat,
compra, unlock, pro …) and several platforms without one sentence naming the
devices and saying the records are separate. German "verkauft" ("who sells
the app") trips it: "vertrieben".

**Consistency**: for each fact that changed (a retention period, "no crash
reporter", consent, what leaves the device), grep the store descriptions
(`fastlane/metadata*/**/description.txt`, review notes) and the app's own
privacy strings; anything that now disagrees is fixed in the same change or
named in the report.

## 8. Publish

```sh
git add -- appstore/site_text_*.py appstore/make_site_legal.py appstore/translations/*.json docs/compliance/terms-review.md site
git commit                                                   # no attribution trailers
python3 vendor/appsite/publish.py --app <slug> --site site --dry-run
```

Read the dry run: it must touch only `<slug>/` and the root index/impressum.
**`publish.py` publishes the whole `site/` folder** — the landing page,
screenshots and store-derived text with it. List what changed beyond the
legal pages (`git diff --stat <last published>..HEAD -- site/` or the dry
run's file list) and say so before publishing; unapproved marketing text goes
live otherwise. Then:

```sh
python3 vendor/appsite/publish.py --app <slug> --site site
until curl -s https://ikunin.github.io/apps/<slug>/terms.html | grep -q '<a phrase new in this change>'; do sleep 5; done
```

`git push` of the app repository does **not** publish the site.

## 9. Report

Five lines: what changed (sections, languages), findings count, checks green,
what is live (or awaiting approval), and the decisions still the human's.
