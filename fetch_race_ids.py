import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

SEASON_CODE = "2026"
CATEGORY_CODE = "WC"
BASE_CALENDAR_URL = (
    "https://www.fis-ski.com/DB/alpine-skiing/calendar-results.html"
    f"?eventselection=results&place=&sectorcode=AL&seasoncode={SEASON_CODE}&categorycode={CATEGORY_CODE}"
    "&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-2026"
    "&saveselection=-1&seasonselection="
)
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "race_ids_2026.json")

def build_driver(headless: bool = False) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def scroll_to_bottom(driver, steps: int = 10, pause: float = 0.5):
    for _ in range(steps):
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(pause)

def click_load_more(driver) -> bool:
    try:
        candidates = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(., 'LOADMORE', 'loadmore'),'load more') or contains(., 'Mehr') or contains(., 'More')]"
            " | //a[contains(., 'Load more')]"
            " | //button[contains(@class,'load-more')]"
            " | //a[contains(@class,'load-more')]"
        )
        clicked = False
        for el in candidates:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                time.sleep(0.2)
                el.click()
                clicked = True
                time.sleep(1.0)
            except Exception:
                continue
        return clicked
    except Exception:
        return False

def fetch_race_ids() -> list[int]:
    driver = build_driver(headless=False)
    all_ids: set[int] = set()
    try:
        driver.get(BASE_CALENDAR_URL)
        # Cookies akzeptieren
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            ).click()
            time.sleep(0.3)
        except Exception:
            pass

        def collect_current_view_ids() -> set[int]:
            local_ids: set[int] = set()
            # Event-Zeilen suchen
            event_rows = driver.find_elements(
                By.CSS_SELECTOR,
                "div.table-row.reset-padding div.container.pr-xs-0 div.g-row"
            )
            if not event_rows:
                event_rows = driver.find_elements(By.CSS_SELECTOR, "div.table-row.reset-padding div.g-row")

            for row in event_rows:
                # Event öffnen
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                    time.sleep(0.2)
                    row.click()
                except Exception:
                    try:
                        link = row.find_element(By.CSS_SELECTOR, "a")
                        driver.execute_script("arguments[0].click();", link)
                    except Exception:
                        continue

                # Auf Event-Detail warten
                try:
                    WebDriverWait(driver, 8).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.table-row.reset-padding"))
                    )
                except Exception:
                    # zurück zur Kalenderseite
                    driver.back()
                    WebDriverWait(driver, 8).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.table-row.reset-padding"))
                    )
                    continue

                # Renn-Zeilen sammeln
                race_rows = driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.table-row.reset-padding div.container div.g-row.px-sm-1.px-xs-0"
                )
                if not race_rows:
                    race_rows = driver.find_elements(By.CSS_SELECTOR, "div.table-row.reset-padding div.g-row")

                allowed = {
                    "downhill", "dh",
                    "super-g", "super g", "sg",
                    "giant slalom", "gs",
                    "slalom", "sl",
                    "parallel",
                    "alpine combined", "combined", "ac"
                }

                for r in race_rows:
                    try:
                        text_in_row = r.text.lower()
                        if "training" in text_in_row or "official training" in text_in_row:
                            continue
                        # Disziplin-Whitelist (wenn erkennbar)
                        if not any(key in text_in_row for key in allowed):
                            # teils knappe Beschriftung → nicht hart ausschließen
                            pass

                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", r)
                        time.sleep(0.15)
                        links_in_row = r.find_elements(By.CSS_SELECTOR, "a")
                        target_link = None
                        for a in links_in_row:
                            href_candidate = a.get_attribute("href")
                            if not href_candidate:
                                continue
                            if ".pdf" in href_candidate or "/document" in href_candidate:
                                continue
                            if "results.html" in href_candidate:
                                target_link = href_candidate
                                break

                        if target_link:
                            driver.get(target_link)
                            WebDriverWait(driver, 10).until(EC.url_contains("results.html"))
                        else:
                            # kein sichtbarer results-Link → überspringen
                            continue

                        current = driver.current_url
                        if "raceid=" in current:
                            part = current.split("raceid=")[1]
                            digits = "".join(ch for ch in part if ch.isdigit())
                            if digits:
                                local_ids.add(int(digits))

                        # zurück zur Event-Seite
                        driver.back()
                        WebDriverWait(driver, 8).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.table-row.reset-padding"))
                        )
                    except Exception:
                        # Fallback: href direkt parsen
                        try:
                            for a2 in r.find_elements(By.CSS_SELECTOR, "a"):
                                h2 = a2.get_attribute("href")
                                if h2 and "raceid=" in h2:
                                    part = h2.split("raceid=")[1]
                                    digits = "".join(ch for ch in part if ch.isdigit())
                                    if digits:
                                        local_ids.add(int(digits))
                        except Exception:
                            pass

                # zurück zur Kalenderseite
                driver.back()
                WebDriverWait(driver, 8).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.table-row.reset-padding"))
                )

            return local_ids

        # Für beide Gender-Ansichten via UI-Tabs sammeln
        for gender_label in ("Men", "Ladies"):
            try:
                tab = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[contains(., '{gender_label}')]|//button[contains(., '{gender_label}')]"))
                )
                driver.execute_script("arguments[0].click();", tab)
                time.sleep(0.5)
            except Exception:
                # Falls Tab nicht gefunden, weiter mit aktueller Ansicht
                pass

            # Seite maximal füllen
            scroll_to_bottom(driver, steps=10, pause=0.4)
            for _ in range(5):
                if not click_load_more(driver):
                    break
                scroll_to_bottom(driver, steps=5, pause=0.4)

            collected = collect_current_view_ids()
            all_ids.update(collected)

    finally:
        driver.quit()

    return sorted(all_ids)

def main():
    ids = fetch_race_ids()
    payload = {"season": SEASON_CODE, "category": CATEGORY_CODE, "race_ids": ids}
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print(f"Gefundene Race-IDs: {len(ids)} -> gespeichert in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()