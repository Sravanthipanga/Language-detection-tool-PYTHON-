"""Compact language profiles: frequent function words + distinctive letters.

Function words ("the", "und", "que", ...) make up a large share of any running
text, so a few dozen per language separate languages that share a script very
reliably. Distinctive letters (ñ, ß, ő, ў, ...) add evidence for short inputs.
"""

from __future__ import annotations

_WORDS = {
    # ---------------------------------------------------------------- Latin
    "en": "the of and to in is it you that he was for on are with as i his they be at one have this from or "
    "had by not but what all were we when your can said there use an each which she do how their if will "
    "my me so no about would make like him into time has look two more write go see could people than "
    "first been who its now find long down day did get come made may part am hello today",
    "es": "el la de que y a en un ser se no haber por con su para como estar tener le lo todo pero más hacer o "
    "poder decir este ir otro ese si me ya ver porque dar cuando él muy sin vez mucho saber qué sobre mi "
    "alguno mismo yo también hasta año dos querer entre así primero desde grande eso ni nos llegar pasar "
    "tiempo ella sí día uno bien poco deber entonces los las del una es hola está estoy cómo gracias",
    "fr": "le de un être et à il avoir ne je son que se qui ce dans en du elle au pour pas plus par sur faire "
    "les des une est sont mais avec tout nous vous ils on lui bien où comme avec leur deux sans aussi très "
    "quand cette ces même été peut fait moi je suis bonjour merci c'est oui non la",
    "de": "der die und in den von zu das mit sich des auf für ist im dem nicht ein eine als auch es an werden "
    "aus er hat dass sie nach wird bei einer um am sind noch wie einem über einen so zum war haben nur oder "
    "aber vor zur bis mehr durch man sein wurde sei ich du wir ihr mein dein guten tag hallo danke heute",
    "it": "di e il la che è per un in non una a sono mi ho lo ma ti ci le si con cosa se io come da hai questo "
    "qui bene sei del della al gli anche mio ne tu più cosa molto quando siamo ciao grazie oggi sto stai "
    "come nel dei delle alla tutto fare essere",
    "pt": "de a o que e do da em um para é com não uma os no se na por mais as dos como mas foi ao ele das tem "
    "à seu sua ou ser quando muito há nos já está eu também só pelo pela até isso ela entre era depois sem "
    "mesmo aos ter seus quem nas me esse eles estão você tinha foram essa num nem suas meu às minha olá "
    "obrigado obrigada hoje bom dia tudo bem",
    "nl": "de en van ik te dat die in een hij het niet zijn is was op aan met als voor had er maar om hem dan zou "
    "of wat mijn men dit zo door over ze zich bij ook tot je mij uit der daar haar naar heb hoe heeft "
    "hebben deze u want nog zal me zij nu ge geen omdat iets worden toch al waren veel meer doen toen moet "
    "ben zonder kan hun dus alles onder ja eens hier wie werd altijd doch wordt wezen kunnen ons zelf tegen "
    "na reeds wil kon niets uw iemand geweest andere hallo dank goedemorgen",
    "sv": "och i att det som en på är av för med till den har de inte om ett han men var jag sig från vi så kan "
    "man när år säger hon under också efter eller nu sin där vid mot ska skulle kommer ut får finns vara "
    "hade alla andra mycket än här då sedan över bara blir upp även vad få två vill ha många hur mer går "
    "sverige tack hej idag",
    "da": "og i at det er en til på som de med han af for ikke der var mig sig men et har om vi min havde ham hun "
    "nu over da fra du ud sin dem os op man hans hvor eller hvad skal selv her alle vil blev kunne ind når "
    "være dog noget ville jo deres efter ned skulle denne end dette mit også under have dig anden hende mine "
    "alt meget sit sine vor mod disse hvis din nogle hos blive mange ad bliver hendes været thi jer sådan "
    "tak hej godmorgen",
    "no": "og i jeg det at en et den til er som på de med han av ikke ikkje der så var meg seg men ett har om vi "
    "min mitt ha hadde hun nå over da ved fra du ut sin dem oss opp man kan hans hvor eller hva skal selv "
    "sjøl her alle vil bli ble blei blitt kunne inn når være kom noen noe ville dere deres kun ja etter ned "
    "skulle denne for deg si sine sitt mot å meget hvorfor dette disse uten hvordan ingen din ditt blir "
    "samme hvilken sånn inni mellom vår hver hvem vors hvis både bare enn fordi før mange også slik vært "
    "takk hei norge",
    "fi": "ja on ei se että hän oli ole olla mutta niin kun kuin mitä jos tai vain minä sinä me te he myös nyt "
    "sitten tämä tuo mikä miten missä koska vielä jo paljon hyvä kaikki olen olet ovat oli ollut hyvää "
    "kiitos moi päivää huomenta terve",
    "pl": "i w nie na się z jest to że do co jak ale o tak po za od jestem być mnie mi ten tym go tylko już by "
    "jego czy jej tego może dla przez ich bardzo który która które więc też jeszcze gdzie kiedy wszystko "
    "dzień dobry dziękuję cześć mam masz jesteś",
    "cs": "a se na v je že to s z o do jsem by ale jako pro tak k jsou jeho bylo jak co už není byl jen jsme "
    "které který která když také nebo ve ze až po mi mě tu ty vy my oni ještě jsi dobrý den děkuji ahoj "
    "dnes velmi všechno",
    "sk": "a sa na v je že to s z o do som by ale ako pre tak k sú jeho bolo ako čo už nie bol len sme ktoré "
    "ktorý ktorá keď tiež alebo vo zo až po mi ma tu ty vy my oni ešte si dobrý deň ďakujem ahoj dnes "
    "veľmi všetko",
    "hu": "a az és hogy nem is egy ez meg de van már csak volt el ha mint még én te ő mi ti ők vagy lesz itt ott "
    "most kell minden nagyon jó köszönöm szia mit miért hol amikor aki ami vagyok vagyunk lehet kicsit",
    "ro": "și de la în a pe cu un o că nu este care din se mai pentru ce să au fi lui sunt ca dar am fost acest "
    "această ei el ea eu tu noi voi ale al prin sau după foarte bună ziua mulțumesc salut astăzi bine",
    "tr": "ve bir bu da de için ne ile o çok daha ben sen gibi var yok mi mı mu mü ama en kadar sonra şey her "
    "ki olarak olan değil benim senin nasıl neden ya merhaba teşekkür ederim günaydın bugün iyi evet hayır "
    "nasılsın misin musun",
    "id": "yang dan di itu dengan untuk tidak ini dari dalam akan pada juga saya ke karena tersebut bisa ada "
    "mereka lebih kami sudah atau hanya oleh harus seperti telah kita banyak apa adalah anda kamu aku "
    "selamat pagi terima kasih apa kabar baik bagaimana sangat",
    "vi": "và của là có không được cho trong một những người với này các đã để từ khi đến như thì nhiều tôi "
    "bạn chúng ta anh chị em xin chào cảm ơn rất hôm nay gì làm sao đi",
    "sw": "na ya wa kwa ni za katika la kuwa hii yake au kama lakini pia hiyo watu sana wao mimi wewe yeye sisi "
    "nyinyi habari jambo asante karibu ndiyo hapana leo nzuri gani",
    "tl": "ang ng sa na mga ay at ko ako ka siya kami tayo sila ito iyan iyon hindi oo po salamat kumusta ikaw "
    "niya nila namin natin para may mayroon wala lang din rin pa ba kung",
    "ca": "el la de que i a en un ser es no per amb els les del una són al com però més tot també molt jo tu "
    "ell ella nosaltres vosaltres ells hola gràcies bon dia avui està estic",
    "hr": "i je u se na da su za od a to ne kao što sam ali s iz ili bi bio bila mi ti on ona mi vi oni ovo "
    "taj koji koja koje kako gdje kada zato hvala dobar dan bok danas jesam nisam",
    "sl": "in je v se na da so za od pa to ne kot kaj sem ali z iz ali bi bil bila jaz ti on ona mi vi oni to ta "
    "ki kako kje kdaj zato hvala dober dan živjo danes",
    "et": "ja on ei et see oli ka mis kui aga nii ta ma sa me te nad siis veel kõik väga tere aitäh hommikust "
    "täna olen oled oleme mina sina tema meie",
    "lv": "un ir ar uz par no ka kā bet vai tas tā es tu viņš viņa mēs jūs viņi arī jau ļoti labdien paldies "
    "sveiki šodien esmu esi ir",
    "lt": "ir yra kad su į iš kaip bet ar tai jis ji aš tu mes jūs jie taip ne labai laba diena ačiū labas "
    "šiandien esu esi buvo",
    "is": "og að í á er það sem ekki við hann hún ég þú það var með um af til en fyrir svo hvað þetta eru takk "
    "góðan daginn halló í dag",
    "sq": "dhe në të që një për me nga është janë do nuk si më ka u jam je ai ajo ne ju ata përshëndetje "
    "faleminderit mirëmëngjes sot shumë",
    "af": "die en van in is dat om te het nie wat was ek jy hy sy ons julle hulle met vir op aan sal kan baie "
    "goeie dag dankie hallo vandag",
    "cy": "y yr a ac i yn o ar mae roedd ei ein eu chi fi ni nhw hi fe ond am gyda bore da diolch helo heddiw "
    "sut ydych",
    "ga": "an na agus ar is i le go a ní tá bhí sé sí mé tú muid sibh siad seo sin dia duit go raibh maith agat "
    "inniu conas",
    "eu": "eta da ez ere bat du dira baina hau hori zer nola non noiz ni zu gu zuek kaixo eskerrik asko egun on "
    "gaur oso",
    # ------------------------------------------------- romanized Indian languages
    "hi-Latn": "hai hain kya nahi nahin main mein mera meri tum tumhara aap aapka hum ka ki ke ko se bhi aur "
    "bahut accha acha theek kaise kaisa kyun kab kahan yaar kuch sab abhi tha thi raha rahi namaste "
    "dhanyavaad shukriya haan ji",
    "te-Latn": "nenu meeru nuvvu memu vaallu ela unnaru unnavu enti emiti cheppu cheppandi chala bagundi baagundi "
    "ledu undi unnadi vachanu vellanu vellu randi kaadu avunu inka ippudu ikkada akkada em entha "
    "dhanyavadalu namaskaram baaga manchidi",
    # ------------------------------------------------------------- Cyrillic
    "ru": "и в не на я быть он с что а по это она этот к но они мы как из у который то за свой что весь год от "
    "так о для ты же все тот мочь вы человек такой его сказать только или ещё бы себя один как уже до "
    "время если сам когда другой вот говорить наш мой знать стать при чтобы дело жизнь кто первый очень "
    "привет спасибо здравствуйте сегодня меня тебя где куда здесь там почему",
    "uk": "і в не на я бути він з що а по це вона цей до але вони ми як із у який то за свій весь рік від так о "
    "для ти же все той могти ви людина такий його сказати тільки або ще би себе один вже до час якщо сам "
    "коли інший ось говорити наш мій знати стати при щоб справа життя хто перший дуже привіт дякую "
    "сьогодні мене тебе є",
    "bg": "и в не на аз съм той с че а по това тя този към но те ние как от у който за свой всички година така "
    "за ти също всичко може вие човек такъв неговото само или още би себе си един вече до време ако "
    "когато друг ето говоря наш мой зная при живот кой първи много здравей благодаря днес е са да ще",
    "sr": "и у не на ја је он са да а по то она овај ка али они ми како из који за свој сви година од тако о за "
    "ти све тај моћи ви човек такав његов рећи само или још би себе један већ до време ако сам када други "
    "ево говорити наш мој знати при живот ко први врло здраво хвала данас",
    "mk": "и во не на јас сум тој со дека а по ова таа овој кон но тие ние како од кој за свој сите година така "
    "ти сè тоа може вие човек таков негов само или уште би себе еден веќе до време ако кога друг еве "
    "зборува наш мој знае при живот кој прв многу здраво благодарам денес е се",
    "be": "і ў не на я быць ён з што а па гэта яна гэты да але яны мы як з у які то за свой увесь год ад так "
    "аб для ты ж усе той магчы вы чалавек такі яго сказаць толькі або яшчэ бы сябе адзін ужо час калі "
    "сам іншы вось наш мой ведаць пры каб справа жыццё хто першы вельмі вітаю дзякуй сёння",
    # ----------------------------------------------------------- Devanagari
    "hi": "है के में की और का को से एक पर यह हैं था कि भी नहीं तो ने हो कर रहा लिए गया हम आप मैं वह इस "
    "जो कुछ क्या थे अपने बहुत कैसे नमस्ते धन्यवाद आज हूँ हूं",
    "mr": "आहे आणि या व ते की हे त्या मी तू आम्ही तुम्ही आहेत होते केले नाही काय कसे खूप मला तुला "
    "आपण पण म्हणून नमस्कार धन्यवाद आज आहात झाले",
    "ne": "छ र को मा का ले यो त्यो म तिमी हामी तपाईं छन् थियो गर्न हुन्छ भएको पनि छैन के कसरी धेरै "
    "मलाई तिमीलाई नमस्ते धन्यवाद आज हो हुनुहुन्छ",
    # --------------------------------------------------------------- Arabic
    "ar": "في من على إلى أن هذا التي الذي هو هي ما لا كان مع عن هذه كل بين قد ذلك لم أو بعد عند نحن أنا "
    "أنت هم مرحبا شكرا اليوم كيف حالك جدا",
    "fa": "و در به از که این را با است برای آن یک خود تا کرد بر هم نیز شد می من تو ما شما آنها سلام "
    "مرسی ممنون امروز چطور خیلی هست نیست",
    "ur": "اور کے میں کی ہے سے کو کا پر یہ وہ نہیں تھا ہیں ایک بھی تو ہم آپ میں کیا کیسے بہت شکریہ السلام آج ہوں ہو گا",
}

# Everyday vocabulary, used only to learn each language's spelling patterns
# (letter trigrams). Not used as whole-word evidence.
_VOCAB = {
    "en": "house water world people child night morning evening book school work friend family city country "
    "money something nothing everything little great small right thing would should thought through",
    "es": "casa agua mundo gente niño noche mañana tarde libro escuela trabajo amigo familia ciudad país dinero "
    "algo nada siempre nunca pequeño grande ahora después mucho tiempo",
    "fr": "maison eau monde gens enfant nuit matin soir livre école travail ami famille ville pays argent "
    "quelque rien toujours jamais petit grand maintenant après beaucoup temps",
    "de": "haus wasser welt leute kind nacht morgen abend buch schule arbeit freund familie stadt land geld "
    "etwas nichts immer nie klein groß jetzt nachher viel zeit",
    "it": "casa acqua mondo gente bambino notte mattina sera libro scuola lavoro amico famiglia città paese "
    "soldi qualcosa niente sempre mai piccolo grande adesso dopo molto tempo",
    "pt": "casa água mundo gente criança noite manhã tarde livro escola trabalho amigo família cidade país "
    "dinheiro algo nada sempre nunca pequeno grande agora depois muito tempo",
    "nl": "huis water wereld mensen kind nacht morgen avond boek school werk vriend familie stad land geld iets "
    "niets altijd nooit klein groot straks veel tijd",
    "sv": "hus vatten värld människor barn natt morgon kväll bok skola arbete vän familj stad land pengar något "
    "ingenting alltid aldrig liten stor nu sedan mycket tid",
    "da": "hus vand verden mennesker barn nat morgen aften bog skole arbejde ven familie by land penge noget "
    "intet altid aldrig lille stor nu bagefter meget tid",
    "no": "hus vann verden mennesker barn natt morgen kveld bok skole arbeid venn familie by land penger noe "
    "ingenting alltid aldri liten stor nå etterpå mye tid",
    "fi": "talo vesi maailma ihmiset lapsi yö aamu ilta kirja koulu työ ystävä perhe kaupunki maa raha jotain "
    "aina koskaan pieni suuri nyt myöhemmin paljon aika",
    "pl": "dom woda świat ludzie dziecko noc rano wieczór książka szkoła praca przyjaciel rodzina miasto kraj "
    "pieniądze coś nic zawsze nigdy mały duży teraz potem dużo czas",
    "cs": "dům voda svět lidé dítě noc ráno večer kniha škola práce přítel rodina město země peníze něco nic "
    "vždy nikdy malý velký teď potom hodně čas",
    "sk": "dom voda svet ľudia dieťa noc ráno večer kniha škola práca priateľ rodina mesto krajina peniaze "
    "niečo nič vždy nikdy malý veľký teraz potom veľa čas",
    "hu": "ház víz világ emberek gyerek éjszaka reggel este könyv iskola munka barát család város ország pénz "
    "valami semmi mindig soha kicsi nagy most aztán sok idő szép nap szó kéz fej szem száj fül láb élet "
    "szív szerelem férfi nő ablak ajtó asztal szék kenyér hús alma út kert erdő folyó",
    "ro": "casă apă lume oameni copil noapte dimineață seară carte școală muncă prieten familie oraș țară bani "
    "ceva nimic mereu niciodată mic mare acum apoi mult timp",
    "tr": "ev su dünya insanlar çocuk gece sabah akşam kitap okul iş arkadaş aile şehir ülke para hiçbir zaman "
    "asla küçük büyük şimdi güzel bugün yarın dün kadın erkek kapı yol ağaç deniz dağ göz el baş yüz kalp "
    "sevgi gelmek gitmek yapmak söylemek görmek bilmek istemek düşünmek",
    "id": "rumah air dunia orang anak malam pagi sore buku sekolah kerja teman keluarga kota negara uang "
    "sesuatu selalu kecil besar sekarang nanti banyak waktu",
    "vi": "nhà nước thế giới người trẻ đêm sáng tối sách trường việc bạn gia đình thành phố đất tiền điều luôn "
    "bao giờ nhỏ lớn bây sau thời gian",
    "sw": "nyumba maji dunia watu mtoto usiku asubuhi jioni kitabu shule kazi rafiki familia mji nchi pesa kitu "
    "hakuna daima kamwe ndogo kubwa sasa baadaye mengi wakati",
    "tl": "bahay tubig mundo tao bata gabi umaga hapon libro paaralan trabaho kaibigan pamilya lungsod bansa pera",
    "ca": "casa aigua món gent nen nit matí tarda llibre escola feina amic família ciutat país diners",
    "hr": "kuća voda svijet ljudi dijete noć jutro večer knjiga škola posao prijatelj obitelj grad zemlja novac",
    "sl": "hiša voda svet ljudje otrok noč jutro večer knjiga šola delo prijatelj družina mesto država denar",
    "et": "maja vesi maailm inimesed laps öö hommik õhtu raamat kool töö sõber perekond linn riik raha",
    "lv": "māja ūdens pasaule cilvēki bērns nakts rīts vakars grāmata skola darbs draugs ģimene pilsēta valsts",
    "lt": "namas vanduo pasaulis žmonės vaikas naktis rytas vakaras knyga mokykla darbas draugas šeima miestas",
    "is": "hús vatn heimur fólk barn nótt morgunn kvöld bók skóli vinna vinur fjölskylda borg land peningar",
    "sq": "shtëpi ujë botë njerëz fëmijë natë mëngjes mbrëmje libër shkollë punë mik familje qytet vend para",
    "af": "huis water wêreld mense kind nag oggend aand boek skool werk vriend familie stad land geld",
    "cy": "tŷ dŵr byd pobl plentyn nos bore noswaith llyfr ysgol gwaith ffrind teulu dinas gwlad arian",
    "ga": "teach uisce domhan daoine páiste oíche maidin tráthnóna leabhar scoil obair cara teaghlach cathair",
    "eu": "etxea ura mundua jendea haurra gaua goiza arratsaldea liburua eskola lana laguna familia hiria",
    "ru": "дом вода мир люди ребёнок ночь утро вечер книга школа работа друг семья город страна деньги ничего "
    "всегда никогда маленький большой сейчас потом много время",
    "uk": "дім вода світ люди дитина ніч ранок вечір книга школа робота друг родина місто країна гроші щось "
    "нічого завжди ніколи маленький великий зараз потім багато час",
    "be": "дом вада свет людзі дзіця ноч раніца вечар кніга школа праца сябар сям'я горад краіна грошы",
    "bg": "къща вода свят хора дете нощ сутрин вечер книга училище работа приятел семейство град страна пари "
    "нещо нищо винаги никога малък голям сега после много време",
    "sr": "кућа вода свет људи дете ноћ јутро вече књига школа посао пријатељ породица град земља новац",
    "mk": "куќа вода свет луѓе дете ноќ утро вечер книга училиште работа пријател семејство град земја пари",
}

STOPWORDS: dict[str, frozenset[str]] = {lang: frozenset(words.split()) for lang, words in _WORDS.items()}
VOCAB: dict[str, frozenset[str]] = {lang: frozenset(words.split()) for lang, words in _VOCAB.items()}

# Letters present in almost any sentence of these languages. When none of
# them appears in a reasonably long text, the language is unlikely.
SIGNATURE_CHARS: dict[str, str] = {"uk": "іїєґ", "be": "ў", "bg": "ъщ", "sr": "јђћ", "mk": "јќѓѕ"}

# Letters that are rare or absent elsewhere. Each occurrence adds evidence.
DISTINCT_CHARS: dict[str, str] = {
    "es": "ñ¿¡",
    "pt": "ãõ",
    "fr": "œûù",
    "de": "ßäöü",
    "it": "ì",
    "ca": "ŀ",
    "sv": "åä",
    "da": "æøå",
    "no": "æøå",
    "fi": "äö",
    "is": "ðþæ",
    "pl": "łżźśćńąę",
    "cs": "řůě",
    "sk": "ľĺŕôä",
    "hu": "őű",
    "ro": "ăâîșțşţ",
    "tr": "ğışçöü",
    "vi": "ơưđạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ",
    "hr": "čćđšž",
    "sl": "čšž",
    "et": "õäöü",
    "lv": "āēīūķļņģ",
    "lt": "ąčęėįšųūž",
    "sq": "ëç",
    "cy": "ŵŷ",
    "uk": "іїєґ",
    "be": "ўі",
    "sr": "ђјљњћџ",
    "mk": "ѓќѕјљњџ",
    "bg": "ъщ",
    "ru": "ыэъ",
    "fa": "پچژگ",
    "ur": "ٹڈڑںےۓ",
}

# Which languages compete inside a multi-language script.
SCRIPT_CANDIDATES: dict[str, tuple[str, ...]] = {
    "Latin": (
        "en",
        "es",
        "fr",
        "de",
        "it",
        "pt",
        "nl",
        "sv",
        "da",
        "no",
        "fi",
        "pl",
        "cs",
        "sk",
        "hu",
        "ro",
        "tr",
        "id",
        "vi",
        "sw",
        "tl",
        "ca",
        "hr",
        "sl",
        "et",
        "lv",
        "lt",
        "is",
        "sq",
        "af",
        "cy",
        "ga",
        "eu",
        "hi-Latn",
        "te-Latn",
    ),
    "Cyrillic": ("ru", "uk", "bg", "sr", "mk", "be"),
    "Devanagari": ("hi", "mr", "ne"),
    "Arabic": ("ar", "fa", "ur"),
}
SCRIPT_DEFAULT = {"Cyrillic": "ru", "Devanagari": "hi", "Arabic": "ar"}
