import requests
from bs4 import BeautifulSoup

race_url = "https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid=127331"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.fis-ski.com/",
}

r = requests.get(race_url, headers=headers)
if r.status_code != 200:
    raise Exception(f"Fehler beim Laden der Seite: {r.status_code}")

soup = BeautifulSoup(r.text, "html.parser")

rows = soup.select("a.table-row")
print(f"Gefundene rows: {len(rows)}")

nation_points_total = {}

season_races = [
    127331, 127332, 127333, 127334, 127335, 127336, 127440, 127441, 127442, 127443, 127340, 127341, 127342, 127343, 127344
]

for raceid in season_races:
    race_url = f"https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid={raceid}"
    r = requests.get(race_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    
    rows = soup.select("a.table-row")
    
    for row in rows:
        nation_el = row.select_one("span.country__name-short")
        points_el = row.select_one("div.justify-right.hidden-xs")
        
        if not nation_el or not points_el:
            continue
        
        nation = nation_el.get_text(strip=True)
        points_text = "".join(c for c in points_el.get_text(strip=True) if c.isdigit())
        points = int(points_text)
        
        nation_points_total[nation] = nation_points_total.get(nation, 0) + points

print(nation_points_total)
