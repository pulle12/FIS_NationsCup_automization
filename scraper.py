from playwright.sync_api import sync_playwright

print('Erster Webscraper')

baseURL = "https://www.fis-ski.com"
URL = baseURL + "/DB/alpine-skiing/calendar-results.html?eventselection=&place=&sectorcode=AL&seasoncode=2026&categorycode=WC&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-2026&saveselection=-1&seasonselection="

print('Scrapen von: ' + URL)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    
    html = page.content()
    print(html)

    browser.close()