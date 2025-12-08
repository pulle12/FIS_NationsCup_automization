import requests
from bs4 import BeautifulSoup
import json
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.fis-ski.com/",
}

nation_points_total = {}

season_races = [
    127331, 127332, 127333, 127334, 127335, 127336,
    127440, 127441, 127442, 127443,
    127340, 127341, 127342, 127343, 127344
]

for raceid in season_races:
    url = f"https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid={raceid}"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"Race {raceid}: Fehler {r.status_code}")
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    season_code_el = soup.select_one("span.seasoncode")
    if season_code_el and season_code_el.get_text(strip=True) != "2026":
        print(f"Race {raceid}: nicht Saison 2026")
        continue

    results_container = soup.select_one("div.tbody")
    if not results_container:
        print(f"Race {raceid}: Kein tbody-Container gefunden")
        continue

    rows = results_container.select("a.table-row")
    print(f"Race {raceid}: Gefundene rows: {len(rows)}")

    for row in rows:
        nation_el = row.select_one("span.country__name-short")
        right_cells = row.select("div.justify-right.hidden-xs")

        if not nation_el or not right_cells:
            continue

        points_el = right_cells[-1]

        nation = nation_el.get_text(strip=True)

        points_text = "".join(c for c in points_el.get_text(strip=True) if c.isdigit())
        if not points_text:
            continue

        points = int(points_text)

        nation_points_total[nation] = nation_points_total.get(nation, 0) + points

output_path = os.path.join("..", "Projekt_Ski", "results.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(nation_points_total, f, indent=4)

print(f"Results gespeichert in {output_path}")
