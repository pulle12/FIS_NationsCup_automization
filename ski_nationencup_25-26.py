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
            race_labels.append(str(entry['race_id']))

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

            plt.plot(
                x_axis,
                df[code],
                linewidth=2,
                marker="o",
                markersize=4,
                alpha=1.0,
                label=full_name if full_name in wichtige else None
            )

        # Titel
        plt.title("Nationencup Saisonverlauf 2025/26", fontsize=16, fontweight="bold")
        plt.ylabel("Punkte", fontsize=12)
        # Achsen
        plt.xticks(ticks=x_axis, labels=race_labels, rotation=45, fontsize=8, ha='right')
        plt.xlim(left=0, right=len(df) + 2) 

        for code in nations:
            full_name = NATION_MAP.get(code, code)
            if full_name in wichtige:
                y_pos = df[code].iloc[-1]
                x_pos = len(df) - 1
                
                # Farbe holen (gleich wie Linie)
                col = NATION_COLORS.get(full_name, "black")
                
                plt.text(
                    x_pos + 0.3, y_pos, 
                    f" {full_name}\n {int(y_pos)}", 
                    fontsize=11, 
                    va="center", 
                    fontweight="bold",
                    color=col
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
            base.paste(chart, (CHART_POS_X, CHART_POS_Y), chart)
            base.save(OUTPUT_IMAGE_PATH, "PNG")
            
            # 4. Wallpaper setzen
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