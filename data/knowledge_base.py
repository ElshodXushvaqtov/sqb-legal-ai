"""
knowledge_base.py – O'zbekiston bank huquqi va rasmiy yozishmalar bazasi
SQB Legal AI v3.0
"""

LEGAL_DOCS = [
    # ── Banklar va bank faoliyati ────────────────────────────────────────────
    """
    O'zbekiston Respublikasi "Banklar va bank faoliyati to'g'risida"gi Qonun (1996-yil 25-aprel, №378-I).

    7-modda. Bankning huquqiy maqomi:
    Banklar mustaqil yuridik shaxslar bo'lib, O'zbekiston Respublikasi qonunchiligi asosida faoliyat yuritadi.

    27-modda. Bank siri:
    Bank mijozlar hisob raqamlari, ular bo'yicha operatsiyalar, qoldiqlari va aylanmalari, shuningdek
    mijozlar to'g'risidagi boshqa ma'lumotlar bank sirini tashkil etadi.
    Bank siri quyidagi hollarda ochilishi mumkin:
    - Mijozning yozma roziligi bilan
    - Sud qaroriga asosan
    - Prokuratura rasmiy talabnomasiga asosan
    - Soliq organlari rasmiy so'roviga asosan
    - Markaziy bank nazorat talabiga asosan
    - Moliyaviy monitoring qo'mitasi talabiga asosan

    28-modda. Davlat organlariga ma'lumot taqdim etish:
    Banklar davlat organlari so'rovlariga belgilangan muddat ichida javob berishlari shart.
    So'rov rasmiy blankal, vakolatli shaxs imzosi va muhr bilan tasdiqlanishi zarur.
    So'rovda: so'rovchi organ nomi, so'rov sanasi va raqami, so'ralayotgan ma'lumot aniq tavsifi,
    so'rovning huquqiy asosi ko'rsatilishi shart.

    39-modda. Javobgarlik:
    Bank siri buzilishi — ma'muriy va jinoiy javobgarlikka tortilish asosi.
    Asossiz ma'lumot taqdim etmaslik — bank litsenziyasini cheklash asosi.
    """,

    # ── Bank siri qonuni ─────────────────────────────────────────────────────
    """
    O'zbekiston Respublikasi "Bank siri to'g'risida"gi Qonun (2006-yil 11-dekabr, №ЎРҚ-30).

    1-modda. Bank siri tushunchasi:
    Bank siri — mijozning shaxsiy ma'lumotlari, hisob raqamlari, ular bo'yicha qoldig'i va
    harakati, kredit va depozit shartlari, kafillar to'g'risidagi ma'lumotlar.

    3-modda. Bank sirini saqlash majburiyati:
    Bank va uning barcha xodimlari mijozlar haqidagi ma'lumotlarni sir saqlashi shart.
    Bu majburiyat ish tugagandan keyin ham davom etadi.

    5-modda. Bank sirini ochish holatlari:
    Bank mijoz ma'lumotlarini uchinchi shaxslarga FAQAT quyidagi holatlarda berishi mumkin:
    1. Mijozning (yoki merosxo'rning) yozma roziligi bilan.
    2. Sud qaroriga asosan — fuqarolik va xo'jalik ishlari bo'yicha.
    3. Prokuratura rasmiy talabnomasiga asosan (JPK 178-modda).
    4. Soliq organlari rasmiy so'roviga asosan (Soliq Kodeksi 86-modda).
    5. Markaziy bank nazorat talabiga asosan.
    6. Moliyaviy razvedka qo'mitasi (MRQ) talabiga asosan.
    7. Jinoiy ishlar bo'yicha tergov organlari talabiga asosan.

    7-modda. Audit jurnali:
    Barcha ma'lumot taqdimotlari audit jurnaliga qayd etilishi shart.
    Jurnal: sana, so'rovchi organ, taqdim etilgan ma'lumotlar doirasi, javobgar xodim imzosi.

    9-modda. Javobgarlik:
    Bank sirini asossiz oshkor qilish — 100-200 bazaviy miqdor miqdorida jarima.
    Qayta sodir etilsa — jinoiy javobgarlik (O'zR JK 189-modda).
    """,

    # ── Soliq Kodeksi ────────────────────────────────────────────────────────
    """
    O'zbekiston Respublikasi Soliq Kodeksi (2019-yil 30-dekabr, №ЎРҚ-599).

    86-modda. Soliq organlarining bank ma'lumotlariga kirishga huquqi:

    86.1. Soliq organlari to'lovchilarning bank hisob raqamlari to'g'risidagi
    ma'lumotlarni soliq tekshiruvi yoki kameral tekshiruv doirasida so'rash huquqiga ega.

    86.2. Bank soliq organining rasmiy so'rovini olgandan so'ng 3 ish kuni ichida
    quyidagi ma'lumotlarni taqdim etishi shart:
    - Hisob raqami holati (faol/yopiq/muzlatilgan)
    - Hisob raqamidagi qoldiq (so'rov sanasiga)
    - Belgilangan davr uchun aylanmalar
    - O'tkazmalar ro'yxati (kontragentlar bilan)

    86.3. Bank soliq organiga taqdim etmasligi mumkin bo'lgan ma'lumotlar:
    - Boshqa mijozlarning shaxsiy ma'lumotlari
    - Bank ichki hujjatlari (kredit qo'mita bayonnomalar va h.k.)
    - Xodimlar to'g'risidagi ma'lumotlar

    86.4. So'rovda mavjud bo'lishi shart:
    - Soliq organi nomi va manzili
    - So'rov sanasi va raqami
    - Vakolatli mansabdor shaxs imzosi va muhri
    - Huquqiy asos (qonun moddasiga havola)
    - So'ralayotgan ma'lumot aniq tavsifi
    - So'rov maqsadi

    86.5. Javob berishdan asossiz bosh tortish — bank uchun 50 bazaviy miqdor jarima.
    Takroriy bosh tortish — 100 bazaviy miqdor + litsenziya cheklash.

    87-modda. Soliq tekshiruvi davomida bank ishi:
    Soliq tekshiruvi bank normal ish rejimini buzmasligi shart.
    Tekshiruvchi bank binolarida maxfiylik rejimini saqlashi shart.
    Taqdim etilgan barcha hujjatlar ikki nusxada imzoli ro'yxat bilan topshiriladi.
    """,

    # ── JPK / Prokuratura ────────────────────────────────────────────────────
    """
    O'zbekiston Respublikasi Jinoyat-protsessual kodeksi (1994-yil 22-sentyabr).

    178-modda. Tergov harakatlari uchun bank ma'lumotlari:

    178.1. Tergov organlari va prokuratura jinoiy ish bo'yicha bank ma'lumotlarini
    rasmiy talab orqali so'rash huquqiga ega.

    178.2. Talabda ko'rsatilishi shart:
    - Jinoiy ish raqami va sanasi
    - Tergov organi nomi va manzili
    - Tergovchi yoki prokurorning to'liq ismi va lavozimi
    - So'ralayotgan ma'lumot aniq tavsifi
    - So'rovning huquqiy asosi
    - Javob muddati

    178.3. Bank talabni olgandan so'ng:
    - 3 ish kuni ichida javob berishi shart (jinoiy ish bo'yicha)
    - 5 ish kuni ichida (boshqa tergov harakatlari bo'yicha)
    - Favqulodda hollarda (pul muzlatish) — 24 soat ichida

    178.4. Bank mijozni so'rov haqida xabardor qilishi mumkin yoki qilmasligi:
    Tergovchi yoki prokuror maxfiylik rejimi haqida ko'rsatma berishi mumkin.
    Bunday ko'rsatma bo'lsa bank mijozni xabardor qilmaydi.

    179-modda. Hisobvaraqlarni muzlatish:
    179.1. Tergovchi yoki prokuror sanktsiyasi bilan hisob raqamlar muzlatilishi mumkin.
    179.2. Muzlatish haqidagi talab 24 soat ichida bajarilishi shart.
    179.3. Muzlatish davomida faqat majburiy to'lovlar (alimentlar, ish haqi) amalga oshiriladi.
    """,

    # ── Markaziy bank ────────────────────────────────────────────────────────
    """
    O'zbekiston Respublikasi Markaziy banki haqidagi Qonun (1995-yil 21-dekabr, №154-I).

    Markaziy bank yo'riqnomasi (2019-yil 15-may, №23/1-son).

    Nazorat va tekshiruv tartibi:

    1. Markaziy bank nazorat so'rovlariga javob muddati — 5 ish kuni.
    2. Favqulodda so'rovlar (likvidlik inqirozi, to'lov qobiliyatsizligi) — 24 soat.
    3. Barcha javoblar rasmiy bank blankasida, imzo va muhr bilan tasdiqlanishi shart.

    Taqdim etilishi shart bo'lgan ma'lumotlar:

    Prudensial ko'rsatkichlar:
    - Kapital yetarliligi koeffitsienti (CAR) — kamida 13%
    - Likvidlik qoplash koeffitsienti (LCR) — kamida 100%
    - Xolis likvidlik koeffitsienti (NSFR) — kamida 100%
    - Muddati o'tgan kreditlar ulushi (NPL) — 5% dan oshmasligi kerak
    - Yirik kredit risklari — kapitalning 25% dan oshmasligi kerak

    Hisobotlar:
    - Oylik: balans, daromadlar/xarajatlar, kapital
    - Choraklik: prudensial ko'rsatkichlar, kredit portfeli
    - Yillik: auditorlik xulosasi bilan moliyaviy hisobot

    Nazorat sanksiyalari:
    - Ogohlantirish
    - Jarima (kapitalning 0.1-1%)
    - Faoliyatni cheklash
    - Litsenziyani bekor qilish
    """,

    # ── AML / Pul yuvish ─────────────────────────────────────────────────────
    """
    O'zbekiston Respublikasi "Jinoiy faoliyatdan olingan daromadlarni legallashtirishga
    va terrorizmni moliyalashtirishga qarshi kurashish to'g'risida"gi Qonun
    (2004-yil 26-avgust, №AML-2004).

    12-modda. Banklarning AML majburiyatlari:

    12.1. Majburiy nazoratga tushuvchi operatsiyalar:
    - 50 million so'mdan yuqori naqd pul operatsiyalari
    - Valyutani naqd pulga almashtirish (5,000 AQSh dollaridan yuqori)
    - Xorijiy valyutadagi o'tkazmalar (50,000 AQSh dollaridan yuqori)
    - Offshor hisoblarga o'tkazmalar (har qanday miqdorda)
    - Nostandart operatsiyalar (g'ayrioddiy miqdor, tezlik, tartib)

    12.2. Shubhali operatsiyalar to'g'risida xabar berish:
    Bank shubhali operatsiyani aniqlagan kundan 3 ish kuni ichida
    Moliyaviy razvedka qo'mitasiga (MRQ) xabar berishi shart.

    12.3. Operatsiyalarni to'xtatish huquqi:
    Bank shubhali operatsiyani 48 soatgacha to'xtatish huquqiga ega.
    MRQ ruxsatisiz to'xtatish muddati uzaytirilmaydi.

    12.4. Mijozni identifikatsiya qilish (KYC):
    - Barcha yangi mijozlar to'liq identifikatsiya qilinishi shart
    - Tavakkalchilik darajasi yuqori mijozlar — kuchaytirilgan tekshiruv (EDD)
    - Siyosiy ta'sirga ega shaxslar (PEP) — alohida nazorat

    12.5. Xabar berish maxfiyligi:
    Xabar berilganligi haqida mijozni xabardor qilish man etiladi ("tipping off").
    """,

    # ── Rasmiy yozishmalar tartibi ───────────────────────────────────────────
    """
    Rasmiy yozishmalar tartibi — SQB Bank Ichki Standart (2023-yil yanvar).

    1. Javob hujjatining majburiy rekvizitlari:

    Blanka ma'lumotlari:
    - Bank to'liq nomi: "O'zbekiston Sanoat-Qurilish Banki" AJ
    - STIR, hisob raqami, BIK
    - Yuridik manzil va aloqa ma'lumotlari
    - Veb-sayt: www.sqb.uz

    Hujjat rekvizitlari:
    - Chiquvchi raqam (ro'yxatga olish raqami)
    - Sana (kun.oy.yil formatida)
    - Kimga: organ nomi, manzil, mansabdor shaxs
    - Javob berilayotgan so'rov raqami va sanasi

    Mazmun tuzilmasi:
    a) Kirish — murojaatga havola, qabul qilinganlik tasdigi
    b) Huquqiy asos — qonun moddalari (to'liq nomi va raqami)
    c) Asosiy qism — so'ralgan ma'lumot yoki tushuntirish
    d) Cheklovlar — bank siri doirasidagi chegaralar (agar zarur)
    e) Muddat — ma'lumot taqdim etilishi muddati
    f) Xulosa — hamkorlikka tayyorlik

    Imzo tartibi:
    - Bank rahbari yoki vakolatli o'rinbosar imzosi
    - Yuridik bo'lim boshlig'i viza
    - Rasmiy muhr

    2. Nusxalar:
    - Asil nusxa — so'rovchiga
    - Nusxa — arxivga (kamida 5 yil)
    - Nusxa — yuridik bo'limda
    """,

    # ── Prokuratura bilan ishlash ────────────────────────────────────────────
    """
    Prokuratura so'rovlari bilan ishlash protsedurasi — SQB Bank.

    Talabnoмa qabul qilinganda qilinishi kerak bo'lgan harakatlar:

    1. Darhol (1 soat ichida):
    - Yuridik bo'limni xabardor qilish
    - Talabnoмani ro'yxatga olish (kiruvchi journal)
    - Talabnoмaning rasmiy ekanligini tekshirish:
      * Prokuratura blankasidaligi
      * Prokuror yoki o'rinbosar imzosi
      * Rasmiy muhr
      * So'rov raqami va sanasi
      * Huquqiy asos (qonun moddasiga havola)

    2. Rasmiylikni tekshirish (24 soat):
    - So'rovchi prokurorning vakolatini tekshirish
    - Jinoiy ish raqamini tekshirish (agar ko'rsatilgan bo'lsa)
    - Prokuratura bosh idorasiga tasdiqlash qo'ng'irog'i (zarur hollarda)

    3. Maxfiylik rejimi:
    - Prokuratura ko'rsatmasi bo'lsa — mijozni xabardor qilish man etiladi
    - Talabnoмa mazmuni bank ichida minimal doira bilan tanishtiriladi
    - Tashqi shaxslarga oshkor qilish taqiqlanadi

    4. Javob tayyorlash:
    - Bosh yuridik maslahatchi ishtirokida
    - Muddati: 10 ish kuni (JPK 178-modda)
    - Jinoiy ishlar bo'yicha: 3 ish kuni
    - Muzlatish talabi: 24 soat

    5. Taqdim etish:
    - Rasmiy bank blankasida, imzo va muhr bilan
    - Hujjatlar ro'yxati tuziladi (inventarizatsiya)
    - Qabul qilishga imzo olinadi
    """,

    # ── Soliq tekshiruvi ─────────────────────────────────────────────────────
    """
    Soliq tekshiruvlari bilan ishlash — amaliy qo'llanma.

    So'rovni qabul qilinganida tekshiriladigan elementlar:

    Majburiy rekvizitlar:
    ✓ Soliq organining rasmiy blankasidaligi
    ✓ Vakolatli mansabdor shaxs imzosi
    ✓ Soliq organi muhri
    ✓ So'rov raqami va sanasi
    ✓ Huquqiy asos (Soliq Kodeksi moddasiga havola)
    ✓ So'ralayotgan ma'lumot aniq tavsifi
    ✓ Tekshiriladigan soliq to'lovchi STIR/pasport ma'lumotlari
    ✓ So'rov davri ko'rsatilganligi
    ✓ Javob muddati

    Taqdim etiladigan ma'lumotlar (Soliq Kodeksi 86-modda):
    - Hisob raqamlari ro'yxati (faol va yopiq)
    - Belgilangan sanadagi qoldiq
    - Ko'rsatilgan davr uchun kredit va debet aylanmalar
    - O'tkazmalar bo'yicha kontragentlar ma'lumotlari

    Taqdim etilmaydigan ma'lumotlar:
    - Boshqa mijozlarning ma'lumotlari
    - Kredit qo'mita bayonnomalari
    - Bank ichki me'yoriy hujjatlari
    - Xodimlar haqidagi ma'lumotlar

    Javob muddati: 3 ish kuni (standart); favqulodda hollarda — 1 ish kuni.

    Barcha taqdim etilgan hujjatlar:
    - Ikki nusxada imzoli ro'yxat bilan topshiriladi
    - Bank nusxasiga qabul qiluvchi imzo qo'yadi
    - 5 ish kuni ichida arxivga topshiriladi
    """,

    # ── Markaziy bank prudensial nazorat ─────────────────────────────────────
    """
    Markaziy bank prudensial nazorat talablari (2023-yil yanvardagi ko'rsatkichlar).

    Majburiy nazorat ko'rsatkichlari:

    Kapital yetarliligi:
    - Kapital yetarliligi koeffitsienti (CAR): kamida 13%
    - 1-darajali kapital (Tier 1): kamida 9%
    - Umumiy kapital: kamida 13%

    Likvidlik:
    - Likvidlik qoplash koeffitsienti (LCR): kamida 100%
    - Xolis barqaror moliyalashtirish koeffitsienti (NSFR): kamida 100%
    - Joriy likvidlik: kamida 30%

    Kredit riski:
    - Muddati o'tgan kreditlar (NPL): 5% dan oshmasligi kerak
    - Yirik kredit risklari: kapitalning 25% dan oshmasligi
    - Bir qarzdorga: kapitalning 15% dan oshmasligi

    Hisobot jadvali:
    - Kunlik: likvidlik ko'rsatkichlari
    - Oylik: balans, P&L, kapital, kreditlar
    - Choraklik: prudensial ko'rsatkichlar majmui
    - Yillik: audit xulosasi bilan moliyaviy hisobot

    Nazorat so'roviga javob muddati: 5 ish kuni (odatiy), 24 soat (favqulodda).
    Javobda: aniq raqamlar, hisob-kitob metodologiyasi, imzoli va muhrli.

    Nazorat topilmalari bo'yicha:
    - Xato aniqlangan taqdirda: 30 kun ichida tuzatish rejasi taqdim etiladi
    - Qayta tekshiruv muddati kelishiladi
    """,

    # ── Fuqarolik kodeksi (kredit va kafillik) ───────────────────────────────
    """
    O'zbekiston Respublikasi Fuqarolik kodeksi.

    Banks va kredit munosabatlari bo'limidan:

    734-modda. Bank kreditlash shartnomasi:
    Bank kredit shartnomasi yozma shaklda tuziladi.
    Shartnomada: miqdor, muddat, foiz stavkasi, qaytarish tartibi ko'rsatiladi.
    Kredit shartnomasiga o'zgartirish faqat ikki tomon kelishuvida.

    735-modda. Kredit berish:
    Bank kredit berish yoki bermaslikni asoslash shart emas.
    Kredit berishdan bosh tortish — shartnoma tuzmaslik huquqi.

    736-modda. Kredit foizi:
    Foiz stavkasi shartnomada belgilanadi.
    O'zgaruvchi stavka oldindan kelishilishi shart.

    757-modda. Kafillik:
    Kafil asosiy qarzdor bilan birgalikda javobgar.
    Bank kafilga da'vo qilishda asosiy qarzdorga da'vo qilmay ham.

    Hisob raqam ochish va yuritish:

    815-modda. Bank hisob raqami shartnomasi:
    Bank mijozning barcha to'lovlarini o'z vaqtida bajarishi shart.
    Mijozning ruxsatisiz hisob raqam muddatidan oldin yopilmaydi.

    816-modda. Hisob raqamni bloklash:
    Sud qarorisiz bloklash — faqat qonunda nazarda tutilgan hollarda.
    Bloklash haqida mijoz darhol xabardor qilinishi shart (agar maxfiylik talabi bo'lmasa).
    """,

    # ── Javob shablonlari ────────────────────────────────────────────────────
    """
    Rasmiy javob shablonlari — SQB Bank Yuridik Bo'limi.

    SHABLON 1: Prokuratura so'roviga javob
    ======================================
    [Chiquvchi raqam] [Sana]
    [Prokuratura nomi va manzili]
    [Tergovchi/prokuror ismi va lavozimi]

    Sizning [sana]dagi [raqam]-son talabnoмangizga javoban,

    "O'zbekiston Sanoat-Qurilish Banki" AJ quyidagilarni ma'lum qiladi:

    O'zbekiston Respublikasi Jinoyat-protsessual kodeksining 178-moddasi va
    "Bank siri to'g'risida"gi Qonunning 5-moddasiga muvofiq...

    [Asosiy qism]

    Tegishli ma'lumotlar [muddat] ish kuni ichida taqdim etiladi.
    Qo'shimcha ma'lumot uchun: Yuridik bo'lim, tel: [telefon].

    Hurmat bilan,
    [Lavozim, Familiya, Ism]
    "O'zbekiston Sanoat-Qurilish Banki" AJ

    SHABLON 2: Soliq organiga javob
    ================================
    O'zbekiston Respublikasi Soliq Kodeksining 86-moddasi asosida...
    Belgilangan ma'lumotlar [muddat] ish kuni ichida taqdim etiladi.

    SHABLON 3: Markaziy bankka javob
    ==================================
    Markaziy bank yo'riqnomasi talablariga muvofiq...
    So'ralgan prudensial ko'rsatkichlar [muddat] ish kuni ichida taqdim etiladi.

    UMUMIY TAMOYILLAR:
    - Barcha javoblar kamida 4 paragraf bo'lishi shart
    - Qonun moddalari to'liq va aniq ko'rsatilishi shart
    - Muddat har doim ko'rsatilishi shart
    - Cheklovlar (bank siri) aniq ko'rsatilishi shart
    - Hamkorlikka tayyorlik ta'kidlanishi shart
    """,
]