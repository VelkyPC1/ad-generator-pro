# Video Factory — pravidlá skladania videí

Prečítaj pred každým vytváraním alebo strihom videa. Pravidlá špecifické pre značku (zakázané slová, zábery,
casting, tón) si zapíš do vlastného súboru — napr. `brands/<klient>/brand-dna/chyby-neopakovat.md` alebo do
`copy_playbook` v `config.json`.

## 1. Záber po zábere
- Nikdy dvakrát ten istý záber za sebou.
- Nikdy dva zábery z rovnakej skupiny za sebou (rovnaká predpona názvu, napr. dva `seq_detail-*`).

## 2. Bez loopu a freeze
- Záber sa nesmie loopovať ani zamraziť — keď chýba dĺžka, pridaj ďalší záber.
- Každý klip beží raz, na svoju plnú dĺžku; orezáva sa len úplne posledný.

## 3. Koniec = produkt
- Posledný záber je vždy produktový (`product_*`) a CTA voiceover beží práve počas neho.
- Video nikdy nekončí záberom osoby ani scenérie.

## 4. Hlas vs. titulky
- Voiceover číta celé slová („päť mililitrov", „mojeshop bodka sk"), titulky ukazujú skratky („5 ml", „mojeshop.sk")
  — cez `display_replacements` v scripte.
- Platí pre čísla, jednotky a URL. Ak URL nie je nutné, do voiceoveru ho nedávaj.

## 5. Synchronizácia
- Prvý záber začína presne s titulkami.
- Titulky nikdy neseknú slovo v strede — stopa trvá do konca posledného slova + 0,15 s.

## 6. Explicitný zoznam klipov
- Každý script má `seq_main` (poradie klipov) a `seq_outro` (produktový záver) — presné názvy súborov bez `.mp4`.
- Žiadne automatické zoraďovanie podľa abecedy — každý záber je vedome zvolený.
- Ak validácia sekvencie zlyhá (rovnaký záber za sebou, outro nie je produkt), oprav script a spusti znova.

## 7. Názvy klipov
- `seq_<popis>.mp4` (sekvencie), `product_<popis>.mp4` (záver), `hook_<popis>.mp4` (UGC hook s vlastným zvukom)
  — bez diakritiky a medzier, `(1)` → `-1`.

## 8. Safezone 9:16
- Cena, ponuka, social proof, CTA aj titulky musia byť celé v safezone — platformy (Reels, TikTok, Stories)
  prekrývajú horný a spodný okraj svojím UI.
- Odporúčané: ~14 % zhora a ~20 % zdola voľné; CTA `--cta-bottom 0.22`.

## 9. Potvrdenie
- Pred každým plateným krokom (nový voiceover, AI video klipy) ukáž súhrn a odhad ceny a počkaj na „áno".
