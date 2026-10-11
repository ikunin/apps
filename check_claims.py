#!/usr/bin/env python3
"""Check the words that claim WHAT A PURCHASE COVERS against how the app is actually sold.

`check_text.py` finds wrong scripts and another app's vocabulary; nothing in it checks a fact. SpeedyCards
published "One purchase … on iPhone, iPad, Mac, Apple TV and Apple Watch" in eleven languages although its Mac
and Apple TV apps are separate App Store records with their own purchases (11 Oct 2026); JustTalk's tagline
"unlocked with one purchase. Mac, Windows, iPhone and iPad" says the same untrue thing.

A purchase never crosses a store record, so the fact is the list of records and the devices each one runs on.
The app declares it in one small file, and the Fastfile keeps it honest (every `app_id:` there must be a record):

    appstore/purchase_records.json
    { "records": { "io.github.ikunin.SpeedyCardsApp": ["iPhone", "iPad", "Apple Watch"],
                   "io.github.ikunin.osx.SpeedyCards": ["Mac"],
                   "io.github.ikunin.SpeedyCards":     ["Apple TV"] },
      "accepted": ["terms.p_free"] }

`accepted` names texts (by their key, in every language) that a person read and found TRUE although the word
lists cannot tell — a sentence about how each platform is sold, say. It is the audit trail, not a way round.

The rule: a text that talks about buying AND about several platforms (device names that sit in different
records, or "every device" / "all platforms" / "five platforms") must, in one sentence, name EVERY record's
devices and say they are separate. Device names are Apple's and Microsoft's and are not translated, so one
rule reads all eleven languages; the word lists below are the translated part. An app with a single record
cannot make this claim and passes trivially.

    python3 vendor/appsite/check_claims.py --texts appstore --records appstore/purchase_records.json \\
        [--also 'fastlane/metadata*/*/*.txt' --also docs/press-kit.md --also 'Shared/*.lproj/Localizable.strings']
"""
import argparse
import glob
import json
import os
import re
import sys

#: How each device is written in a text. ASCII look-arounds, not \b: a Hangul or kana particle follows "Mac".
DEVICE_PATTERNS = {
    "iPhone": r"iphone",
    "iPad": r"ipad",
    "Apple Watch": r"watch",
    "Mac": r"(?<![a-z])mac(?![a-z])|macos",
    "Apple TV": r"apple[\s ]*tv|tvos",
    "Vision Pro": r"vision[\s ]*pro|visionos",
    "Windows": r"windows",
}

#: Words that mean buying / unlocking, in the eleven languages (stems).
PURCHASE = re.compile(
    r"purchas|\bbuy|bought|unlock|\bpro\b|kauf|freischalt|erwerb|achat|achet|débloqu|compra|desbloque|acquist|sblocc|"
    r"購入|買|解除|アンロック|구매|구입|잠금|покупк|купи|купл|разблок|придб|розблок|αγορ|ξεκλειδ", re.I)

#: "Every device" / "all platforms" / "five platforms" without naming any: a quantifier, up to two words, the noun.
_GAP = r"\W+(?:\w+\W+){0,2}?"
EVERYWHERE = re.compile("|".join([
    r"(every|all|any|each|five|5)" + _GAP + r"(devices?|platforms?)",                                    # en
    r"(jede[mnrs]?|alle[nr]?|fünf)" + _GAP + r"(ger[äa]te?|plattform)",                                  # de
    r"(chaque|tou[st]e?s?|cinq)" + _GAP + r"(appareils?|plateformes?)",                                  # fr
    r"(cada|tod[oa]s|cinco)" + _GAP + r"(dispositivos?|aparelhos?|plataformas?)",                        # es, pt
    r"(ogni|tutti|cinque)" + _GAP + r"(dispositiv[oi]|piattaform[ae])",                                  # it
    r"(どの|すべての|全|[5五]つの)\s*(apple\s*)?(デバイス|機種|プラットフォーム)",                                  # ja
    r"(모든|5개|다섯)\W*(apple\W*)?(기기|플랫폼)",                                                        # ko
    r"(всех|каждом|пяти|пять)" + _GAP + r"(устройств|платформ)",                                          # ru
    r"(усіх|кожному|п.яти|п.ять)" + _GAP + r"(пристро|платформ)",                                        # uk
    r"(όλες|όλων|κάθε|πέντε)" + _GAP + r"(συσκευ|πλατφόρμ)",                                             # el
]), re.I)

#: "separate", in the eleven languages. Words that also mean ownership ("own", "propre") are NOT here:
#: "what you already own" must not pass for it.
SEPARATE = re.compile(
    r"separate|independient|independent|\b(its|their) own\b(?:\W+\w+){0,2}?\W+(purchase|licen[cs]e)|separat|separad|gesondert|getrennt|"
    r"eigene[nm]? Kauf|séparé|distinct|propre achat|compra propia|compra própria|propi[oa] acquisto|"
    r"acquisto propri|独立|別々|別途|別の購入|個別に|별도|따로|отдельн|раздельн|окрем|відокрем|χωριστ|ξεχωριστ|"
    r"δική της αγορά|own licen[cs]e|"
    r"carry over|carry across|nicht übertragen|übertrag\w* sich nicht|ne se transf|ne s.appliquent pas|no se (trasladan|transfieren)|"
    r"non si trasfer|non valgono|não (se )?transfer|não valem|引き継がれ|引き継げ|とは別|別の|별개|이어지지|이전되지|"
    r"не переносятся|не переходят|не переносяться|δεν μεταφέρ", re.I)

SENTENCES = re.compile(r"(?<=[.!?。！？;])\s*")
#: A sentence that asks: "?" in most languages, ";" in Greek, "…ですか。" in Japanese.
QUESTION = re.compile(r"[?？;]$|(ですか|ますか|でしょうか)[。？]?$")


def devices_named(text):
    low = text.lower()
    return {device for device, pattern in DEVICE_PATTERNS.items() if re.search(pattern, low)}


def _says_separate(sentence, records):
    """A sentence that names two or more records' devices AND says they are separate: an honest separation."""
    named = devices_named(sentence)
    return sum(1 for devices in records.values() if named & set(devices)) > 1 and bool(SEPARATE.search(sentence))


def verdict(text, records):
    """None if the text is fine, else why not."""
    text = " ".join(s for s in SENTENCES.split(text) if not QUESTION.search(s.rstrip()))   # a question claims nothing
    if len(records) < 2 or not PURCHASE.search(text):
        return None
    named = devices_named(text)
    scopes_named = {rec for rec, devices in records.items() if named & set(devices)}
    if not (len(scopes_named) > 1 or EVERYWHERE.search(text)):
        return None
    if any(_says_separate(sentence, records) for sentence in SENTENCES.split(text)):
        return None
    return ("talks about buying across platforms without a sentence that names the devices and says the "
            f"records are separate ({'; '.join('/'.join(d) for d in records.values())})")


def load_records(path, fastfile="fastlane/Fastfile"):
    """(records, accepted): the declared records, refused if a device is unknown or the Fastfile sells a record
    that is not declared, and the keys a person has accepted."""
    with open(path, encoding="utf-8") as handle:
        declared = json.load(handle)
    records, accepted = declared["records"], set(declared.get("accepted", ()))
    for record, devices in records.items():
        unknown = set(devices) - set(DEVICE_PATTERNS)
        if unknown:
            raise SystemExit(f"{path}: {record}: unknown device(s) {sorted(unknown)} — one of {sorted(DEVICE_PATTERNS)}")
    if os.path.isfile(fastfile):
        with open(fastfile, encoding="utf-8") as handle:
            sold = set(re.findall(r'^\s*app_id:\s*"([^"]+)"', handle.read(), re.M))
        missing = sold - set(records)
        if missing:
            raise SystemExit(f"{fastfile} sells {sorted(missing)} which {path} does not declare: "
                             f"add the devices each runs on")
    return records, accepted


# --- where the texts live -----------------------------------------------------------------------------------

def _paragraphs(path):
    with open(path, encoding="utf-8") as handle:
        for number, block in enumerate(re.split(r"\n\s*\n", handle.read()), 1):
            yield f"{path} ¶{number}", block


def _strings_values(path):
    with open(path, encoding="utf-8") as handle:
        for key, value in re.findall(r'^"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)";', handle.read(), re.M):
            yield f"{path} {key}", value


def _json_values(path, prefix=""):
    """Every string in a JSON file (an app that keeps its translations as data, not as Python tables)."""
    def walk(node, where):
        if isinstance(node, str):
            yield f"{path} {where}", node
        elif isinstance(node, dict):
            for key, value in node.items():
                yield from walk(value, f"{where}.{key}" if where else key)
        elif isinstance(node, list):
            for number, value in enumerate(node):
                yield from walk(value, f"{where}[{number}]")
    with open(path, encoding="utf-8") as handle:
        yield from walk(json.load(handle), prefix)


def _read(path):
    if path.endswith(".strings"):
        return _strings_values(path)
    return _json_values(path) if path.endswith(".json") else _paragraphs(path)


def texts(directory, also):
    import check_text   # the kit's own, next to this file
    for file, language, key, text in check_text.tables(directory):
        yield f"{directory}/{os.path.basename(file)} [{language}] {key}", text
    for pattern in also:
        for path in sorted(glob.glob(pattern)):
            yield from _read(path)


def _key(where):
    """The text's own key, without its file, language or list position: 'terms.p_free', 'p_free', 'faq_all'."""
    return re.sub(r"\[\d+\]", "", where.split(" ")[-1])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--texts", default="appstore", help="directory of site_text_*.py / make_site_translations.py")
    parser.add_argument("--records", default="appstore/purchase_records.json")
    parser.add_argument("--also", action="append", default=[], help="more files (glob): listing, docs, .strings, .json")
    args = parser.parse_args(argv)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isfile(args.records):
        raise SystemExit(f"{args.records} is missing: declare each store record and the devices it runs on")
    records, accepted = load_records(args.records)
    bad = [(where, why) for where, text in texts(args.texts, args.also)
           if _key(where) not in accepted and (why := verdict(text, records))]
    for where, why in bad:
        print(f"  FAIL {where}: {why}")
    if bad:
        print(f"{len(bad)} text(s) claim more than the purchases cover. Facts: "
              + "; ".join(f"{r}={'/'.join(d)}" for r, d in records.items()))
        return 1
    print(f"  ok   no text claims a purchase covers more than its store record ({len(records)} records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
