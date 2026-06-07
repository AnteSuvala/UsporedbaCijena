# Usporedba cijena: Spar vs Kaufland

Završni projekt — web aplikacija koja uspoređuje cijene istih proizvoda između
dva trgovačka lanca (Spar i Kaufland). Podaci dolaze iz dnevnih CSV cjenika koje
lanci objavljuju online. Korisnik traži proizvod, a aplikacija pokaže razliku u
cijeni između lanaca.

Proizvodi se povezuju **preko barkoda** (isti EAN u obje trgovine), a korisnik
ih pretražuje po nazivu.

## Brzi start
```bash
pip install -r requirements.txt
python src/pipeline.py              # normalizira oba CSV-a i spaja po barkodu
python -m streamlit run app/app.py  # web tražilica
```

Rezultat spajanja je `data/processed/usporedba.csv` (jedan redak po proizvodu
koji postoji u oba lanca, s razlikom u cijeni).

## Tehnologije
- Python + Pandas za obradu podataka
- Streamlit za web sloj (logika je odvojena od web sloja pa se lako deploya)
- Opseg podataka: samo najnoviji cjenik (danas vs danas), bez povijesti

## Struktura
```
├── data/raw/          # dnevni CSV-ovi
├── data/processed/    # usporedba.csv (rezultat)
├── src/
│   ├── sources.py     # postavke po lancu (encoding/separator/stupci)
│   ├── normalize.py   # raw CSV -> zajednička shema + čišćenje cijena
│   ├── match.py       # spajanje po barkodu + razlika u cijeni
│   ├── pipeline.py    # normalize -> match -> spremi
│   └── fetch.py       # skidanje današnjih cjenika
└── app/app.py         # Streamlit tražilica
```

## Kako radi
1. `src/sources.py` — opis svakog lanca (encoding, separator, mapiranje stupaca).
2. `src/normalize.py` — svaki CSV pretvara u zajedničku shemu i čisti cijene.
3. `src/match.py` — spaja lance po barkodu i računa razliku.
4. `src/pipeline.py` — sve zajedno → `usporedba.csv`.
5. `app/app.py` — Streamlit tražilica s filterima i sortiranjem.

## Napomene o podacima
Formati cjenika se dosta razlikuju, pa je dobar dio posla bio u čišćenju:
- Kaufland CSV: UTF-8, separator TAB, cijene imaju vodeće razmake.
- Spar CSV: Windows-1250 (zbog hrvatske dijakritike), separator `;`, neke cijene prazne.
- Oba koriste decimalni zarez (8,55) i imaju stupac `barkod`.
- Od ~14.774 Kaufland i ~17.689 Spar proizvoda, ~6.880 dijeli isti barkod.
- Nazivi se jako razlikuju ("Dobre Pahuljice zobene" vs "DOBRE ZOBENE PAHULJ."),
  zato spajanje ide po barkodu, a ne po nazivu.
- U podacima ima i očitih grešaka (npr. cijena 0,39 € za čokoladu), pa
  `match.py` izbacuje cijene ispod 0.05 € i parove s omjerom većim od 10×.

## Automatsko osvježavanje
`.github/workflows/daily.yml` jednom dnevno pokreće pipeline i commita novi
`usporedba.csv` natrag u repo, pa se Streamlit Cloud sam redeploya.
