"""
fetch.py
--------
Skida DANASNJE CSV-ove za Spar i Kaufland direktno po URL-u.
Datum je ugraden u URL; samo zamijenimo danasnji datum.

Kaufland URL obrazac (datum u dva mjesta):
  - putanja:    /mpc_15_5/{m}_{Y}/{d}_{m}/        (bez vodecih nula)
  - ime fajla:  ..._%20{DDMMYYYY}%20_7-30.csv     (s vodecim nulama)

Spar URL obrazac:
  - .../{fiksni_prefiks}_{YYYYMMDD}_0330.csv
"""

import os
import datetime as dt

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")

TIMEOUT = 30

HEADERS = {"User-Agent": "Mozilla/5.0 (CjenikiBot/1.0)"}

# ── Kaufland ──────────────────────────────────────────────────────────────────
KAUFLAND_TMPL = (
    "https://www.kaufland.hr/content/dam/kaufland/global/article/hr_HR"
    "/download/document/mpc_15_5/{m}mj/{d}"
    "/Hipermarket_Svilajska_ulica_37_Osijek_6430_{DD}{MM}{Y}_7-30.csv"
)

# ── Spar ──────────────────────────────────────────────────────────────────────
SPAR_TMPL = (
    "https://www.spar.hr/datoteke_cjenici"
    "/hipermarket_osijek_svilajska_31a_8725_interspar_8725_os_porta._0400_{YYYYMMDD}_0330.csv"
)


def _kaufland_url(today: dt.date) -> str:
    return KAUFLAND_TMPL.format(
        m=today.month,            # bez vodece nule  (6)
        d=today.day,              # bez vodece nule  (5)
        Y=today.year,             # puna godina      (2026)
        DD=f"{today.day:02d}",    # s vodecim nulom (05)
        MM=f"{today.month:02d}",  # s vodecim nulom (06)
    )


def _spar_url(today: dt.date) -> str:
    return SPAR_TMPL.format(YYYYMMDD=today.strftime("%Y%m%d"))


def _download(url: str, dest: str) -> None:
    r = requests.get(url, timeout=TIMEOUT, headers=HEADERS, stream=True)
    r.raise_for_status()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=65_536):
            f.write(chunk)


def fetch_today() -> list[tuple[str, str]]:
    """
    Preuzima danasnje CSV-ove i vraca [(putanja, kljuc_lanca), ...].
    Preskace fajl ako vec postoji u data/raw/.
    """
    today = dt.date.today()
    date_str = today.strftime("%Y%m%d")
    os.makedirs(RAW_DIR, exist_ok=True)

    configs = [
        ("kaufland", _kaufland_url(today)),
        ("spar",     _spar_url(today)),
    ]

    results = []
    for key, url in configs:
        dest = os.path.join(RAW_DIR, f"{key}_{date_str}.csv")
        if os.path.exists(dest):
            print(f"{key}: vec postoji -> {dest}")
            results.append((dest, key))
            continue

        print(f"{key}: preuzimam ...")
        print(f"  URL: {url}")
        try:
            _download(url, dest)
            print(f"  OK  -> {dest}")
            results.append((dest, key))
        except requests.HTTPError as exc:
            print(f"  [GRESKA] HTTP {exc.response.status_code}: {url}")
        except Exception as exc:
            print(f"  [GRESKA] {exc}")

    if not results:
        raise RuntimeError("Preuzimanje nije uspjelo ni za jedan lanac.")
    return results


if __name__ == "__main__":
    pairs = fetch_today()
    print("\nPreuzeti fajlovi:")
    for path, key in pairs:
        print(f"  {key:10s} -> {path}")
