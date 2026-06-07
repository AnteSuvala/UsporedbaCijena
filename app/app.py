"""
app.py — Usporedba cijena Spar vs Kaufland
Pokretanje: streamlit run app/app.py
"""

import os
import re
import unicodedata

import pandas as pd
import streamlit as st
from rapidfuzz import fuzz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data/processed/usporedba.csv")

# Spar naziv se vise ne prikazuje (Kaufland nazivi izgledaju urednije);
# spajanje i dalje ide po barkodu pa je redak isti proizvod u oba lanca.
DISPLAY_COLS = [
    "naziv_kaufland",
    "cijena_spar", "cijena_kaufland",
    "razlika_eur", "razlika_posto", "jeftiniji",
]

COL_LABELS = {
    "naziv_kaufland": "Naziv",
    "cijena_spar": "Cijena Spar (€)",
    "cijena_kaufland": "Cijena Kaufland (€)",
    "razlika_eur": "Razlika (€)",
    "razlika_posto": "Razlika (%)",
    "jeftiniji": "Jeftiniji",
}

SORT_MAP = {
    "Razlika % ↓": ("razlika_posto", False),
    "Razlika € ↓": ("razlika_eur", False),
    "Cijena Spar ↑": ("cijena_spar", True),
    "Cijena Kaufland ↑": ("cijena_kaufland", True),
}


def _fold(s: str) -> str:
    """Mala/velika slova + makni dijakritiku: 'Čokolada' -> 'cokolada'.
    Tako 'cokolada' nadje 'Čokolada', a 'milka' tocno 'Milka'."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("đ", "d").replace("Đ", "d")
    return s.lower()


@st.cache_data
def load() -> pd.DataFrame:
    return pd.read_csv(DATA, dtype={"barkod": str})


st.set_page_config(page_title="Usporedba cijena", layout="wide")
st.title("Usporedba cijena: Spar vs Kaufland")

if not os.path.exists(DATA):
    st.warning(
        "Podaci još nisu generirani. Pokreni `python src/pipeline.py` lokalno, "
        "ili pričekaj prvo dnevno osvježavanje (GitHub Actions)."
    )
    st.stop()

df = load()

# ── filteri ────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    q = st.text_input("Pretraži proizvod:", placeholder="npr. jogurt, čokolada, kruh...")
with col2:
    filter_store = st.selectbox("Jeftiniji u:", ["Svi", "Spar", "Kaufland", "Isto"])
with col3:
    sort_by = st.selectbox("Sortiraj po:", list(SORT_MAP.keys()))

# ── filtriranje ────────────────────────────────────────────────────────────────
result = df.copy()

if q:
    names = (result["naziv_kaufland"].fillna("") + " " + result["naziv_spar"].fillna("")).map(_fold)
    tokens = [_fold(t) for t in q.split() if t.strip()]

    # 1) Doslovni pogodak: SVE rijeci iz upita moraju se pojaviti u nazivu
    #    (bilo kojim redom). Ovo je ono sto korisnik ocekuje od trazilice.
    mask = pd.Series(True, index=names.index)
    for t in tokens:
        mask &= names.str.contains(re.escape(t), na=False)
    result = result[mask]

    # 2) Ako doslovno nema nista (npr. tipfeler), fuzzy fallback s visokim pragom.
    if result.empty:
        qf = _fold(q)
        scores = names.map(lambda s: fuzz.partial_ratio(qf, s))
        result = df.copy()[scores >= 85]

if filter_store != "Svi":
    result = result[result["jeftiniji"].str.lower() == filter_store.lower()]

sort_col, asc = SORT_MAP[sort_by]
result = result.sort_values(sort_col, ascending=asc, na_position="last")

# ── metrike ────────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
spar_cheaper = (result["jeftiniji"] == "spar").sum()
kauf_cheaper = (result["jeftiniji"] == "kaufland").sum()

# Predznak: razlika_eur = cijena_spar - cijena_kaufland.
#   > 0  -> Spar skuplji  -> Kaufland u prosjeku jeftiniji
#   < 0  -> Kaufland skuplji -> Spar u prosjeku jeftiniji
avg_eur = result["razlika_eur"].mean()

m1.metric("Prikazano", f"{len(result)}")
m2.metric("Jeftiniji Spar", f"{spar_cheaper}")
m3.metric("Jeftiniji Kaufland", f"{kauf_cheaper}")

if pd.isna(avg_eur) or len(result) == 0:
    m4.metric("Prosj. jeftiniji", "—")
elif avg_eur > 0:
    m4.metric("Prosj. jeftiniji", "Kaufland",
              delta=f"{avg_eur:.2f} € / proizvod", delta_color="off")
elif avg_eur < 0:
    m4.metric("Prosj. jeftiniji", "Spar",
              delta=f"{abs(avg_eur):.2f} € / proizvod", delta_color="off")
else:
    m4.metric("Prosj. jeftiniji", "Izjednačeno", delta="0.00 €", delta_color="off")

# ── tablica ────────────────────────────────────────────────────────────────────
# Prikazujemo najvise MAX_REDAKA (vec sortirano) i renderamo kao STATICNU HTML
# tablicu umjesto st.dataframe. st.dataframe ima vlastiti unutarnji scroll/canvas
# koji na nekim mobitelima lose renderira i zna "zaostati" za stranicom; staticna
# tablica prirodno tece sa stranicom, a horizontalni scroll na uskim ekranima
# ostaje unutar samog bloka tablice.
MAX_REDAKA = 300

show = [c for c in DISPLAY_COLS if c in result.columns]
display = result[show].head(MAX_REDAKA).rename(columns=COL_LABELS).reset_index(drop=True)

for col in ["Cijena Spar (€)", "Cijena Kaufland (€)"]:
    if col in display.columns:
        display[col] = display[col].map(lambda x: f"{x:.2f} €" if pd.notna(x) else "")

if "Razlika (€)" in display.columns:
    display["Razlika (€)"] = display["Razlika (€)"].map(
        lambda x: f"{abs(x):.2f} €" if pd.notna(x) else ""
    )

if "Razlika (%)" in display.columns:
    display["Razlika (%)"] = display["Razlika (%)"].map(
        lambda x: f"{x:.1f}%" if pd.notna(x) else ""
    )

if "Jeftiniji" in display.columns:
    display["Jeftiniji"] = display["Jeftiniji"].str.capitalize()

st.markdown(
    """
    <style>
      .cjenik-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
      table.cjenik { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
      table.cjenik th, table.cjenik td {
        padding: 0.45rem 0.7rem;
        border-bottom: 1px solid rgba(128,128,128,0.25);
        white-space: nowrap;
      }
      table.cjenik th { text-align: left; font-weight: 600; }
      /* naziv lijevo, brojcani stupci desno */
      table.cjenik td:not(:first-child), table.cjenik th:not(:first-child) { text-align: right; }
      table.cjenik tr:hover td { background: rgba(128,128,128,0.08); }
    </style>
    """,
    unsafe_allow_html=True,
)

html = display.to_html(index=False, escape=True, border=0, classes="cjenik")
st.markdown(f'<div class="cjenik-wrap">{html}</div>', unsafe_allow_html=True)

prikazano = min(len(result), MAX_REDAKA)
suffix = f" (prikazano prvih {MAX_REDAKA})" if len(result) > MAX_REDAKA else ""
st.caption(
    f"Izvor: dnevni cjenici Spar i Kaufland · {prikazano} rezultata{suffix} · "
    f"{len(df):,} spojenih proizvoda ukupno"
)
