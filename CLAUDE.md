# Završni projekt — Usporedba cijena (Spar vs Kaufland)

> Ovaj fajl je kontekst za Claude Code. Pročitaj ga prije rada da nastaviš
> točno gdje smo stali u prethodnom razgovoru.

## Cilj projekta
Web aplikacija koja uspoređuje cijene istih proizvoda između dva lanca
(Spar i Kaufland). Korisnik traži proizvod, app pokaže razliku u cijeni.
Podaci dolaze iz dnevnih CSV cjenika koje lanci objavljuju online.

## Ključne odluke (dogovoreno)
- **Jezik/stack:** Python + Pandas, web sloj Streamlit (alternativa Flask).
- **Opseg podataka:** "samo najnovije" (danas vs danas) — BEZ povijesti/snapshota.
  Ako kasnije zatreba povijest, dodaje se zaseban sloj; trenutno se NE radi.
- **Hosting:** odluka odgođena; dizajn je "local-first" pa se lako deploya kasnije
  (logika odvojena od web sloja).
- **Spajanje proizvoda:** preko **barkoda** (egzaktan ključ, pouzdano).
  Fuzzy po nazivu se NE koristi za spajanje lanaca — samo za korisničku tražilicu.

## Nalazi iz podataka (provjereno na stvarnim fajlovima)
- Kaufland CSV: UTF-8, separator TAB, 15 stupaca, cijene imaju vodeće razmake.
- Spar CSV: Windows-1250 (hrv. dijakritika!), separator `;`, 12 stupaca,
  neke cijene prazne.
- Oba: decimalni zarez (8,55), oba imaju stupac `barkod`.
- Od ~14.774 Kaufland i ~17.689 Spar proizvoda: **6.880 dijeli isti barkod.**
- Nazivi se jako razlikuju ("Dobre Pahuljice zobene" vs "DOBRE ZOBENE PAHULJ.")
  → zato barkod, ne naziv, za spajanje.
- U podacima ima outliera (npr. cijena 0,39 € za čokoladu) → treba sanity-filter.

## Struktura
```
cjenik-usporedba/
├── data/raw/          # dnevni CSV-ovi (sad: 2 uzorka)
├── data/processed/    # usporedba.csv (rezultat)
├── src/
│   ├── sources.py     # config po lancu (encoding/sep/mapiranje stupaca)
│   ├── normalize.py   # raw CSV -> zajednička shema + čišćenje cijena
│   ├── match.py       # spajanje po barkodu + razlika u cijeni
│   ├── pipeline.py    # normalize -> match -> spremi  ✅ RADI
│   └── fetch.py       # skidanje DANAŠNJIH fajlova   ⬅ STUB, treba dovršiti
└── app/app.py         # Streamlit tražilica (fuzzy)  ⬅ početna verzija
```

## Status
- [x] normalize.py — radi na oba lanca
- [x] match.py — spaja po barkodu, računa razlika_eur / razlika_posto / jeftiniji
- [x] pipeline.py — end-to-end, ispisuje top razlike, sprema usporedba.csv
- [x] app/app.py — Streamlit tražilica s filterima, sortiranjem, metrikama
- [x] fetch.py — dnevni download po URL obrascu s datumom (Kaufland + Spar)
- [x] sanity-filtri za outliere u cijenama (cijena ≤ 0.05 € i omjer > 10× filtrirani)
- [x] poliranje weba (filteri po jeftinijem lancu, sortiranje, metrike na vrhu)

## Pokretanje
```bash
pip install -r requirements.txt
python src/pipeline.py        # generira data/processed/usporedba.csv
streamlit run app/app.py      # pokrene web tražilicu
```

## Sljedeći korak (predloženo)
- Automatsko pokretanje pipeline.py jednom dnevno (Task Scheduler / cron)
- Deployment (Streamlit Community Cloud ili Heroku)
- Dodati kategorijski pregled (top razlike po kategoriji)
