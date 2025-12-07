from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

print('Erster Webscraper')

baseURL = "https://www.fis-ski.com"
URL = baseURL + "/DB/alpine-skiing/calendar-results.html?eventselection=&place=&sectorcode=AL&seasoncode=2026&categorycode=WC&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-2026&saveselection=-1&seasonselection="

print('Scrapen von: ' + URL)

nation_points = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    
    html1 = page.content()
    soup1 = BeautifulSoup(html1, 'html.parser')
    results = soup1.find_all(id='57999')

    element1 = page.query_selector("div.g-row a")
    href = element1.get_attribute("href")
    print('Scrapen von: ' + href)
    page.goto(href, wait_until="domcontentloaded")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)
    html2 = page.content()
    rows = page.query_selector_all("a.table-row")
    print("Gefundene rows:", len(rows))
    for row in rows:
        nation_el = row.query_selector("span.country__name-short")

        points_el = row.query_selector("div.justify-right.hidden-xs.g-lg-2.g-md-2.g-sm-2")

        if not nation_el or not points_el:
            continue

        nation = nation_el.inner_text().strip()
        points_text = points_el.inner_text().strip()

        try:
            points = int(points_text)
        except:
            continue

        # Map befüllen
        if nation in nation_points:
            nation_points[nation] += points
        else:
            nation_points[nation] = points
    
    print(nation_points)
    browser.close()
