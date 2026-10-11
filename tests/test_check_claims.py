#!/usr/bin/env python3
"""check_claims must catch the sentences that were published, and pass the true ones.
`python3 tests/test_check_claims.py`, no pytest needed."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import check_claims as c

SPEEDY = {"app": ["iPhone", "iPad", "Apple Watch"], "mac": ["Mac"], "tv": ["Apple TV"]}
JUSTTALK = {"mac": ["Mac"], "ios": ["iPhone", "iPad"], "win": ["Windows"]}

#: Published, false: one purchase does not cross store records.
FALSE = [
    (SPEEDY, "Free to play, unlocked with one purchase. Five Apple platforms, eleven languages, no account needed."),
    (SPEEDY, "One game, one purchase — the same on every Apple device you own."),
    (SPEEDY, "One purchase that unlocks every mode on iPhone, iPad, Mac, Apple TV and Apple Watch."),
    (SPEEDY, "Ein Spiel, ein Kauf — dasselbe auf jedem Apple-Gerät, das Sie besitzen."),
    (SPEEDY, "一つのゲームを一度買えば、お持ちのどの Apple デバイスでも同じように遊べます。"),
    (JUSTTALK, "Free to try, unlocked with one purchase. Mac, Windows, iPhone and iPad, 100 languages."),
    (JUSTTALK, "The same app on every platform. Each is bought once from its own store: the App Store for Mac, "
               "iPhone and iPad, the Microsoft Store for Windows."),
]
TRUE = [
    (SPEEDY, "One purchase unlocks iPhone, iPad and Apple Watch; Mac and Apple TV are separate apps, each with its own purchase."),
    (SPEEDY, "iPhone、iPad、Apple Watch でまとめて解放する購入です（Mac と Apple TV は別のアプリで、購入も別々です）。"),
    (SPEEDY, "Pro unlocks all ten modes here. Buying a bundle after a theme does not refund it, so the shop shows what you already own."),
    (SPEEDY, "Free to play. Eleven languages, no account needed."),
    (JUSTTALK, "Free to try. Each of Mac, iPhone and iPad, and Windows is a separate purchase, bought once from its own store."),
    ({"only": ["Mac"]}, "Unlocked with one purchase, on every Mac."),   # one record: nothing to confuse
]


class ClaimTests(unittest.TestCase):
    def test_published_false_claims_are_caught(self):
        for records, text in FALSE:
            self.assertIsNotNone(c.verdict(text, records), text)

    def test_true_statements_pass(self):
        for records, text in TRUE:
            self.assertIsNone(c.verdict(text, records), text)

    def test_a_separate_word_in_another_sentence_does_not_excuse_it(self):
        text = "Pro unlocks the game on iPhone, iPad, Mac and Apple TV. Single themes are sold separately."
        self.assertIsNotNone(c.verdict(text, SPEEDY))

    def test_json_translations_are_read(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "de.json")
            json.dump({"home": {"lockup": "Ein Kauf für Mac, Windows, iPhone und iPad."}}, open(path, "w"))
            self.assertEqual(list(c._json_values(path)),
                             [(f"{path} home.lockup", "Ein Kauf für Mac, Windows, iPhone und iPad.")])

    def test_the_fastfile_cannot_sell_an_undeclared_record(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            records, fastfile = os.path.join(tmp, "r.json"), os.path.join(tmp, "Fastfile")
            json.dump({"a": ["Mac"]}, open(records, "w"))
            open(fastfile, "w").write('MAC = {\n  app_id: "a",\n}\nIOS = {\n  app_id: "b",\n}\n')
            with self.assertRaises(SystemExit):
                c.load_records(records, fastfile)


if __name__ == "__main__":
    unittest.main()
