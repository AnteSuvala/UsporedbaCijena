# Usporedba cijena: Spar vs Kaufland

Završni projekt — web aplikacija koja uspoređuje cijene istih proizvoda između
dva trgovačka lanca, na temelju dnevnih CSV cjenika koje objavljuju online.

Proizvodi se povezuju **preko barkoda** (isti EAN u obje trgovine), a korisnik
ih pretražuje **fuzzy pretragom po nazivu**.

## Brzi start
```bash
pip install -r requirements.txt
python src/pipeline.py        # normalizira oba CSV-a i spaja po barkodu
python -m streamlit run app/app.py    # web tražilica
```

Rezultat spajanja je `data/processed/usporedba.csv` (jedan redak po proizvodu
koji postoji u oba lanca, s razlikom u cijeni).

## Kako radi
1. `src/sources.py` — opis svakog lanca (encoding, separator, mapiranje stupaca).
2. `src/normalize.py` — svaki "messy" CSV → zajednička shema, čišćenje cijena.
3. `src/match.py` — spajanje po barkodu + izračun razlike.
4. `src/pipeline.py` — sve zajedno → `usporedba.csv`.
5. `app/app.py` — Streamlit tražilica.

Vidi `CLAUDE.md` za detaljne odluke i status.
