"""
sources.py
-----------
Konfiguracija po lancu trgovina.

Svaki lanac objavljuje CSV u svom formatu (drugi encoding, separator,
nazivi stupaca). Ovdje na JEDNOM mjestu opisujemo kako svaki izgleda i
kako se njegovi stupci mapiraju u nasu ZAJEDNICKU shemu.

Dodavanje treceg lanca = samo novi unos u SOURCES. Ostatak koda se ne mijenja.
"""

# Zajednicka (ciljana) shema u koju normaliziramo sve lance.
# Redoslijed = redoslijed stupaca u izlaznoj tablici.
COMMON_COLUMNS = [
    "barkod",            # primarni kljuc za spajanje izmedu trgovina
    "naziv",
    "marka",
    "neto_kolicina",
    "jedinica_mjere",
    "cijena",            # redovna MPC u EUR
    "cijena_po_jm",      # cijena po jedinici mjere (EUR)
    "akcijska_cijena",   # ako postoji
    "najniza_30d",       # najniza cijena u 30 dana
    "kategorija",
    "lanac",             # "Spar" / "Kaufland" (dodaje se automatski)
]

SOURCES = {
    "kaufland": {
        "lanac": "Kaufland",
        "encoding": "utf-8",
        "sep": "\t",
        # mapiranje: kljuc = nas zajednicki stupac, vrijednost = naziv u njihovom CSV-u
        "columns": {
            "barkod": "barkod",
            "naziv": "naziv proizvoda",
            "marka": "marka proizvoda",
            "neto_kolicina": "neto količina(KG)",
            "jedinica_mjere": "jedinica mjere",
            "cijena": "maloprod.cijena(EUR)",
            "cijena_po_jm": "cijena jed.mj.(EUR)",
            "akcijska_cijena": "akc.cijena, A=akcija",
            "najniza_30d": "Najniža MPC u 30dana",
            "kategorija": "kategorija proizvoda",
        },
    },
    "spar": {
        "lanac": "Spar",
        "encoding": "windows-1250",
        "sep": ";",
        "columns": {
            "barkod": "barkod",
            "naziv": "naziv",
            "marka": "marka",
            "neto_kolicina": "neto količina",
            "jedinica_mjere": "jedinica mjere",
            "cijena": "MPC (EUR)",
            "cijena_po_jm": "cijena za jedinicu mjere (EUR)",
            "akcijska_cijena": "MPC za vrijeme posebnog oblika prodaje (EUR)",
            "najniza_30d": "Najniža cijena u posljednjih 30 dana (EUR)",
            "kategorija": "kategorija proizvoda",
        },
    },
}
