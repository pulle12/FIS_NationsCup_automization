from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

print('Erster Webscraper')

baseURL = "https://www.fis-ski.com"
URL = baseURL + "/DB/alpine-skiing/calendar-results.html?eventselection=&place=&sectorcode=AL&seasoncode=2026&categorycode=WC&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-2026&saveselection=-1&seasonselection="

print('Scrapen von: ' + URL)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    
    html1 = page.content()
    soup1 = BeautifulSoup(html1, 'html.parser')
    results = soup1.find_all(id='57999')

    element1 = page.query_selector("div.g-row a")
    href1 = element1.get_attribute("href")
    print('Scrapen von: ' + href1)
    page.goto(href1)
    html2 = page.content()
    element2 = page.query_selector("div.g-row a")
    href2 = element2.get_attribute("href")
    results = map()

    browser.close()

