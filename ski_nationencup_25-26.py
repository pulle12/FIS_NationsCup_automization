import pandas as pd
import matplotlib.pyplot as plt
import ctypes
from PIL import Image
import os
import time
import sys

# --- KONFIGURATION ---
EXCEL_PATH = r'C:\Users\summe\Documents\Office\Excel\ski_alpin_verlaeufe.xlsx'
SHEET_NAME = '25-26_Py_exp'
BASE_IMAGE_PATH = r'C:\Users\summe\Bilder\Sport\ski\manuel_feller.avif'
OUTPUT_IMAGE_PATH = r'C:\Users\summe\Bilder\Sport\ski\ski_nationencup_25-26.png'

# Wo soll das Diagramm auf dem Bild platziert werden? (Pixel Koordinaten)
CHART_POS_X = -150
CHART_POS_Y = 350
CHART_SIZE = (1700, 1300) # Breite, Höhe des Diagramms

def update_wallpaper():
    print("Lese Excel Daten...", end="")

    try:
        # 1. Excel laden
        df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, usecols="A:Z")

        # Erste Spalte = Rennen
        race_column = df.columns[0]
        races = df[race_column].astype(str)

        # Alle Nationen (alle anderen Spalten)
        nations = df.columns[1:]

        # 2. Plot vorbereiten
        plt.figure(figsize=(14, 10), dpi=120)
        plt.style.use('fivethirtyeight')
        wichtige = ["Österreich", "Schweiz", "Norwegen", "Frankreich", "USA", "Deutschland", "Italien", "Schweden", "Albanien", "Kroatien"]

        # Jede Nation als eigene Linie zeichnen
        for nation in nations:
            plt.plot(
                races,
                df[nation],
                linewidth=2,
                marker="o",
                markersize=5,
            )

        # Titel
        plt.title("World Cup Points by Nation (per Race)", fontsize=13, fontweight="bold")

        # Achsen
        plt.xticks(rotation=90, fontsize=7)
        plt.yticks(fontsize=9)
        plt.grid(True, alpha=0.15, linestyle="--")
        plt.box(False)

        for nation in wichtige:
            y = df[nation].iloc[-1]      # letzter Wert der Nation
            x = len(races) - 1           # letzte X-Position (da Kategorien)
            plt.text(
                x + 0.2,                 # etwas rechts neben der Linie
                y,
                nation,
                fontsize=9,
                va="center",
                ha="left",
                fontweight="bold"
            )

        # Manuelle Randeinstellung statt tight_layout()
        plt.subplots_adjust(bottom=0.30, top=0.92)

        plt.savefig("temp_chart.png", transparent=True)
        plt.close()

        # 3. Wallpaper-Bild einbetten
        base = Image.open(BASE_IMAGE_PATH).convert("RGBA")
        chart = Image.open("temp_chart.png").convert("RGBA")

        chart = chart.resize(CHART_SIZE, Image.Resampling.LANCZOS)

        base.paste(chart, (CHART_POS_X, CHART_POS_Y), chart)

        base.save(OUTPUT_IMAGE_PATH, "PNG")
        print(" Bild generiert.", end="")

        # 4. Wallpaper setzen
        abs_path = os.path.abspath(OUTPUT_IMAGE_PATH)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
        print(" Wallpaper aktualisiert!")

    except Exception as e:
        print(f"\n[FEHLER] {e}")


if __name__ == "__main__":
    print("--- SKI WORLD CUP WALLPAPER ENGINE GESTARTET ---")
    print(f"Überwache: {EXCEL_PATH}")

    last_mtime = 0

    while True:
        try:
            current_mtime = os.path.getmtime(EXCEL_PATH)

            if current_mtime != last_mtime:
                time.sleep(1)
                update_wallpaper()
                last_mtime = current_mtime

            time.sleep(5)

        except KeyboardInterrupt:
            sys.exit()
        except FileNotFoundError:
            print("Excel Datei nicht gefunden! Warte...")
            time.sleep(10)