"""Where to report a security vulnerability — the same words on every site.

The Cyber Resilience Act (Art. 14) asks the maker of a product with digital
elements to say where a vulnerability is reported. **This is shared rather
than owned**, like the Impressum: it is about the *operator* — one person, one
mailbox, one way to reach them — not about what any one app does, so it is
written once here and every support page and the index at the root carry it
(`legal.security`, appended by `legal.page` to every `support.html`).

Data only, so `legal` can import it and `check_text.py --texts appsite` reads
it like an app's text table. `{mail}` becomes the app's support address with a
subject that names the app and "Security" (`legal.mail`). It makes no promise
of a response time, deliberately: one person answers, and a deadline written
here is a deadline published on every site at once.
"""

#: The fragment every page links the section by; security.txt's Policy names it.
ANCHOR = "security"

TEXT = {
"en": {"h": "Report a security vulnerability",
       "p": "If you find a security vulnerability in one of my apps or on these websites, please report it by email to {mail}, with “Security” in the subject. You can write in German or English. Describe what you found and how to reproduce it, and please give me the chance to fix it before you make it public."},
"de": {"h": "Sicherheitslücke melden",
       "p": "Wenn du eine Sicherheitslücke in einer meiner Apps oder auf diesen Websites findest, melde sie bitte per E-Mail an {mail}, mit „Security“ im Betreff. Du kannst auf Deutsch oder Englisch schreiben. Beschreib, was du gefunden hast und wie es sich nachvollziehen lässt, und gib mir bitte Gelegenheit, die Lücke zu schließen, bevor du sie veröffentlichst."},
"fr": {"h": "Signaler une faille de sécurité",
       "p": "Si tu trouves une faille de sécurité dans l’une de mes apps ou sur ces sites, signale-la par e-mail à {mail}, avec « Security » dans l’objet. Tu peux écrire en allemand ou en anglais. Décris ce que tu as trouvé et comment le reproduire, et laisse-moi s’il te plaît le temps de la corriger avant de la rendre publique."},
"es": {"h": "Informar de una vulnerabilidad de seguridad",
       "p": "Si encuentras una vulnerabilidad de seguridad en una de mis apps o en estos sitios web, infórmala por correo electrónico a {mail}, con «Security» en el asunto. Puedes escribir en alemán o en inglés. Describe lo que encontraste y cómo reproducirlo, y dame, por favor, la oportunidad de corregirla antes de hacerla pública."},
"it": {"h": "Segnalare una vulnerabilità di sicurezza",
       "p": "Se trovi una vulnerabilità di sicurezza in una delle mie app o su questi siti, segnalala via e-mail a {mail}, con «Security» nell’oggetto. Puoi scrivere in tedesco o in inglese. Descrivi cosa hai trovato e come riprodurlo, e per favore dammi modo di correggerla prima di renderla pubblica."},
"pt": {"h": "Relatar uma vulnerabilidade de segurança",
       "p": "Se você encontrar uma vulnerabilidade de segurança em um dos meus apps ou nestes sites, relate-a por e-mail para {mail}, com “Security” no assunto. Você pode escrever em alemão ou em inglês. Descreva o que encontrou e como reproduzir e, por favor, me dê a chance de corrigi-la antes de torná-la pública."},
"ja": {"h": "セキュリティ上の脆弱性の報告",
       "p": "私のアプリやこれらのウェブサイトでセキュリティ上の脆弱性を見つけた場合は、件名に「Security」と入れて {mail} までメールでお知らせください。ドイツ語または英語でお書きください。見つけた内容と再現の手順を記載し、公開する前に修正する機会をいただけますようお願いします。"},
"ko": {"h": "보안 취약점 신고",
       "p": "제 앱이나 이 웹사이트에서 보안 취약점을 발견하셨다면 제목에 “Security”를 넣어 {mail} 로 이메일을 보내 주세요. 독일어나 영어로 작성해 주시면 됩니다. 발견한 내용과 재현 방법을 적어 주시고, 공개하기 전에 고칠 기회를 주시기 바랍니다."},
"el": {"h": "Αναφορά ευπάθειας ασφαλείας",
       "p": "Αν βρεις μια ευπάθεια ασφαλείας σε μία από τις εφαρμογές μου ή σε αυτούς τους ιστότοπους, ανάφερέ τη με email στο {mail}, με «Security» στο θέμα. Μπορείς να γράψεις στα γερμανικά ή στα αγγλικά. Περίγραψε τι βρήκες και πώς αναπαράγεται, και δώσε μου, σε παρακαλώ, την ευκαιρία να τη διορθώσω πριν τη δημοσιοποιήσεις."},
"uk": {"h": "Повідомити про вразливість",
       "p": "Якщо ти знайдеш вразливість безпеки в одному з моїх застосунків або на цих сайтах, повідом про неї електронною поштою на {mail}, вказавши «Security» в темі листа. Писати можна німецькою або англійською. Опиши, що ти знайшов і як це відтворити, і, будь ласка, дай мені змогу її виправити, перш ніж оприлюднювати."},
"ru": {"h": "Сообщить об уязвимости",
       "p": "Если ты найдёшь уязвимость в одном из моих приложений или на этих сайтах, сообщи о ней по электронной почте на {mail}, указав «Security» в теме письма. Писать можно на немецком или английском. Опиши, что ты нашёл и как это воспроизвести, и, пожалуйста, дай мне возможность её исправить, прежде чем публиковать."},
}
