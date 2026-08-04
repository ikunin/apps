"""The Impressum — § 5 DDG provider identification — in every language.

**The operative text stays German in all of them.** § 5 DDG is German law about
a German-language provider identification; translating it would be inventing a
legal document rather than translating one. It is one block, used unchanged.

What is per-language is the page around it: the navigation, the title, and one
note telling a reader who does not read German what this page is and where to
go for help instead. Without that, following "Impressum" from the French site
lands on a German page with a German menu and no language switcher, and the
only way back is the browser's back button.

**This is shared rather than owned**, unlike the rest of each app's prose,
because it is a document about the *operator*, not about the app. One operator,
one address; a move should not mean editing three repositories. Each app
supplies its own support address and name through `Site.impressum`.
"""

import html

#: § 5 DDG requires each of these. A missing one is worse than no Impressum.
REQUIRED = ("name", "street", "postcode", "city", "country", "phone", "email")

#: Title, meta template, and the note for a reader who does not read German.
#: `{support}` becomes a link to that language's support page. German gets no
#: note: it is already reading the document.
TEXT = {
"en": ("Provider identification under § 5 DDG for {app}.",
 "<strong>In English:</strong> this page is the provider identification German law requires of commercial websites (§ 5 DDG). It names who operates this site and how to reach them. It is in German because the law is German. For help with the app, use {support}."),
"de": ("Impressum und Anbieterkennzeichnung nach § 5 DDG für {app}.", ""),
"fr": ("Identification du fournisseur selon le § 5 DDG, pour {app}.",
 "<strong>En français :</strong> cette page est l’identification du fournisseur que la loi allemande impose aux sites commerciaux (§ 5 DDG). Elle indique qui exploite ce site et comment le joindre. Elle est en allemand parce que la loi l’est. Pour de l’aide sur l’app, voir {support}."),
"es": ("Identificación del prestador conforme al § 5 DDG, para {app}.",
 "<strong>En español:</strong> esta página es la identificación del prestador que la ley alemana exige a los sitios comerciales (§ 5 DDG). Dice quién opera este sitio y cómo contactarlo. Está en alemán porque la ley lo está. Para ayuda con la app, ve a {support}."),
"it": ("Identificazione del fornitore ai sensi del § 5 DDG, per {app}.",
 "<strong>In italiano:</strong> questa pagina è l’identificazione del fornitore che la legge tedesca richiede ai siti commerciali (§ 5 DDG). Indica chi gestisce questo sito e come contattarlo. È in tedesco perché la legge è tedesca. Per assistenza sull’app, vedi {support}."),
"pt": ("Identificação do prestador nos termos do § 5 DDG, para o {app}.",
 "<strong>Em português:</strong> esta página é a identificação do prestador que a lei alemã exige dos sites comerciais (§ 5 DDG). Diz quem opera este site e como entrar em contato. Está em alemão porque a lei é alemã. Para ajuda com o app, veja {support}."),
"ja": ("{app} の § 5 DDG に基づく事業者情報。",
 "<strong>日本語で：</strong>このページは、ドイツ法が商用サイトに義務づけている事業者情報（§ 5 DDG）です。このサイトの運営者と連絡先を示しています。法律がドイツのものであるため、本文はドイツ語です。アプリのサポートは{support}をご覧ください。"),
"ko": ("{app}의 § 5 DDG에 따른 사업자 정보.",
 "<strong>한국어 안내:</strong> 이 페이지는 독일법이 상업용 웹사이트에 요구하는 사업자 정보(§ 5 DDG)입니다. 이 사이트를 누가 운영하며 어떻게 연락하는지를 밝힙니다. 법이 독일법이라 본문은 독일어입니다. 앱 관련 도움말은 {support}를 보세요."),
"el": ("Στοιχεία παρόχου κατά § 5 DDG, για το {app}.",
 "<strong>Στα ελληνικά:</strong> αυτή η σελίδα είναι τα στοιχεία παρόχου που ο γερμανικός νόμος απαιτεί από τους εμπορικούς ιστότοπους (§ 5 DDG). Λέει ποιος λειτουργεί αυτόν τον ιστότοπο και πώς να επικοινωνήσεις. Είναι στα γερμανικά επειδή ο νόμος είναι γερμανικός. Για βοήθεια με την εφαρμογή, δες {support}."),
"uk": ("Відомості про постачальника згідно з § 5 DDG, для {app}.",
 "<strong>Українською:</strong> ця сторінка — відомості про постачальника, яких німецький закон вимагає від комерційних сайтів (§ 5 DDG). Вона називає, хто керує цим сайтом і як з ним зв’язатися. Текст німецькою, бо закон німецький. По допомогу із застосунком див. {support}."),
"ru": ("Сведения о поставщике согласно § 5 DDG, для {app}.",
 "<strong>По-русски:</strong> эта страница — сведения о поставщике, которых немецкий закон требует от коммерческих сайтов (§ 5 DDG). Она называет, кто управляет этим сайтом и как с ним связаться. Текст на немецком, потому что закон немецкий. За помощью с приложением см. {support}."),
}


def about_the_app(site, language):
    """The two paragraphs that describe an app rather than its operator.

    Separated out because the portfolio at the root of the Pages site carries
    the same § 5 identification and is not an app: it has no privacy page of
    its own, and "die App" there would be three of them. One § 5 block, two
    callers, rather than a second copy that would go stale the next time the
    law's wording did.
    """
    return f"""  <h3>Verkauf über den App&nbsp;Store</h3>
  <p>
    Die App und alle In-App-Käufe werden über den Apple App&nbsp;Store
    vertrieben. Vertragspartner für den Kauf ist Apple; Rückerstattungen
    laufen über
    <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>.
  </p>

  <h3>Datenschutz</h3>
  <p>
    Verantwortlicher im Sinne der DSGVO ist der oben genannte Diensteanbieter.
    Einzelheiten in der
    <a href="{site.local(language, "privacy.html")}">Datenschutzerklärung</a>,
    siehe auch die
    <a href="{site.local(language, "terms.html")}">Nutzungsbedingungen</a>.
  </p>
"""


def body(site, language, *, about=None):
    """The German provider identification. Identical in every language."""
    it = site.impressum
    subject = it.get("subject", it["app"]).replace(" ", "%20")
    mail = f'mailto:{it["email"]}?subject={subject}'
    tel = "tel:+" + "".join(c for c in it["phone"] if c.isdigit())
    return f"""  <p class="muted">Angaben gemäß § 5 DDG (Digitale-Dienste-Gesetz).</p>

  <h3>Diensteanbieter</h3>
  <p>
    {html.escape(it["name"])}<br>
    {html.escape(it["street"])}<br>
    {html.escape(it["postcode"])} {html.escape(it["city"])}<br>
    {html.escape(it["country"])}
  </p>

  <h3>Kontakt</h3>
  <p>
    E-Mail: <a href="{mail}">{html.escape(it["email"])}</a><br>
    Telefon: <a href="{tel}">{html.escape(it["phone"])}</a>
  </p>

  <h3>Verantwortlich für den Inhalt</h3>
  <p>{html.escape(it["name"])}, Anschrift wie oben.</p>

  <h3>Umsatzsteuer</h3>
  <p>
    Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:
    {html.escape(it.get("vat", "keine"))}.
  </p>

  <h3>Verbraucherstreitbeilegung</h3>
  <p>
    Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren
    vor einer Verbraucherschlichtungsstelle teilzunehmen (§ 36
    Verbraucherstreitbeilegungsgesetz).
  </p>
  <p class="muted">
    Ein Hinweis auf die OS-Plattform der Europäischen Kommission entfällt: die
    Plattform wurde am 20. Juli 2025 eingestellt.
  </p>

{about if about is not None else about_the_app(site, language)}
  <h3>Haftung für Links</h3>
  <p>
    Diese Seiten enthalten Links zu externen Websites Dritter, auf deren
    Inhalte wir keinen Einfluss haben. Für diese fremden Inhalte kann keine
    Gewähr übernommen werden; verantwortlich ist stets der jeweilige Anbieter
    der Seite.
  </p>
"""


def page(site, language, *, about=None, note=None):
    """One Impressum page.

    `about` and `note` are the parts that talk about an app rather than about
    the operator, and the portfolio at the root of the Pages site — which is not
    an app and has no privacy or support page of its own — supplies its own.
    Left alone, this renders exactly what it always did.
    """
    missing = [k for k in REQUIRED if not site.impressum.get(k)]
    if missing:
        raise SystemExit("Site.impressum is missing " + ", ".join(missing)
                         + " — § 5 DDG requires each of them")
    meta, standard = TEXT[language]
    if note is None:
        # {support} is this app's own support page. A caller that brings its
        # own note brings its own links with it, and is not formatted again.
        support = f'<a href="{site.local(language, "support.html")}">Support</a>'
        note = standard.format(support=support)
    markup = body(site, language, about=about)
    if note:
        markup += f'\n  <div class="note">\n    <p>{note}</p>\n  </div>\n'
    main = ('<main class="legal"><div class="wrap">\n\n'
            f'<section>\n  <h2>Impressum</h2>\n{markup}</section>\n\n'
            '</div></main>\n')
    return site.document(
        language, "impressum.html",
        title=f'Impressum — {html.escape(site.impressum["app"])}',
        description=html.escape(meta.format(app=site.impressum["app"])),
        main=main)


def write(site):
    for language in site.languages:
        site.write(language, "impressum.html", page(site, language))
    return len(site.languages)
