import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup

print('Erster Webscraper')

# https://www.fis-ski.com/DB/alpine-skiing/calendar-results.html?eventselection=&place=&sectorcode=AL&seasoncode=2026&categorycode=WC&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-2026&saveselection=-1&seasonselection=

baseURL = "https://www.fis-ski.com"
URL = baseURL + "/DB/alpine-skiing/calendar-results.html?eventselection=&place=&sectorcode=AL&seasoncode=2026&categorycode=WC&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-2026&saveselection=-1&seasonselection="

print('Scrapen von: ' + URL)

session1 = HTMLSession()
page1 = session1.get(URL)
page1.html.render()
print(page1.html.html)