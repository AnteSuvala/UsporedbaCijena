import pandas as pd
from sources import SOURCES, COMMON_COLUMNS


def _clean_price(series: pd.Series) -> pd.Series:
    # '   8,55' -> 8.55, prazno -> NaN
    s = (
        series.astype(str)
        .str.strip()
        .str.replace("\xa0", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(s, errors="coerce")


def _clean_barcode(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    s = s.where(s.str.fullmatch(r"\d+"), "")   # samo znamenke, inace prazno
    return s


def normalize(path: str, source_key: str) -> pd.DataFrame:
    cfg = SOURCES[source_key]
    raw = pd.read_csv(path, sep=cfg["sep"], encoding=cfg["encoding"], dtype=str)
    raw.columns = [c.strip() for c in raw.columns]

    out = pd.DataFrame()
    price_cols = {"cijena", "cijena_po_jm", "akcijska_cijena", "najniza_30d"}

    for target, source_col in cfg["columns"].items():
        if source_col not in raw.columns:
            out[target] = pd.NA
            continue
        col = raw[source_col]
        if target == "barkod":
            out[target] = _clean_barcode(col)
        elif target in price_cols:
            out[target] = _clean_price(col)
        else:
            out[target] = col.astype(str).str.strip()

    out["lanac"] = cfg["lanac"]
    out = out.reindex(columns=COMMON_COLUMNS)

    # bez barkoda nema spajanja, pa takve retke izbacujem
    out = out[out["barkod"].astype(str).str.len() > 0].reset_index(drop=True)
    return out


if __name__ == "__main__":
    df = normalize("data/raw/spar_zadar_20260605.csv", "spar")
    print(df.head())
    print("redaka:", len(df))
