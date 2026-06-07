import os
import sys
import pandas as pd
from normalize import normalize
from match import match_by_barcode
from fetch import fetch_today

# da Windows konzola ne puca na dijakritici
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "data/processed/usporedba.csv")


def _keep_existing(razlog: str) -> None:
    # ako dnevni podaci nisu dobri, ne prepisujem stari rezultat nego ga zadrzim
    print(f"[UPOZORENJE] {razlog}")
    if os.path.exists(OUTPUT):
        print(f"Zadrzavam prethodni rezultat -> {OUTPUT}")
    else:
        print("[NAPOMENA] Nema prethodnog usporedba.csv za zadrzati.")


def run():
    print("=== Preuzimanje cjenika ===")
    try:
        inputs = fetch_today()
    except Exception as exc:
        _keep_existing(f"Preuzimanje nije uspjelo: {exc}")
        return
    by_key = {key: path for path, key in inputs}

    print("\n=== Normalizacija ===")
    dfs = {}
    for key, path in by_key.items():
        try:
            dfs[key] = normalize(path, key)
            print(f"{key:10s}: {len(dfs[key]):>6} proizvoda")
        except Exception as exc:
            print(f"[UPOZORENJE] Normalizacija '{key}' nije uspjela: {exc}")

    if "spar" not in dfs or "kaufland" not in dfs:
        missing = [k for k in ("spar", "kaufland") if k not in dfs]
        _keep_existing(f"Nedostaju podaci za: {missing}")
        return

    spar = dfs["spar"]
    kauf = dfs["kaufland"]

    comp = match_by_barcode(spar, kauf)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    comp.to_csv(OUTPUT, index=False, encoding="utf-8")

    print(f"\nSpojeno po barkodu:    {len(comp):>6} proizvoda")
    print(f"Spremljeno -> {OUTPUT}")
    print("\n=== Top 5 razlika u cijeni ===")
    cols = [c for c in comp.columns if c.startswith(("naziv_", "cijena_"))]
    print(comp[cols + ["razlika_posto", "jeftiniji"]].head().to_string(index=False))


if __name__ == "__main__":
    run()
