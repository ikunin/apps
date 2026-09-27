"""The eleven languages, and the words that are the same for every app.

Navigation labels, language names and the governing-language clause are
*chrome*: they say nothing about what an app does, so they belong here rather
than in each app's text tables. An app that adds a page of its own supplies
that page's label itself — see `Page` in chrome.py.

An app's own prose does NOT belong here. Legal text has to be read and owned
per app; a sentence that has to change for one app must not change for the
others. `appsite.boilerplate` ships a starting point to copy, not a shared
source to depend on. That distinction is the whole design: structure is
single-sourced, prose is owned.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Language:
    code: str
    name: str      # endonym, for the language switcher
    locale: str    # what App Store Connect calls it
    nav: dict      # page kind -> label
    governing: str = ""   # translations say which version wins; "" for the original


def _nav(home, support, privacy, terms, apps, download, buy):
    # `download` and `buy` are the verbs on a store link that is not Apple's
    # badge — a platform sold directly (appsite/stores.py).
    return {"home": home, "support": support, "privacy": privacy,
            "terms": terms, "impressum": "Impressum", "apps": apps,
            "download": download, "buy": buy}


# Order matters: it is the order of the language switcher and of the hreflang
# links, and English comes first because it is the original.
LANGUAGES = {
    "en": Language("en", "English", "en-US",
                   _nav("Home", "Support", "Privacy", "Terms", "More apps",
                        "Download", "Buy")),
    "de": Language("de", "Deutsch", "de-DE",
                   _nav("Start", "Hilfe", "Datenschutz", "Nutzung", "Mehr Apps",
                        "Herunterladen", "Kaufen"),
                   "Dies ist eine Übersetzung. Maßgeblich ist im Zweifel die "
                   "englische Fassung: {link}."),
    "fr": Language("fr", "Français", "fr-FR",
                   _nav("Accueil", "Aide", "Confidentialité", "Conditions", "Autres apps",
                        "Télécharger", "Acheter"),
                   "Ceci est une traduction. En cas de divergence, la version "
                   "anglaise fait foi : {link}."),
    "es": Language("es", "Español", "es-ES",
                   _nav("Inicio", "Ayuda", "Privacidad", "Condiciones", "Más apps",
                        "Descargar", "Comprar"),
                   "Esto es una traducción. En caso de discrepancia, prevalece "
                   "la versión en inglés: {link}."),
    "it": Language("it", "Italiano", "it",
                   _nav("Home", "Aiuto", "Privacy", "Condizioni", "Altre app",
                        "Scarica", "Acquista"),
                   "Questa è una traduzione. In caso di difformità prevale la "
                   "versione inglese: {link}."),
    "pt": Language("pt", "Português", "pt-BR",
                   _nav("Início", "Ajuda", "Privacidade", "Termos", "Mais apps",
                        "Baixar", "Comprar"),
                   "Esta é uma tradução. Em caso de divergência, prevalece a "
                   "versão em inglês: {link}."),
    "ja": Language("ja", "日本語", "ja",
                   _nav("ホーム", "サポート", "プライバシー", "利用規約", "ほかのアプリ",
                        "ダウンロード", "購入"),
                   "これは翻訳です。相違がある場合は英語版が優先します：{link}。"),
    "ko": Language("ko", "한국어", "ko",
                   _nav("홈", "지원", "개인정보", "이용약관", "다른 앱",
                        "다운로드", "구매"),
                   "이 문서는 번역본입니다. 내용이 다를 경우 영어판이 우선합니다: {link}."),
    "el": Language("el", "Ελληνικά", "el",
                   _nav("Αρχική", "Βοήθεια", "Απόρρητο", "Όροι", "Άλλες εφαρμογές",
                        "Λήψη", "Αγορά"),
                   "Αυτή είναι μετάφραση. Σε περίπτωση απόκλισης υπερισχύει η "
                   "αγγλική έκδοση: {link}."),
    "uk": Language("uk", "Українська", "uk",
                   _nav("Головна", "Допомога", "Приватність", "Умови", "Інші застосунки",
                        "Завантажити", "Купити"),
                   "Це переклад. У разі розбіжностей чинною є англійська "
                   "версія: {link}."),
    "ru": Language("ru", "Русский", "ru",
                   _nav("Главная", "Помощь", "Приватность", "Условия", "Другие приложения",
                        "Скачать", "Купить"),
                   "Это перевод. При расхождениях действует английская "
                   "версия: {link}."),
}

#: The word the governing-language clause links on. Deliberately "English" in
#: every language: it names the language you are about to be sent to.
ORIGINAL_LINK_LABEL = "English"
