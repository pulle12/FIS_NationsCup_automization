# ⛷️ Ski Alpin Nationencup 25/26

Dieses Projekt sammelt Weltcup-Ergebnisse von der FIS-Seite, aggregiert Nationenpunkte und bietet eine kleine GUI zum Filtern (Disziplin/Geschlecht) und zum Steuern des Datenlaufs.

## Komponenten

- **`scraper.py`**: Lädt Ergebnisse für bekannte Race-IDs, speichert strukturierte `results.json` mit Metadaten je Rennen.
- **`fetch_race_ids.py`**: Klickt durch die FIS Kalender-Results Seite, öffnet Events und deren Rennen, extrahiert `raceid` aus der Ergebnis-URL und schreibt `race_ids_2026.json`.
- **`gui.py`**: Mini-Oberfläche zum Laden/Filtern von `results.json` sowie Button „IDs neu laden“ (ruft `fetch_race_ids.py`).
- **`automate.bat`**: Startet die GUI; von dort kannst du IDs laden und den Scrape manuell anstoßen.
- **`ski_nationencup_25-26.py`**: Deine Auswertung/Visualisierung basierend auf `results.json`.

## Ergebnisse-Format

`results.json` ist ein Objekt:

```
{
    "season": "2026",
    "category": "WC",
    "generated_at": "YYYY-MM-DDThh:mm:ss",
    "races": [
        {
            "meta": { "season": "2026", "category": "WC", "discipline": "GS", "gender": "M", "date": "dd.mm.yyyy", "location": "Ort", "race_id": 127353 },
            "points": { "AUT": 80, "SUI": 45, ... }
        },
        ...
    ]
}
```

## Installation

```powershell
# venv empfohlen
python -m venv .venv
.venv\Scripts\activate

python -m pip install selenium webdriver-manager pandas matplotlib pillow
```

## Nutzung

- Starte die GUI:
```powershell
.venv\Scripts\python.exe gui.py
```
- IDs neu laden: Button „IDs neu laden“ in der GUI (legt/aktualisiert `race_ids_2026.json`).
- Ergebnisse scrapen: `scraper.py` nutzen; der Scraper lädt die Race-IDs aus `race_ids_2026.json` oder fällt auf eine Fallback-Liste zurück.
- Auswertung: `ski_nationencup_25-26.py` ausführen oder in die GUI integrieren.

## Hinweise

- Die FIS-Seite lädt Inhalte dynamisch. Der ID-Fetch nutzt Klicks, Scrollen und Wartezeiten; falls die Seite blockt, erneut versuchen.
- Trainings können aktuell mitgesammelt werden; Filterung ist möglich, wenn gewünscht.
- `automate.bat` startet die GUI, damit du entscheiden kannst, ob IDs neu geladen werden sollen.

---
Viel Spaß beim Entwickeln und Auswerten!
