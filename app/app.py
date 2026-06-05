"""
app.py — Usporedba cijena Spar vs Kaufland
Pokretanje: streamlit run app/app.py
"""

import os
import pandas as pd
import streamlit as st
from rapidfuzz import process, fuzz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data/processed/usporedba.csv")

DISPLAY_COLS = [
    "naziv_spar", "naziv_kaufland",
    "cijena_spar", "cijena_kaufland",
    "razlika_eur", "razlika_posto", "jeftiniji",
]

COL_LABELS = {
    "naziv_spar": "Naziv (Spar)",
    "naziv_kaufland": "Naziv (Kaufland)",
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
    names = result["naziv_spar"].fillna("") + " " + result["naziv_kaufland"].fillna("")
    hits = process.extract(q, names, scorer=fuzz.WRatio, limit=100)
    idx = [i for _, score, i in hits if score > 50]
    result = result.loc[idx]

if filter_store != "Svi":
    result = result[result["jeftiniji"].str.lower() == filter_store.lower()]

sort_col, asc = SORT_MAP[sort_by]
result = result.sort_values(sort_col, ascending=asc, na_position="last")

# ── metrike ────────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
spar_cheaper = (result["jeftiniji"] == "spar").sum()
kauf_cheaper = (result["jeftiniji"] == "kaufland").sum()
avg_diff = result["razlika_posto"].mean()

m1.metric("Prikazano", f"{len(result)}")
m2.metric("Jeftiniji Spar", f"{spar_cheaper}")
m3.metric("Jeftiniji Kaufland", f"{kauf_cheaper}")
m4.metric("Prosj. razlika", f"{avg_diff:.1f}%" if pd.notna(avg_diff) else "—")

# ── tablica ────────────────────────────────────────────────────────────────────
show = [c for c in DISPLAY_COLS if c in result.columns]
display = result[show].rename(columns=COL_LABELS).reset_index(drop=True)

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

st.dataframe(display, use_container_width=True, height=520)
st.caption(f"Izvor: dnevni cjenici Spar i Kaufland · {len(df):,} spojenih proizvoda ukupno")
