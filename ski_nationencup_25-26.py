import pandas as pd
import matplotlib.pyplot as plt
import ctypes
from PIL import Image
import os
import time
import sys
import json

# --- KONFIGURATION ---
# EXCEL_PATH = r'C:\Users\summe\Documents\Office\Excel\ski_alpin_verlaeufe.xlsx'
# SHEET_NAME = '25-26_Py_exp'
BASE_IMAGE_PATH = r'C:\Users\summe\Bilder\Sport\ski\manuel_feller.avif'
OUTPUT_IMAGE_PATH = r'C:\Users\summe\Bilder\Sport\ski\ski_nationencup_25-26.png'
file_path = "./results.json"

# Wo soll das Diagramm auf dem Bild platziert werden? (Pixel Koordinaten)
CHART_POS_X = -150
CHART_POS_Y = 350
CHART_SIZE = (1900, 1300) # Breite, Höhe des Diagramms

# Mapping von FIS-Code zu vollem Namen (für deine "wichtige" Liste)
NATION_MAP = {
    "AUT": "Österreich", "SUI": "Schweiz", "NOR": "Norwegen", 
    "FRA": "Frankreich", "USA": "USA", "GER": "Deutschland", 
    "ITA": "Italien", "SWE": "Schweden", "CRO": "Kroatien",
    "ALB": "Albanien", "CAN": "Kanada", "SLO": "Slowenien"
}

NATION_COLORS = {
    "Österreich": "#ED2939", # Rot
    "Schweiz": "#FF0000",    # Rot (etwas anders) oder Weiß im Darkmode
    "Norwegen": "#00205B",   # Blau
    "Frankreich": "#0055A4", # Blau
    "USA": "#3C3B6E",        # Dunkelblau
    "Deutschland": "#FFCC00",# Gold/Gelb (Schwarz sieht man schlecht)
    "Italien": "#009246",    # Grün
    "Schweden": "#FECC00",   # Gelb
    "Kroatien": "#FF0000",
}

RACE_ID_TO_NAME = {
    "127331": "Sölden-RTL (W)",
    "127332": "Sölden-RTL (M)",
    "127333": "Levi-SL (W)",
    "127334": "Levi-SL (M)",
    "127335": "Gurgl-SL (M)",
    "127336": "Gurgl-SL (W)",
    "127440": "Copper Mountain-SG (M)",
    "127441": "Copper Mountain-RTL (M)",
    "127442": "Copper Mountain-RTL (W)",
    "127443": "Copper Mountain-SL (W)",
    "127340": "Beaver Creek-DH (M)",
    "127341": "Beaver Creek-SG (M)",
    "127342": "Tremblant-RTL1 (W)",
    "127343": "Tremblant-RTL2 (W)",
    "127344": "Beaver Creek-RTL (M)"
    # Falls eine ID fehlt, zeigt der Code automatisch die Nummer an
}

# Liste der Nationen, die beschriftet werden sollen (Namen müssen zum Mapping oben passen)
wichtige = ["Österreich", "Schweiz", "Norwegen", "Frankreich", "USA", "Deutschland", "Italien", "Schweden", "Kroatien"]

def update_wallpaper():
    # print("Lese Excel Daten...", end="")

    # Sicherheits-Check: Existiert die Datei überhaupt?
    if not os.path.exists(file_path):
        print(f"FEHLER: Die Datei wurde unter '{file_path}' nicht gefunden.")
        return
        
    try:
        # 1. Excel laden
        # df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, usecols="A:Z")

        # Erste Spalte = Rennen
        # race_column = df.columns[0]
        # races = df[race_column].astype(str)

        # Alle Nationen (alle anderen Spalten)
        # nations = df.columns[1:]

        # 2. Datei öffnen (Modus 'r' für read)
        with open(file_path, "r", encoding="utf-8") as f:
            # json.load verwandelt den Text aus der Datei zurück in ein Python-Dictionary
            raw_data = json.load(f)

        print("✅ Daten erfolgreich geladen!\n")

        data_for_df = []
        race_labels = []

        for entry in raw_data:
            # entry sieht so aus: {'race_id': 123, 'points': {'AUT': 10...}}
            row = entry['points'].copy() # Startet mit {'AUT': 10...}
            data_for_df.append(row)
            r_id = str(entry['race_id'])
            nice_name = RACE_ID_TO_NAME.get(r_id, r_id) 
            race_labels.append(nice_name)

        df = pd.DataFrame(data_for_df)
        df = df.fillna(0)
        df = df.cumsum()
        
        x_axis = range(len(df))

        last_row = df.iloc[-1]
        sorted_cols = last_row.sort_values(ascending=False).index
        df = df[sorted_cols]
        nations = df.columns.tolist()

        # 2. Plot vorbereiten
        plt.figure(figsize=(16, 9), dpi=120)
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.grid(True, which='major', axis='y', alpha=0.3, linestyle='--')
        plt.grid(False, axis='x')

        # Jede Nation als eigene Linie zeichnen
        for code in nations:
            full_name = NATION_MAP.get(code, code)

            if full_name in wichtige:
                # HIER IST DER FARB-FIX FÜR DIE LINIE:
                col = NATION_COLORS.get(full_name, "black") # Farbe holen
                
                plt.plot(
                    x_axis, 
                    df[code], 
                    linewidth=3, 
                    marker="o", 
                    markersize=6, 
                    alpha=0.9, 
                    label=full_name, 
                    color=col # <--- Hier wird die Linie eingefärbt!
                )
            else:
                # Hintergrundrauschen
                plt.plot(x_axis, df[code], linewidth=1, color="grey", alpha=0.1)

        # Titel
        plt.title("Nationencup Saisonverlauf 2025/26", fontsize=16, fontweight="bold")
        plt.ylabel("Punkte", fontsize=12)
        # Achsen
        plt.xticks(ticks=x_axis, labels=race_labels, rotation=45, fontsize=8, ha='right')
        plt.xlim(left=0, right=len(df) + 2) 

        label_data = []
        for code in nations:
            full_name = NATION_MAP.get(code, code)
            if full_name in wichtige:
                y_pos = df[code].iloc[-1]
                x_pos = len(df) - 1
                col = NATION_COLORS.get(full_name, "black")
                
                label_data.append({
                    "text": f" {full_name} ({int(y_pos)})",
                    "y": y_pos,
                    "x": x_pos,
                    "color": col
                })

        # Sortieren (höchste oben)
        label_data.sort(key=lambda k: k["y"], reverse=True)

        # Kollisions-Logik
        max_val = df.max().max()
        min_dist = max_val * 0.035 # Ca 3.5% Abstand
        
        last_y = float('inf')

        for item in label_data:
            current_y = item["y"]
            
            # Wenn zu nah am Vorgänger, schieb es runter
            if last_y - current_y < min_dist:
                current_y = last_y - min_dist
                item["y"] = current_y
            
            last_y = current_y

            # Text zeichnen
            plt.text(
                item["x"] + 0.2, 
                item["y"], 
                item["text"], 
                fontsize=11, 
                va="center", 
                fontweight="bold",
                color=item["color"] # Text in gleicher Farbe wie Linie
            )
        # Manuelle Randeinstellung statt tight_layout()
        plt.subplots_adjust(bottom=0.20, top=0.90, right=0.85)

        plt.savefig("temp_chart.png", transparent=True)
        plt.close()

        # 3. Wallpaper-Bild einbetten
        print("Bild generieren...", end="")
        if os.path.exists(BASE_IMAGE_PATH):
            base = Image.open(BASE_IMAGE_PATH).convert("RGBA")
            chart = Image.open("temp_chart.png").convert("RGBA")
            
            chart = chart.resize(CHART_SIZE, Image.Resampling.LANCZOS)
            cw, ch = chart.size
            box = (CHART_POS_X, CHART_POS_Y, CHART_POS_X + cw, CHART_POS_Y + ch)
            
            base.paste(chart, box, chart)
            base.save(OUTPUT_IMAGE_PATH, "PNG")
            
            abs_path = os.path.abspath(OUTPUT_IMAGE_PATH)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
            print(" Wallpaper aktualisiert!")
        else:
            print(f"\n[FEHLER] Basis-Bild nicht gefunden unter: {BASE_IMAGE_PATH}")

    except Exception as e:
        print(f"\n[FEHLER] {e}")
        import traceback
        traceback.print_exc() # Hilft beim Debuggen


if __name__ == "__main__":
    print("--- SKI WORLD CUP WALLPAPER ENGINE GESTARTET ---")
    print(f"Überwache: {file_path}")

    update_wallpaper()

    last_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0

    while True:
        try:
            if os.path.exists(file_path):
                current_mtime = os.path.getmtime(file_path)

                if current_mtime != last_mtime:
                    print("\nÄnderung erkannt! Aktualisiere...")
                    time.sleep(1) # Kurz warten falls Schreibvorgang noch läuft
                    update_wallpaper()
                    last_mtime = current_mtime

            time.sleep(5)

        except KeyboardInterrupt:
            print("\nBeendet.")
            sys.exit()
        except Exception as e:
            print(f"Loop Fehler: {e}")
            time.sleep(10)