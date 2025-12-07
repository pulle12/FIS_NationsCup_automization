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

nation_points = {}

for row in rows:
    nation_el = row.select_one("span.country__name-short")
    points_el = row.select_one("div.justify-right.hidden-xs")

    if not nation_el or not points_el:
        continue

    nation = nation_el.get_text(strip=True)
    points_text = points_el.get_text(strip=True)

    try:
        points = int(points_text)
    except:
        continue

    nation_points[nation] = nation_points.get(nation, 0) + points

print(nation_points)
