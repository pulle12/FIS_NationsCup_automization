import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys

DEFAULT_RESULTS = os.path.join(os.path.dirname(__file__), "results.json")


def load_results(path: str = DEFAULT_RESULTS):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    races = data.get("races", []) if isinstance(data, dict) else data
    return races


def aggregate(races, discipline_filter: str, gender_filter: str):
    totals = {}
    for race in races:
        meta = race.get("meta", {}) if isinstance(race, dict) else {}
        disc = meta.get("discipline", "unknown").lower()
        gender = meta.get("gender", "unknown").lower()

        if discipline_filter != "Alle" and discipline_filter.lower() != disc:
            continue
        if gender_filter != "Alle" and gender_filter.lower() != gender:
            continue

        for nation, pts in race.get("points", {}).items():
            totals[nation] = totals.get(nation, 0) + pts
    return sorted(totals.items(), key=lambda x: x[1], reverse=True)


def unique_values(races, key):
    vals = set()
    for race in races:
        meta = race.get("meta", {}) if isinstance(race, dict) else {}
        vals.add(meta.get(key, "unknown"))
    return sorted(v for v in vals if v)


def main():
    root = tk.Tk()
    root.title("Ski Nationencup Viewer")
    root.geometry("520x500")

    state = {"races": [], "path": DEFAULT_RESULTS}

    def run_fetch_ids():
        try:
            py = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
            if not os.path.exists(py):
                py = sys.executable
            subprocess.run([py, os.path.join(os.path.dirname(__file__), "fetch_race_ids.py")], check=False)
            messagebox.showinfo("IDs", "Race-IDs wurden (neu) geladen. Bitte results neu scrapen.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte IDs nicht laden: {e}")

    def refresh_options():
        discs = ["Alle"] + unique_values(state["races"], "discipline")
        genders = ["Alle"] + unique_values(state["races"], "gender")
        discipline_cb["values"] = discs
        gender_cb["values"] = genders
        if discs:
            discipline_var.set(discs[0])
        if genders:
            gender_var.set(genders[0])

    def load_file(path=None):
        if not path:
            path = filedialog.askopenfilename(initialdir=os.path.dirname(DEFAULT_RESULTS), filetypes=[("JSON", "*.json")])
            if not path:
                return
        try:
            state["races"] = load_results(path)
            state["path"] = path
            refresh_options()
            update_list()
            status_var.set(f"Geladen: {os.path.basename(path)} ({len(state['races'])} Rennen)")
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Datei nicht laden: {e}")

    def update_list(*_args):
        discipline = discipline_var.get() or "Alle"
        gender = gender_var.get() or "Alle"
        rows = aggregate(state["races"], discipline, gender)
        tree.delete(*tree.get_children())
        for nation, pts in rows:
            tree.insert("", "end", values=(nation, pts))

    top = ttk.Frame(root, padding=10)
    top.pack(fill="x")

    ttk.Label(top, text="Disziplin:").grid(row=0, column=0, padx=4, pady=4, sticky="w")
    discipline_var = tk.StringVar(value="Alle")
    discipline_cb = ttk.Combobox(top, textvariable=discipline_var, state="readonly")
    discipline_cb.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

    ttk.Label(top, text="Geschlecht:").grid(row=0, column=2, padx=4, pady=4, sticky="w")
    gender_var = tk.StringVar(value="Alle")
    gender_cb = ttk.Combobox(top, textvariable=gender_var, state="readonly")
    gender_cb.grid(row=0, column=3, padx=4, pady=4, sticky="ew")

    for cb in (discipline_cb, gender_cb):
        cb.bind("<<ComboboxSelected>>", update_list)

    load_btn = ttk.Button(top, text="Datei laden", command=lambda: load_file())
    load_btn.grid(row=0, column=4, padx=4, pady=4)

    ids_btn = ttk.Button(top, text="IDs neu laden", command=run_fetch_ids)
    ids_btn.grid(row=0, column=5, padx=4, pady=4)

    top.columnconfigure(1, weight=1)
    top.columnconfigure(3, weight=1)

    tree = ttk.Treeview(root, columns=("Nation", "Punkte"), show="headings")
    tree.heading("Nation", text="Nation")
    tree.heading("Punkte", text="Punkte")
    tree.column("Nation", width=120, anchor="w")
    tree.column("Punkte", width=100, anchor="e")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    status_var = tk.StringVar(value="Keine Datei geladen")
    ttk.Label(root, textvariable=status_var, anchor="w").pack(fill="x", padx=10, pady=(0, 10))

    # Initiales Laden, falls Datei existiert
    if os.path.exists(DEFAULT_RESULTS):
        load_file(DEFAULT_RESULTS)

    root.mainloop()


if __name__ == "__main__":
    main()
