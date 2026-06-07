# Postavke za svaki lanac trgovina.
# Svaki lanac ima svoj format CSV-a (encoding, separator, nazivi stupaca),
# pa ovdje opisujem kako se njihovi stupci preslikavaju u nasu zajednicku shemu.

# Stupci koje koristimo nakon normalizacije (i njihov redoslijed).
COMMON_COLUMNS = [
    "barkod",            # kljuc za spajanje dvaju lanaca
    "naziv",
    "marka",
    "neto_kolicina",
    "jedinica_mjere",
    "cijena",
    "cijena_po_jm",
    "akcijska_cijena",
    "najniza_30d",
    "kategorija",
    "lanac",
]

SOURCES = {
    "kaufland": {
        "lanac": "Kaufland",
        "encoding": "utf-8",
        "sep": "\t",
        # kljuc = nas stupac, vrijednost = naziv u njihovom CSV-u
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
