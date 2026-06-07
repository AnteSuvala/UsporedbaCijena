import pandas as pd


def match_by_barcode(df_a: pd.DataFrame, df_b: pd.DataFrame) -> pd.DataFrame:
    # spajam dva lanca po barkodu i racunam razliku u cijeni
    lanac_a = df_a["lanac"].iloc[0].lower()
    lanac_b = df_b["lanac"].iloc[0].lower()

    keep = ["barkod", "naziv", "marka", "cijena", "akcijska_cijena", "kategorija"]
    a = df_a[keep].add_suffix(f"_{lanac_a}").rename(columns={f"barkod_{lanac_a}": "barkod"})
    b = df_b[keep].add_suffix(f"_{lanac_b}").rename(columns={f"barkod_{lanac_b}": "barkod"})

    # ako se isti barkod ponovi, uzimam najnizu cijenu
    a = a.sort_values(f"cijena_{lanac_a}").drop_duplicates("barkod", keep="first")
    b = b.sort_values(f"cijena_{lanac_b}").drop_duplicates("barkod", keep="first")

    m = a.merge(b, on="barkod", how="inner")

    ca, cb = f"cijena_{lanac_a}", f"cijena_{lanac_b}"

    # izbacujem ocite greske u podacima (premale cijene i nerealan omjer)
    valid = (m[ca] > 0.05) & (m[cb] > 0.05)
    m = m[valid].copy()
    ratio = m[[ca, cb]].max(axis=1) / m[[ca, cb]].min(axis=1)
    m = m[ratio <= 10].copy()

    m["razlika_eur"] = (m[ca] - m[cb]).round(2)
    m["jeftiniji"] = m.apply(
        lambda r: lanac_a if r[ca] < r[cb]
        else (lanac_b if r[cb] < r[ca] else "isto"),
        axis=1,
    )
    m["razlika_posto"] = (
        (m[[ca, cb]].max(axis=1) - m[[ca, cb]].min(axis=1))
        / m[[ca, cb]].min(axis=1) * 100
    ).round(1)

    return m.sort_values("razlika_posto", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    from normalize import normalize
    spar = normalize("data/raw/spar_zadar_20260605.csv", "spar")
    kauf = normalize("data/raw/kaufland_osijek_20260310.csv", "kaufland")
    print(match_by_barcode(spar, kauf).head())
