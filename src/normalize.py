"""
normalize.py
-------------
Pretvara jedan "messy" CSV (kako ga lanac objavi) u nasu zajednicku shemu.

Rjesava:
  - razliciti encoding (utf-8 vs windows-1250)
  - razliciti separator (tab vs ;)
  - cijene s razmacima ("   8,55") i decimalnim zarezom -> float 8.55
  - prazne cijene -> NaN
  - barkod kao cisti string (bez .0, bez razmaka)
"""

import pandas as pd
from sources import SOURCES, COMMON_COLUMNS


def _clean_price(series: pd.Series) -> pd.Series:
    """'   8,55' -> 8.55 ; '' -> NaN. Decimalni zarez -> tocka."""
    s = (
        series.astype(str)
        .str.strip()
        .str.replace("\xa0", "", regex=False)   # non-breaking space
        .str.replace(".", "", regex=False)       # tisucice (ako ih ima)
        .str.replace(",", ".", regex=False)       # decimalni zarez -> tocka
    )
    return pd.to_numeric(s, errors="coerce")


def _clean_barcode(series: pd.Series) -> pd.Series:
    """Barkod kao cisti string znamenki; nevaljano -> prazno."""
    s = series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    s = s.where(s.str.fullmatch(r"\d+"), "")
    return s


def normalize(path: str, source_key: str) -> pd.DataFrame:
    """
    path        : putanja do raw CSV-a
    source_key  : "kaufland" ili "spar" (kljuc iz sources.SOURCES)
    -> DataFrame u zajednickoj shemi COMMON_COLUMNS
    """
    cfg = SOURCES[source_key]
    raw = pd.read_csv(path, sep=cfg["sep"], encoding=cfg["encoding"], dtype=str)
    raw.columns = [c.strip() for c in raw.columns]

    out = pd.DataFrame()
    price_cols = {"cijena", "cijena_po_jm", "akcijska_cijena", "najniza_30d"}

    for target, source_col in cfg["columns"].items():
        if source_col not in raw.columns:
            out[target] = pd.NA          # lanac nema taj stupac -> prazno
            continue
        col = raw[source_col]
        if target == "barkod":
            out[target] = _clean_barcode(col)
        elif target in price_cols:
            out[target] = _clean_price(col)
        else:
            out[target] = col.astype(str).str.strip()

    out["lanac"] = cfg["lanac"]
    out = out.reindex(columns=COMMON_COLUMNS)   # garantira isti redoslijed/stupce

    # zadrzi samo retke s valjanim barkodom (kljuc za spajanje)
    out = out[out["barkod"].astype(str).str.len() > 0].reset_index(drop=True)
    return out


if __name__ == "__main__":
    # brzi test
    df = normalize("data/raw/spar_zadar_20260605.csv", "spar")
    print(df.head())
    print("redaka:", len(df))
