# Vzor klienta

Skopíruj tento priečinok ako `staticky/brands/<klient>/` (názov bez diakritiky a medzier, napr. `moja-znacka`).

```
<klient>/
├── .env                          voliteľné — vlastný GEMINI_API_KEY klienta (oddelené účtovanie)
├── brand-dna/
│   ├── brand-spec-card.png       fonty, farby, logo, tón — posiela sa ako referencia pri KAŽDOM generovaní
│   ├── visual-style-card.png     vizuálny štýl fotiek a kompozície
│   ├── brand-research-brief.json voliteľné — výstup brand researchu (primary_color_hex sa použije v dashboarde)
│   └── logos/                    oficiálne logá (PNG s priehľadnosťou) na dodatočné prilepenie
└── products/<produkt>/
    ├── source-product-images/    čisté fotky produktu (packshot bez ľudí funguje najlepšie)
    └── product-image-ads/<YYYY-MM-DD-nazov>/
        ├── prompts-sk.json       zadanie bannerov (vzor vedľa)
        └── outputs/              sem generátor uloží bannery + manifest.json
```

Brand karty vytvoríš podľa `staticky/01-brand-research-prompt/` a `staticky/02-brand-cards/`.
