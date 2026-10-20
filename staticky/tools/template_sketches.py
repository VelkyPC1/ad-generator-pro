"""
Náčrty 40 Motion templatov pre tab „Templaty a štýly" v dashboarde.

Každý template = mini banner v HTML/CSS (žiadne obrázky, žiadne API). Rozloženie zodpovedá
receptu v 04-brief-template-copy-prompts/01-templates-by-motion/<NN>-*.md — kde je produkt,
nadpis, recenzia, cena, CTA. Všetko je v percentách a cqw, takže náčrt škáluje s kartou.

Keď v `template-previews/<NN>.png` (alebo .jpg) existuje AI ukážka, dashboard ju ukáže
namiesto náčrtu (náčrt ostane dostupný prepínačom).
"""

CATEGORIES = [
    ("offer", "Ponuka a zľava"),
    ("proof", "Recenzie a social proof"),
    ("compare", "Porovnanie a pred / po"),
    ("product", "Produkt a benefity"),
    ("native", "UGC a native"),
    ("editorial", "Headline a editorial"),
    ("new", "Nové / nezaradené"),
]

CATEGORY_OF = {
    2: "offer", 14: "offer", 30: "offer", 35: "offer", 37: "offer",
    3: "proof", 6: "proof", 9: "proof", 11: "proof", 15: "proof", 16: "proof",
    17: "proof", 19: "proof", 24: "proof", 38: "proof",
    7: "compare", 8: "compare", 25: "compare", 31: "compare", 36: "compare",
    4: "product", 5: "product", 12: "product", 13: "product", 18: "product",
    22: "product", 26: "product", 27: "product", 28: "product",
    29: "native", 32: "native", 33: "native", 34: "native", 39: "native", 40: "native",
    1: "editorial", 10: "editorial", 20: "editorial", 21: "editorial", 23: "editorial",
}


def b(cls, x, y, w, h, inner="", style=""):
    """Absolútne umiestnený blok — x, y, w, h v percentách plochy banneru."""
    size = f"left:{x}%;top:{y}%;width:{w}%;" + (f"height:{h}%;" if h else "")
    return f'<div class="{cls}" style="{size}{style}">{inner}</div>'


def lines(n, width=100, gap=1.2):
    """n šedých riadkov textu (telo copy)."""
    out = []
    for i in range(n):
        w = width if i < n - 1 else width * 0.6
        out.append(f'<i class="ln" style="width:{w}%;margin-top:{gap}cqw"></i>')
    return "".join(out)


def checks(items, mark="✓", cls="ok"):
    return "".join(f'<div class="li"><b class="{cls}">{mark}</b>{t}</div>' for t in items)


STARS = '<span class="stars">★★★★★</span>'
PROD = "prod"            # produkt
PROD_BOX = "prod box"     # krabička


SKETCHES = {
    # ---------------- Headline a editorial ----------------
    1: ("9:16", "bg-photo", (
        b("ph person", 0, 0, 100, 100)
        + b("t xl", 8, 10, 84, 0, "Jedna veta,<br>ktorá predá.")
        + b(PROD, 58, 62, 26, 26)
    )),
    10: ("4:5", "bg-linen", (
        b("t xs caps center", 0, 6, 100, 0, "As featured in")
        + b("logos", 10, 12, 80, 6, "<span>VOGUE</span><span>ELLE</span><span>GQ</span><span>Forbes</span>")
        + b("t serif it md center", 10, 26, 80, 0, "„Najlepší produkt,<br>aký sme tento rok testovali.“")
        + b("t xs center muted", 0, 50, 100, 0, "— Redakcia magazínu")
        + b(PROD, 40, 62, 20, 32)
    )),
    20: ("4:5", "bg-dark", (
        b("ph person moody", 0, 0, 100, 100)
        + b("pill tag", 8, 52, 30, 0, "HOT TOPIC")
        + b("t xl caps cond white", 8, 60, 86, 0, "Prečo o tom<br>nikto nehovorí")
        + b("t xs white muted", 8, 90, 60, 0, "@znacka")
    )),
    21: ("1:1", "bg-gradient", (
        b("t xl retro white", 6, 8, 62, 0, "Toto<br>chceš.")
        + b("hand", 62, 0, 30, 40, "", "transform:rotate(200deg)")
        + b(PROD, 56, 38, 28, 52)
    )),
    23: ("1:1", "bg-white", (
        b("t lg", 8, 8, 84, 0, "Áno, je drahší.")
        + b("manifest", 8, 26, 84, 0, "Lebo nešetríme na zložení.<br>Lebo vydrží dvakrát dlhšie.<br>Lebo to cítiť.<br><b>Za kvalitu sa neospravedlňujeme.</b>")
        + b(PROD, 44, 74, 12, 22)
    )),

    # ---------------- Ponuka a zľava ----------------
    2: ("9:16", "bg-split", (
        b("t xxl white", 8, 8, 84, 0, "-30 %<br><small>na všetko</small>")
        + b(PROD, 30, 40, 40, 40)
        + b("cta", 20, 86, 60, 0, "Chcem zľavu")
    )),
    14: ("1:1", "bg-gradient-soft", (
        b("benefitbar", 6, 8, 88, 10, "<span>🌿</span><span>💧</span><span>✨</span><span>🛡</span><span>⏱</span>")
        + b("gift", 18, 28, 64, 50, b(PROD, 10, 10, 22, 70) + b(PROD, 39, 6, 22, 74) + b(PROD, 68, 10, 22, 70))
        + b("hand", 0, 70, 30, 30)
        + b("t sm center", 0, 84, 100, 0, "Celá rutina v jednom balení")
    )),
    30: ("1:1", "bg-white", (
        b("banner-white t lg caps center", 0, 3, 100, 0, "Silný výrok.")
        + b("ph warm", 6, 18, 88, 52, b(PROD, 38, 22, 24, 70))
        + b("iconbar", 0, 72, 100, 18, "<span>⚡<br><small>Energia</small></span><span>🌱<br><small>Prírodné</small></span><span>✓<br><small>Overené</small></span>")
        + b("ticker", 0, 91, 100, 9, "★ 4,9 · 12 000 zákazníkov · ★ 4,9 · doprava zdarma")
    )),
    35: ("1:1", "bg-cream", (
        b("t md caps center", 6, 6, 88, 0, "Najlepší vo svojej triede")
        + b("cta", 34, 23, 32, 0, "Kúpiť")
        + b("crumbs", 20, 40, 60, 42)
        + b(PROD, 39, 41, 22, 38)
        + b("statpill", 8, 84, 84, 10, "<span><b>15 g</b> proteín</span><span><b>2 g</b> cukor</span><span><b>180</b> kcal</span>")
    )),
    37: ("1:1", "bg-dark", (
        b("banner-white t lg caps center", 0, 3, 100, 0, "Silný výrok.")
        + b("burst", 66, 18, 26, 26, "-40 %")
        + b("hand", 34, 20, 32, 30)
        + b(PROD, 38, 30, 24, 46)
        + b("iconbar dark", 0, 74, 100, 15, "<span>⚡<br><small>Rýchle</small></span><span>🌱<br><small>Čisté</small></span><span>✓<br><small>Overené</small></span>")
        + b("ticker", 0, 91, 100, 9, "ZĽAVA LEN TENTO TÝŽDEŇ · ZĽAVA LEN TENTO TÝŽDEŇ")
    )),

    # ---------------- Recenzie a social proof ----------------
    3: ("9:16", "bg-photo", (
        b("ph room", 0, 0, 100, 100, b(PROD + " blur", 62, 44, 26, 22))
        + b("quote-panel", 7, 8, 86, 0,
            '<div class="t md white">„Konečne niečo, čo funguje.“</div>'
            + '<div style="margin-top:2cqw">' + lines(3) + '</div>'
            + f'<div class="t xs white" style="margin-top:3cqw">Jana K. · zdravotná sestra {STARS}</div>')
    )),
    6: ("4:5", "bg-cream", (
        b("t md center", 6, 5, 88, 0, "Pridajte sa k 50 000+ ženám")
        + b("t sm center", 0, 19, 100, 0, STARS + " 4,9 / 5")
        + b(PROD, 38, 26, 24, 34)
        + b("card", 10, 62, 80, 18, f'{STARS}<div class="t xs" style="margin-top:1cqw">„Najlepšia kúpa tohto roka.“</div>' + lines(1))
        + b("logos", 8, 86, 84, 7, "<span>VOGUE</span><span>ELLE</span><span>Forbes</span>")
    )),
    9: ("4:5", "bg-photo", (
        b("ph warm", 0, 0, 100, 100, b(PROD, 60, 50, 26, 34))
        + b("card", 8, 10, 74, 36, '<span class="stars one">★☆☆☆☆</span>'
            + '<div class="t sm" style="margin-top:1.5cqw">„Neviem tomu uveriť. Som naštvaná…</div>'
            + '<div class="t xs muted" style="margin-top:1cqw">…že mi o ňom nikto nepovedal skôr.“</div>')
        + b("t lg caps white center", 0, 84, 100, 0, "Recenzie sú tu.")
    )),
    11: ("1:1", "bg-cream", (
        b("t serif it lg", 7, 7, 86, 0, "„Prvýkrát po rokoch som sa cítila sama sebou.“")
        + b("card", 7, 50, 66, 40, f'{STARS}' + lines(3) + '<div class="t xs accent" style="margin-top:1.5cqw">…Čítať ďalej</div>')
        + b(PROD, 68, 46, 24, 46)
    )),
    15: ("1:1", "bg-white", (
        b("t lg", 7, 6, 86, 0, "Toto mi napísala zákazníčka")
        + b("fbcomment", 7, 28, 86, 26, '<i class="av"></i><div><b>Lucia M.</b>' + lines(2) + '<div class="t xs muted">Páči sa mi to · Odpovedať · 2 h</div></div>')
        + b(PROD, 38, 58, 24, 40)
    )),
    16: ("1:1", "bg-cream", (
        b("t serif it sm center", 0, 7, 100, 0, "Úprimne?")
        + b("t xxl caps center", 4, 15, 92, 0, "Robila som<br>to zle")
        + b("t sm center", 8, 46, 84, 0, "roky — až kým som neskúsila toto.")
        + b(PROD, 14, 62, 20, 34)
        + b("badge", 40, 66, 18, 18, "100 %<br><small>prírodné</small>")
        + b("card", 62, 68, 32, 18, f'{STARS}<div class="t xs">2 400 recenzií</div>')
    )),
    17: ("1:1", "bg-accent", (
        b("t lg white", 7, 6, 86, 0, "„Toto som potrebovala.“")
        + b("t sm", 7, 24, 50, 0, '<span class="stars">★★★★★</span>')
        + b("card", 7, 34, 70, 58, '<div class="review-head"><i class="av"></i><b>Petra S.</b><span class="verified">✓ Overený nákup</span></div>'
            + lines(4) + '<div class="t xs accent" style="margin-top:1.5cqw">Čítať ďalej</div>'
            + '<div class="t xs muted" style="margin-top:1cqw">👍 Užitočné (48)</div>')
        + b(PROD, 68, 40, 26, 50)
    )),
    19: ("1:1", "bg-white", (
        b("review-head", 7, 6, 86, 8, '<i class="av"></i><b>Martina, 34</b>')
        + b("t md", 7, 20, 86, 0, 'Skúšala som všetko. <mark>Až toto mi reálne pomohlo</mark> a po dvoch týždňoch <mark>som videla rozdiel</mark>. Odporúčam každej.')
        + b(PROD, 70, 60, 22, 36)
        + b("badge", 50, 72, 16, 16, "✓<br><small>overené</small>")
    )),
    24: ("1:1", "bg-white", (
        b("studio", 0, 0, 100, 55, b(PROD, 38, 10, 24, 82))
        + b("fbcomment", 6, 60, 88, 34, '<i class="av"></i><div><b>Katka Nováková</b>' + lines(2) + '<div class="t xs muted">❤️👍 128 · 3 h</div></div>')
    )),
    38: ("4:5", "bg-white", (
        b("ph person warm", 0, 0, 55, 100)
        + b("accent-panel", 55, 0, 45, 100, b(PROD, 28, 8, 44, 40)
            + b("card", 8, 54, 84, 36, f'{STARS}<div class="t xs" style="margin-top:1cqw">„Milujem ho.“</div>' + lines(1) + '<div class="t xs muted">LOGO</div>'))
    )),

    # ---------------- Porovnanie a pred / po ----------------
    7: ("4:5", "bg-white", (
        b("col-them", 0, 0, 50, 100, '<div class="t xs caps center muted">Bežné produkty</div>'
            + b("prod gray", 30, 12, 40, 30) + b("list", 8, 50, 86, 0, checks(["Chémia", "Rýchlo vyprchá", "Drahé"], "✕", "no")))
        + b("col-us", 50, 0, 50, 100, '<div class="t xs caps center white">Naša značka</div>'
            + b(PROD, 30, 12, 40, 30) + b("list white", 8, 50, 86, 0, checks(["Prírodné", "Vydrží týždne", "Výhodné"])))
        + b("vs", 42, 4, 16, 0, "VS")
    )),
    25: ("1:1", "bg-white", (
        b("col-us vivid", 0, 0, 52, 100, b(PROD, 28, 8, 44, 40) + b("splash", 20, 44, 60, 8)
            + b("list white", 8, 58, 86, 0, checks(["Lepšia chuť", "Menej cukru", "Viac bielkovín", "Čisté zloženie"])))
        + b("col-them cream", 52, 0, 48, 100, b("prod gray", 30, 10, 40, 36)
            + b("list", 8, 58, 86, 0, checks(["Umelé arómy", "Veľa cukru", "Málo bielkovín", "Konzervanty"], "✕", "no")))
        + b("burst small", 40, 34, 20, 20, "VS")
    )),
    31: ("1:1", "bg-white", (
        b("grid2", 4, 4, 92, 92, '<div class="cell head">' + b(PROD, 34, 8, 32, 84) + '</div><div class="cell head">' + b("prod gray", 34, 8, 32, 84) + '</div>'
            + "".join(f'<div class="cell"><b>{a}</b></div><div class="cell">{c}</div>' for a, c in (("Vydrží 2 roky", "Vydrží pol roka"), ("Bez chémie", "Chémia"), ("Doprava zdarma", "Doprava 5 €"))))
    )),
    8: ("9:16", "bg-white", (
        b("ph selfie dim", 0, 0, 100, 50, b("handwrite", 6, 80, 40, 0, "1. deň"))
        + b("ph selfie bright", 0, 50, 100, 50, b("handwrite", 6, 80, 40, 0, "30. deň"))
        + b("divider", 0, 49.5, 100, 1)
    )),
    36: ("4:5", "bg-photo", (
        b("ph kitchen", 0, 0, 100, 100)
        + b("whiteboard", 12, 10, 56, 38, '<div class="wb"><span>☹</span><span class="arr">→</span><span>☺</span></div><div class="handwrite dark">Vyskúšaj 30 dní</div>')
        + b("hand", 52, 52, 40, 48)
        + b(PROD, 60, 40, 22, 40)
    )),

    # ---------------- Produkt a benefity ----------------
    4: ("4:5", "bg-white", (
        b(PROD, 38, 30, 24, 40)
        + b("callout", 4, 12, 30, 12, "<b>Vitamín C</b><br>žiarivá pleť") + b("line-c", 34, 20, 10, 0, "", "transform:rotate(25deg)")
        + b("callout", 66, 12, 30, 12, "<b>Bez umelých farbív</b><br>prírodné zloženie") + b("line-c", 56, 20, 10, 0, "", "transform:rotate(-25deg)")
        + b("callout", 4, 74, 30, 12, "<b>50 ml</b><br>na 3 mesiace") + b("line-c", 34, 74, 10, 0, "", "transform:rotate(-25deg)")
        + b("callout", 66, 74, 30, 12, "<b>Vegan</b><br>bez testov") + b("line-c", 56, 74, 10, 0, "", "transform:rotate(25deg)")
    )),
    5: ("4:5", "bg-cream", (
        b(PROD, 8, 22, 30, 56)
        + b("t md", 44, 10, 52, 0, "Prečo práve my")
        + b("list dots", 44, 26, 52, 0, checks(["Vydrží roky", "Jemný k pokožke", "Bez zbytočnej chémie", "Doprava zdarma", "Vyrobené v EÚ"], "●", "dot"))
    )),
    12: ("1:1", "bg-white", (
        b("ph person action", 0, 0, 68, 100)
        + b("t md white", 5, 6, 58, 0, "„Bez neho už nikam.“")
        + b("fan", 52, 50, 46, 46, b("prod c1", 0, 20, 30, 70, "", "transform:rotate(-14deg)") + b("prod c2", 34, 10, 30, 80) + b("prod c3", 66, 20, 30, 70, "", "transform:rotate(14deg)"))
    )),
    13: ("1:1", "bg-gradient-soft", (
        b(PROD, 38, 28, 24, 46)
        + b("stat", 4, 6, 28, 0, "<b>15 g</b><small>proteínu</small>") + b("stat", 68, 6, 28, 0, "<b>0 g</b><small>cukru</small>")
        + b("stat", 4, 70, 28, 0, "<b>180</b><small>kcal</small>") + b("stat", 68, 70, 28, 0, "<b>100 %</b><small>prírodné</small>")
        + b("pricebadge", 60, 46, 18, 18, "2,99 €")
        + b("crumbs", 26, 76, 48, 16)
    )),
    18: ("1:1", "bg-white", (
        b("banner-accent t sm white center", 0, 0, 100, 0, "Chutí ako dezert, pomáha ako vitamín")
        + b("props", 0, 10, 100, 90)
        + b("hand", 34, 36, 32, 40)
        + b(PROD, 40, 28, 20, 38)
        + b("stat", 4, 18, 26, 0, "<b>15 g</b><small>proteínu</small>") + b("stat", 70, 18, 26, 0, "<b>0 g</b><small>cukru</small>")
        + b("stat", 4, 72, 26, 0, "<b>8</b><small>vitamínov</small>") + b("stat", 70, 72, 26, 0, "<b>180</b><small>kcal</small>")
    )),
    22: ("1:1", "bg-photo", (
        b("ph food", 0, 0, 100, 100)
        + b("t lg white center", 6, 6, 88, 0, "Chutí ako malinová šiška")
        + b(PROD, 38, 34, 24, 44, "", "transform:rotate(-12deg)")
        + b("statpill", 6, 86, 88, 9, "<span><b>15 g</b> proteín</span><span><b>2 g</b> cukor</span><span><b>180</b> kcal</span>")
    )),
    26: ("4:5", "bg-dark", (
        b("ph warm hands", 0, 0, 100, 50, b(PROD, 40, 20, 20, 70))
        + b("divider-logo", 0, 49, 100, 0, "LOGO")
        + b("t lg caps white", 8, 58, 84, 0, "Po prechode <span class='accent2'>87 %</span> zákazníčok spí lepšie")
        + b("t xs white muted", 8, 88, 84, 0, "Prieskum medzi 1 200 používateľkami")
    )),
    27: ("1:1", "bg-white", (
        b("overhead", 0, 0, 45, 100, b("bowl", 10, 22, 80, 56, "<span>A</span><span>B</span><span>C</span><span>D</span>"))
        + b("info", 50, 8, 46, 0, f'{STARS}<div class="t xs muted">2 100 recenzií</div><div class="t xs caps" style="margin:2cqw 0">LOGO</div>'
            + '<div class="t md accent">Všetko v jednom</div>'
            + '<div class="list" style="margin-top:2cqw">' + checks(["Rýchla príprava", "Bez lepku", "Na celý týždeň"]) + '</div>'
            + '<div class="cta" style="position:static;margin-top:3cqw">Objednať</div>')
    )),
    28: ("1:1", "bg-cream", (
        b("t serif it sm center", 0, 5, 100, 0, "Konečne")
        + b("t lg caps center", 0, 12, 100, 0, "Všetko v jednom")
        + b("hand", 34, 52, 32, 36)
        + b(PROD, 40, 36, 20, 40)
        + b("callout", 4, 34, 26, 0, "Hydratuje") + b("callout", 70, 34, 26, 0, "Chráni")
        + b("callout", 4, 62, 26, 0, "Ľahký") + b("callout", 70, 62, 26, 0, "Šetrí čas")
        + b("banner-accent t sm white center", 0, 89, 100, 11, "-20 % s kódom LETO")
    )),

    # ---------------- UGC a native ----------------
    29: ("9:16", "bg-photo", (
        b("ph selfie", 0, 0, 100, 100)
        + b("tweet", 8, 34, 84, 26, '<div class="review-head"><i class="av"></i><b>Anna</b><span class="muted"> @anna</span></div>'
            + '<div class="t sm" style="margin-top:1.5cqw">Nepopulárny názor: drahšie neznamená lepšie.</div>'
            + '<div class="t xs muted" style="margin-top:1.5cqw">♡ 12,4 tis. · ↻ 1 800</div>')
    )),
    32: ("9:16", "bg-photo", (
        b("ph desk", 0, 0, 100, 100, b("hand", 30, 40, 40, 30) + b(PROD, 38, 34, 24, 26))
        + b("bubble c1", 6, 6, 60, 0, "Téma: spánok 😴") + b("bubble c2", 30, 16, 64, 0, "Toto mi zmenilo večery")
        + b("bubble c3", 6, 66, 70, 0, "Prečo práve toto? 👇") + b("bubble c4", 24, 76, 70, 0, "Po týždni zaspávam za 10 min")
        + b("bubble c5", 10, 87, 60, 0, "Odporúčam ✨")
    )),
    33: ("4:5", "bg-white", (
        b("masthead", 0, 0, 100, 10, "DAILY NEWS")
        + b("t xs caps muted", 6, 12, 60, 0, "Latest headlines")
        + b("t serif md", 6, 17, 88, 0, "Ženy hromadne menia rutinu — a tento produkt je dôvod")
        + b("ph selfie", 4, 40, 45, 56) + b("ph selfie bright", 51, 40, 45, 56)
    )),
    34: ("1:1", "bg-white", (
        b("ios", 0, 0, 100, 7, "<span>9:41</span><span>●●● 📶 🔋</span>")
        + b("notesbar", 0, 7, 100, 7, "<span>‹ Poznámky</span><span>Hotovo</span>")
        + b("t xs muted center", 0, 16, 100, 0, "15. októbra 2026 9:41")
        + b("t serif lg", 7, 23, 70, 0, "Prečo to beriem každý deň")
        + b("list", 7, 46, 62, 0, checks(["Viac vitamínu D než 800 húb", "Menej cukru než jablko", "Bielkoviny ako 3 vajcia"]))
        + b(PROD, 74, 46, 24, 48)
    )),
    39: ("1:1", "bg-white", (
        b("t md", 7, 8, 86, 0, 'Ak ťa to každé ráno zdržiava, nie je to tým, že… <span class="muted">viac</span>')
        + b("ph closeup", 0, 36, 100, 64)
    )),
    40: ("4:5", "bg-photo", (
        b("ph floor", 0, 0, 100, 100)
        + b(PROD, 34, 30, 32, 50, "", "transform:rotate(-4deg)")
        + b("postit", 30, 36, 40, 26, "Funguje to.<br>Fakt.<br>— M.", "transform:rotate(6deg)")
    )),
}


CSS = """
  /* ---------- Náčrty templatov (mini bannery, škálujú cez cqw) ---------- */
  .mk { container-type: inline-size; position: relative; overflow: hidden; height: 100%; width: auto; border-radius: 10px; background: #f4f1ec; color: #1d1d1f; font-family: -apple-system, 'SF Pro Text', system-ui, sans-serif; box-shadow: 0 1px 2px rgba(0,0,0,0.15), 0 8px 22px rgba(0,0,0,0.12); --a: #5E5CE6; --a2: #FF9F0A; --ok: #34C759; --no: #FF3B30; }
  .mk > div, .mk div[style*="left"] { position: absolute; }
  .mk .t { line-height: 1.08; letter-spacing: -0.01em; }
  .mk .xs { font-size: 4.2cqw; } .mk .sm { font-size: 5.2cqw; } .mk .md { font-size: 6.6cqw; font-weight: 700; }
  .mk .lg { font-size: 8.4cqw; font-weight: 800; } .mk .xl { font-size: 11cqw; font-weight: 800; } .mk .xxl { font-size: 13cqw; font-weight: 900; letter-spacing: -0.03em; }
  .mk .caps { text-transform: uppercase; } .mk .center { text-align: center; } .mk .white { color: #fff; } .mk .muted { opacity: 0.6; }
  .mk .accent { color: var(--a); } .mk .accent2 { color: var(--a2); }
  .mk .serif { font-family: 'New York', Georgia, 'Times New Roman', serif; font-weight: 600; } .mk .it { font-style: italic; }
  .mk .cond { font-stretch: condensed; letter-spacing: -0.04em; } .mk .retro { font-family: 'Cooper Black', 'Arial Rounded MT Bold', ui-rounded, sans-serif; }
  .mk small { font-size: 0.55em; font-weight: 600; }
  .mk .ln { display: block; height: 1.7cqw; border-radius: 1cqw; background: rgba(0,0,0,0.16); }
  .mk .white .ln, .mk .quote-panel .ln { background: rgba(255,255,255,0.55); }

  /* pozadia */
  .mk.bg-white { background: #fff; } .mk.bg-cream { background: #f6efe4; } .mk.bg-linen { background: #efe9df; }
  .mk.bg-dark { background: #1c1c22; } .mk.bg-accent { background: var(--a); }
  .mk.bg-gradient { background: linear-gradient(135deg, #ff7a59, #ff3d8b 55%, #8a5cff); }
  .mk.bg-gradient-soft { background: linear-gradient(160deg, #fdf3e7, #f3e3f6); }
  .mk.bg-split { background: linear-gradient(180deg, var(--a) 0 52%, #ffd8a8 52%); }
  .mk.bg-photo { background: #cdb9a5; }

  /* foto plochy (náznak fotky) */
  .mk .ph { background: linear-gradient(160deg, #d9c2ab, #a98a72); overflow: hidden; }
  .mk .ph.warm { background: linear-gradient(160deg, #f1d6bd, #c99a78); }
  .mk .ph.moody { background: linear-gradient(170deg, #4a4e5a, #15161b); }
  .mk .ph.room { background: linear-gradient(170deg, #e8e2d8 0 60%, #cfc3b3 60%); }
  .mk .ph.kitchen { background: linear-gradient(180deg, #f3efe8 0 55%, #d8cbb8 55%); }
  .mk .ph.desk { background: linear-gradient(160deg, #c7b39c, #8f735d); }
  .mk .ph.floor { background: linear-gradient(180deg, #ddd3c6 0 40%, #b79e83 40%); }
  .mk .ph.food { background: radial-gradient(circle at 30% 35%, #f6a5c0 0 18%, transparent 19%), radial-gradient(circle at 72% 62%, #e88aa8 0 20%, transparent 21%), radial-gradient(circle at 20% 80%, #7b3f2a 0 14%, transparent 15%), linear-gradient(160deg, #f7d9c4, #d99a7c); }
  .mk .ph.closeup { background: radial-gradient(ellipse at 50% 50%, #e9c3a8, #b47e62); }
  .mk .ph.selfie { background: linear-gradient(170deg, #cbb8a6, #9c8471); }
  .mk .ph.dim { filter: saturate(0.4) brightness(0.75) contrast(0.9); }
  .mk .ph.bright { filter: saturate(1.2) brightness(1.12); }
  .mk .ph.hands { background: linear-gradient(160deg, #f4d2b5, #c88f6c); }
  .mk .person::after, .mk .ph.selfie::after, .mk .ph.action::after { content: ''; position: absolute; left: 50%; bottom: 0; width: 64%; height: 78%; transform: translateX(-50%); background: radial-gradient(circle at 50% 24%, #f1cdb0 0 15%, transparent 15.5%), radial-gradient(ellipse at 50% 100%, #8e5a63 0 48%, transparent 49%); }
  .mk .ph.moody::after { filter: brightness(0.55); }
  .mk .ph.action::after { left: 40%; transform: translateX(-50%) rotate(-8deg); }

  /* produkt */
  .mk .prod { border-radius: 22% 22% 14% 14% / 14% 14% 8% 8%; background: linear-gradient(90deg, #ffffff, #ece9f8 60%, #d9d4ef); box-shadow: 0 2cqw 4cqw rgba(0,0,0,0.25); }
  .mk .prod::before { content: ''; position: absolute; left: 30%; width: 40%; top: -12%; height: 14%; border-radius: 1.2cqw 1.2cqw 0 0; background: #2c2c34; }
  .mk .prod::after { content: ''; position: absolute; left: 12%; right: 12%; top: 38%; height: 28%; border-radius: 1cqw; background: var(--a); opacity: 0.9; }
  .mk .prod.gray { background: linear-gradient(90deg, #f1f1f1, #cfcfcf); filter: grayscale(1); opacity: 0.85; }
  .mk .prod.gray::after { background: #9a9a9a; }
  .mk .prod.blur { filter: blur(0.6cqw); }
  .mk .prod.c1::after { background: #FF9F0A; } .mk .prod.c2::after { background: #34C759; } .mk .prod.c3::after { background: #FF375F; }
  .mk .hand { border-radius: 45% 45% 40% 40%; background: linear-gradient(180deg, #f2c9a8, #dba47f); opacity: 0.95; }

  /* UI prvky */
  .mk .cta { background: var(--a); color: #fff; font-weight: 700; font-size: 5cqw; text-align: center; padding: 2.6cqw 0; border-radius: 99px; }
  .mk .pill { background: #fff; color: #111; font-size: 3.8cqw; font-weight: 800; text-align: center; padding: 1.2cqw 0; border-radius: 99px; }
  .mk .stars { color: #FFB800; letter-spacing: 0.08em; font-size: 4.6cqw; }
  .mk .stars.one { color: #FFB800; }
  .mk .card { background: #fff; border-radius: 3cqw; padding: 3cqw; box-shadow: 0 1.5cqw 4cqw rgba(0,0,0,0.16); }
  .mk .card .ln { background: rgba(0,0,0,0.14); }
  .mk .quote-panel { background: rgba(20,20,26,0.55); border-radius: 3cqw; padding: 4cqw; backdrop-filter: blur(4px); }
  .mk .review-head { display: flex; align-items: center; gap: 2cqw; font-size: 4.4cqw; }
  .mk .av, .mk .fbcomment .av { display: inline-block; width: 8cqw; height: 8cqw; border-radius: 50%; background: radial-gradient(circle at 50% 38%, #f1cdb0 0 30%, #8e5a63 31%); flex: 0 0 auto; }
  .mk .verified { margin-left: auto; color: var(--ok); font-size: 3.6cqw; font-weight: 700; }
  .mk .fbcomment { background: #f0f2f5; border-radius: 4cqw; padding: 3cqw; display: flex; gap: 2.4cqw; font-size: 4.4cqw; }
  .mk .fbcomment > div { flex: 1; }
  .mk .tweet { background: #fff; border-radius: 3cqw; padding: 3.4cqw; box-shadow: 0 2cqw 6cqw rgba(0,0,0,0.3); }
  .mk .list .li { font-size: 4.6cqw; font-weight: 600; margin-top: 1.8cqw; display: flex; gap: 1.6cqw; align-items: baseline; }
  .mk .list.white .li { color: #fff; }
  .mk .li b.ok { color: var(--ok); } .mk .li b.no { color: var(--no); } .mk .li b.dot { color: var(--a); font-size: 0.8em; }
  .mk .list.white .li b.ok { color: #fff; }
  .mk .vs { background: #111; color: #fff; font-weight: 900; font-size: 5cqw; text-align: center; border-radius: 99px; padding: 1.4cqw 0; }
  .mk .burst { background: var(--a2); color: #111; font-weight: 900; font-size: 6cqw; display: flex; align-items: center; justify-content: center; transform: rotate(-12deg); clip-path: polygon(50% 0, 61% 18%, 82% 8%, 79% 30%, 100% 36%, 84% 52%, 98% 70%, 76% 72%, 76% 95%, 58% 82%, 44% 100%, 38% 79%, 15% 90%, 20% 66%, 0 58%, 18% 44%, 6% 22%, 29% 22%, 32% 0); }
  .mk .burst.small { font-size: 5cqw; transform: none; }
  .mk .badge { border-radius: 50%; background: #fff; border: 0.6cqw solid var(--a); color: var(--a); font-weight: 800; font-size: 3.6cqw; display: flex; align-items: center; justify-content: center; text-align: center; line-height: 1.05; }
  .mk .pricebadge { border-radius: 50%; background: var(--a2); color: #111; font-weight: 900; font-size: 4cqw; display: flex; align-items: center; justify-content: center; }
  .mk .logos { display: flex; justify-content: space-between; align-items: center; font-family: Georgia, serif; font-weight: 700; font-size: 4.4cqw; color: #8a8a8a; letter-spacing: 0.04em; }
  .mk .manifest { font-size: 5cqw; line-height: 1.5; }
  .mk .banner-white { background: #fff; color: #111; padding: 2.4cqw 0; }
  .mk .banner-accent { background: var(--a); padding: 2.4cqw 0; display: flex; align-items: center; justify-content: center; }
  .mk .iconbar { background: color-mix(in srgb, var(--a) 18%, #fff); display: flex; justify-content: space-around; align-items: center; text-align: center; font-size: 6cqw; line-height: 1.1; }
  .mk .iconbar.dark { background: rgba(255,255,255,0.12); color: #fff; }
  .mk .iconbar small { font-size: 3.4cqw; font-weight: 700; }
  .mk .ticker { background: #111; color: #fff; font-size: 3.4cqw; font-weight: 700; white-space: nowrap; overflow: hidden; display: flex; align-items: center; padding-left: 2cqw; }
  .mk .benefitbar { background: #fff; border-radius: 99px; display: flex; justify-content: space-around; align-items: center; font-size: 5cqw; box-shadow: 0 1cqw 3cqw rgba(0,0,0,0.1); }
  .mk .gift { background: linear-gradient(180deg, #f9e1ea, #f1c7d6); border-radius: 3cqw; box-shadow: inset 0 3cqw 0 rgba(0,0,0,0.06), 0 2cqw 5cqw rgba(0,0,0,0.15); }
  .mk .statpill { background: #fff; border-radius: 99px; display: flex; justify-content: space-around; align-items: center; font-size: 3.8cqw; box-shadow: 0 1cqw 3cqw rgba(0,0,0,0.12); }
  .mk .stat { text-align: center; line-height: 1; }
  .mk .stat b { display: block; font-size: 8cqw; font-weight: 900; letter-spacing: -0.03em; color: var(--a); }
  .mk .stat small { font-size: 3.6cqw; font-weight: 700; }
  .mk .crumbs { background: radial-gradient(circle at 20% 70%, #7b4a2e 0 3%, transparent 3.5%), radial-gradient(circle at 75% 80%, #7b4a2e 0 4%, transparent 4.5%), radial-gradient(circle at 40% 90%, #a0673f 0 2.5%, transparent 3%), radial-gradient(circle at 85% 40%, #a0673f 0 2.5%, transparent 3%), radial-gradient(circle at 12% 30%, #7b4a2e 0 2%, transparent 2.5%); }
  .mk .props { background: radial-gradient(circle at 8% 20%, #f4c37a 0 9%, transparent 9.5%), radial-gradient(circle at 92% 30%, #e86a6a 0 8%, transparent 8.5%), radial-gradient(circle at 10% 88%, #9ccf7a 0 10%, transparent 10.5%), radial-gradient(circle at 90% 90%, #f0a5c4 0 9%, transparent 9.5%); filter: blur(0.4cqw); }
  .mk .callout { background: #fff; border-radius: 2.4cqw; padding: 1.8cqw 2.2cqw; font-size: 3.6cqw; line-height: 1.25; box-shadow: 0 1cqw 3cqw rgba(0,0,0,0.12); }
  .mk .callout b { color: var(--a); font-size: 4cqw; }
  .mk .line-c { border-top: 0.5cqw dashed var(--a); }
  .mk .col-them { background: #ececec; padding-top: 4cqw; }
  .mk .col-them.cream { background: #f6efe4; }
  .mk .col-us { background: var(--a); padding-top: 4cqw; }
  .mk .col-us.vivid { background: linear-gradient(160deg, #ff7a59, #ff3d8b); }
  .mk .splash { background: radial-gradient(ellipse, rgba(255,255,255,0.7) 0 40%, transparent 70%); }
  .mk .grid2 { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 2fr 1fr 1fr 1fr; gap: 0; border: 0.6cqw solid #111; }
  .mk .grid2 .cell { position: relative; border: 0.4cqw solid #111; display: flex; align-items: center; justify-content: center; font-size: 5cqw; font-weight: 800; text-align: center; }
  .mk .grid2 .cell.head { background: #fafafa; }
  .mk .divider { background: #fff; }
  .mk .handwrite { font-family: 'Marker Felt', 'Bradley Hand', 'Comic Sans MS', cursive; color: #fff; font-size: 6cqw; text-shadow: 0 0.4cqw 1cqw rgba(0,0,0,0.4); }
  .mk .handwrite.dark { color: #1f3a8a; text-shadow: none; position: static; text-align: center; font-size: 5.4cqw; }
  .mk .whiteboard { background: #fbfbf8; border: 1.2cqw solid #b9b2a6; border-radius: 1.5cqw; padding: 2cqw; }
  .mk .wb { display: flex; justify-content: space-around; align-items: center; font-size: 10cqw; color: #1f3a8a; }
  .mk .wb .arr { font-size: 7cqw; }
  .mk .accent-panel { background: var(--a); }
  .mk .studio { background: linear-gradient(180deg, #f7f7f9, #e7e7ee); }
  .mk mark { background: #d4ff3a; padding: 0 0.6cqw; }
  .mk .fan > div { position: absolute; }
  .mk .overhead { background: #efe7da; }
  .mk .bowl { border-radius: 50%; background: #fff; display: grid; grid-template-columns: 1fr 1fr; overflow: hidden; box-shadow: 0 2cqw 5cqw rgba(0,0,0,0.15); }
  .mk .bowl span { display: flex; align-items: center; justify-content: center; font-size: 5cqw; font-weight: 800; color: #fff; }
  .mk .bowl span:nth-child(1) { background: #f4a259; } .mk .bowl span:nth-child(2) { background: #8cb369; } .mk .bowl span:nth-child(3) { background: #bc4b51; } .mk .bowl span:nth-child(4) { background: #5b8e7d; }
  .mk .info .cta { padding: 2cqw 0; font-size: 4.4cqw; }
  .mk .divider-logo { text-align: center; font-size: 3.6cqw; font-weight: 800; letter-spacing: 0.2em; color: #fff; border-top: 0.3cqw solid rgba(255,255,255,0.4); padding-top: 1cqw; }
  .mk .masthead { background: #fff; border-bottom: 0.4cqw solid #ccc; font-family: Georgia, serif; font-weight: 900; font-size: 8cqw; display: flex; align-items: center; justify-content: center; letter-spacing: 0.02em; }
  .mk .ios { display: flex; justify-content: space-between; align-items: center; padding: 0 4cqw; font-size: 3.6cqw; font-weight: 700; }
  .mk .notesbar { display: flex; justify-content: space-between; align-items: center; padding: 0 4cqw; font-size: 4.2cqw; color: #E5A100; font-weight: 600; }
  .mk .bubble { display: inline-block; width: auto !important; padding: 1.6cqw 3cqw; border-radius: 2cqw; font-size: 4.4cqw; font-weight: 700; }
  .mk .bubble.c1 { background: #fff; } .mk .bubble.c2 { background: #FFD60A; } .mk .bubble.c3 { background: #FF375F; color: #fff; }
  .mk .bubble.c4 { background: #111; color: #fff; } .mk .bubble.c5 { background: #64D2FF; }
  .mk .postit { background: #ffe974; padding: 3cqw; font-family: 'Marker Felt', 'Bradley Hand', cursive; font-size: 5.2cqw; line-height: 1.3; color: #222; box-shadow: 0 1.5cqw 3cqw rgba(0,0,0,0.25); }
  .mk .postit::before { content: ''; position: absolute; top: -2cqw; left: 35%; width: 30%; height: 4cqw; background: rgba(255,255,255,0.6); }
"""


def generic_sketch(ratio: str = "4:5") -> str:
    """Náčrt pre nový template, ktorý ešte nemá vlastný — všeobecná kompozícia + štítok „nový"."""
    w, h = (int(x) for x in ratio.split(":")) if ":" in ratio else (4, 5)
    inner = (b("t lg", 8, 8, 84, 0, "Nový template") + b("t xs muted", 8, 24, 84, 0, "náčrt sa doplní")
             + b(PROD, 36, 36, 28, 40) + b("cta", 22, 84, 56, 0, "CTA"))
    return f'<div class="mk bg-cream" style="aspect-ratio:{w}/{h}">{inner}</div>'


def sketch_html(num: int, ratio_hint: str = "4:5") -> str:
    entry = SKETCHES.get(num)
    if not entry:
        return generic_sketch(ratio_hint)
    ratio, bg, inner = entry
    w, h = (int(x) for x in ratio.split(":"))
    return f'<div class="mk {bg}" style="aspect-ratio:{w}/{h}">{inner}</div>'


def sketch_ratio(num: int, ratio_hint: str = "") -> str:
    entry = SKETCHES.get(num)
    return entry[0] if entry else (ratio_hint or "4:5")
