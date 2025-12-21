import json
import os
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Setup ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

season_results_list = []

SEASON_CODE = "2026"
CATEGORY_CODE = "WC"
RACE_ID_FILE = "race_ids_2026.json"

# Fallback-Liste falls keine IDs-Datei vorhanden ist
FALLBACK_RACE_IDS = [
    127331, 127332, 127333, 127334, 127335, 127336,
    127440, 127441, 127442, 127443,
    127340, 127341, 127342, 127343, 127344, 127347, 127348, 127350, 127349, 127351, 127352, 127339, 127357, 127360, 127356, 127361, 127362, 127363
]


def load_race_ids() -> list[int]:
    path = os.path.join(os.path.dirname(__file__), RACE_ID_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            try:
                data = json.load(fh)
                # akzeptiere {"race_ids": [...]} oder direkt [...]
                if isinstance(data, dict) and "race_ids" in data:
                    return list(map(int, data["race_ids"]))
                if isinstance(data, list):
                    return list(map(int, data))
            except Exception:
                pass
    return FALLBACK_RACE_IDS


def extract_meta(soup: BeautifulSoup) -> dict:
    text_blob = " ".join(el.get_text(" ", strip=True) for el in soup.select("div.event-header, div.event-header__name, div.event-header__subtitle"))
    discipline = None
    gender = None
    date = None
    location = None

    # Disziplin per Stichwort
    for key in ["Downhill", "Super-G", "Super G", "Giant Slalom", "Slalom", "Parallel", "Alpine Combined", "Combined", "GS", "SL", "DH", "SG", "PGS", "AC"]:
        if key.lower() in text_blob.lower():
            discipline = key
            break

    # Gender-Heuristik
    low = text_blob.lower()
    if "men" in low or "m." in low:
        gender = "M"
    if "ladies" in low or "women" in low or "w." in low:
        gender = "W"

    # Datum (einfaches Muster)
    m_date = re.search(r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", text_blob)
    if m_date:
        date = m_date.group(1)

    # Location: erster Teil vor Komma falls vorhanden
    if "," in text_blob:
        location = text_blob.split(",", 1)[0].strip()

    return {
        "season": SEASON_CODE,
        "category": CATEGORY_CODE,
        "discipline": discipline or "unknown",
        "gender": gender or "unknown",
        "date": date,
        "location": location,
    }


season_races = load_race_ids()
print(f"Gefundene Race-IDs (Datei/Fallback): {len(season_races)} -> {season_races}")

print("Starte Scraping pro Rennen mit strenger Punkte-Filterung...")

try:
    for raceid in season_races:
        url = f"https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid={raceid}"
        driver.get(url)

        try:
            # Warte auf Tabelle
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.table-row"))
            )
        except:
            print(f"Race {raceid}: Keine Daten/Timeout.")
            season_results_list.append({
                "race_id": raceid,
                "points": {} 
            })
            continue

        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Hol alle Zeilen
        rows = soup.select("a.table-row")
        print(f"Race {raceid}: Analysiere {len(rows)} Athleten...")

        current_race_points = {}

        for row in rows:
            nation_el = row.select_one("span.country__name-short")
            # Wir holen ALLE Spalten, die rechts ausgerichtet sind (Zeit, Diff, Punkte)
            right_cells = row.select("div.justify-right")

            if not nation_el or not right_cells:
                continue

            nation = nation_el.get_text(strip=True)

            # --- LOGIK FIX ---
            # Die Weltcup-Punkte stehen fast immer in der LETZTEN Spalte.
            # Wenn ein Fahrer keine Punkte bekommt (Platz > 30), ist die Spalte oft leer oder enthält "-"
            
            last_cell_text = right_cells[-1].get_text(strip=True)
            
            points = 0
            
            # Prüfen ob Text eine Zahl ist
            if last_cell_text.isdigit():
                val = int(last_cell_text)
                
                # DER WICHTIGSTE CHECK:
                # Weltcuppunkte sind maximal 100 (für Platz 1). 
                # Wenn die Zahl > 100 ist, haben wir versehentlich Zeit, FIS-Code oder Race-Points erwischt.
                if val <= 100:
                    points = val
                else:
                    # Zahl zu groß -> ignorieren (das sind keine WC Punkte)
                    points = 0
            
            # Nur addieren, wenn Punkte > 0
            if points > 0:
                current_race_points[nation] = current_race_points.get(nation, 0) + points

        print(f"Race {raceid}: {len(current_race_points)} Nationen gepunktet.")
        
        season_results_list.append({
            "race_id": raceid,
            "points": current_race_points
        })

finally:
    driver.quit()

output_path = os.path.join("..", "Projekt_Ski", "results.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(season_results_list, f, indent=4)

print(f"Fertig! Results gespeichert in {output_path}")