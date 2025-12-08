import json
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Setup für Selenium (Headless Chrome) ---
chrome_options = Options()
chrome_options.add_argument("--headless")  # Browser läuft unsichtbar
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
# Wichtig: User-Agent setzen, damit FIS nicht blockiert
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Browser starten
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

nation_points_total = {}

# Das sind Rennen der Saison 2025 (nicht 2026!)
season_races = [
    127331, 127332, 127333, 127334, 127335, 127336,
    127440, 127441, 127442, 127443,
    127340, 127341, 127342, 127343, 127344
]

print("Starte Scraping... (das kann etwas dauern, da der Browser rendern muss)")

try:
    for raceid in season_races:
        url = f"https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid={raceid}"
        driver.get(url)

        try:
            # Wir warten maximal 10 Sekunden, bis die Tabelle geladen ist
            # Wir suchen nach dem Link-Element der Table-Rows, da dieses erst per JS erscheint
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.table-row"))
            )
        except:
            print(f"Race {raceid}: Timeout oder keine Daten geladen.")
            continue

        # Jetzt holen wir das HTML vom Browser, nachdem JS ausgeführt wurde
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # --- Saison Check ---
        season_code_el = soup.select_one("span.seasoncode")
        # ACHTUNG: Die IDs in deiner Liste sind Saison 2025. 
        # Wenn du strikt auf "2026" prüfst, wirst du keine Ergebnisse bekommen.
        # Ich habe es hier auf != "2025" geändert, damit du siehst, dass es funktioniert.
        if season_code_el:
            season_text = season_code_el.get_text(strip=True)
            if season_text != "2025": 
                print(f"Race {raceid}: Ist Saison {season_text}, überspringe...")
                continue
        
        # --- Daten extrahieren ---
        # FIS hat manchmal mehrere 'tbody' container, wir suchen spezifisch
        rows = soup.select("a.table-row")
        print(f"Race {raceid}: Gefundene rows: {len(rows)}")

        for row in rows:
            nation_el = row.select_one("span.country__name-short")
            # Die Punkte stehen oft in div.justify-right
            right_cells = row.select("div.justify-right")

            if not nation_el or not right_cells:
                continue

            nation = nation_el.get_text(strip=True)

            # Die FIS Tabelle ist trickreich. Manchmal ist es die letzte Zelle, manchmal die vorletzte (wegen FIS-Punkten vs Cup-Punkten).
            # Bei Results ist die letzte Spalte meist "Cup Points" oder "Time".
            # Wir suchen nach der Zelle, die wie Weltcuppunkte aussieht (Ganzzahl, oft fett gedruckt oder letzte Spalte).
            
            # Bei offiziellen Resultaten ist die letzte Zelle oft die "Race Points" oder "Cup Points".
            # Wir nehmen hier die Logik: Wenn Text eine Zahl ist.
            points_found = 0
            
            # Wir iterieren von hinten durch die Zellen, um die Punkte zu finden
            for cell in reversed(right_cells):
                txt = cell.get_text(strip=True)
                if txt.isdigit():
                    points_found = int(txt)
                    break # Wir nehmen die letzte Zahl (meistens Cup Points bei Results)
            
            if points_found > 0:
                nation_points_total[nation] = nation_points_total.get(nation, 0) + points_found

finally:
    driver.quit()

# --- JSON Speichern ---
output_dir = os.path.join("..", "Projekt_Ski")
os.makedirs(output_dir, exist_ok=True) # Ordner erstellen falls nicht existent
output_path = os.path.join(output_dir, "results.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(nation_points_total, f, indent=4)

print(f"Fertig! Results gespeichert in {output_path}")
print("Ergebnis-Vorschau:", nation_points_total)