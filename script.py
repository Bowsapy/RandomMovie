import tkinter as tk
from tkinter import messagebox
from threading import Thread
import requests
import json
import time
import random
import webbrowser

GENRE_MAPPING = {
    28: 'Akční', 12: 'Dobrodružný', 16: 'Animovaný', 35: 'Komedie',
    80: 'Krimi', 99: 'Dokumentární', 18: 'Drama', 10751: 'Rodinný',
    14: 'Fantasy', 36: 'Historický', 27: 'Horor', 10402: 'Hudební',
    9648: 'Mysteriózní', 10749: 'Romantický', 878: 'Sci-Fi',
    10770: 'TV film', 53: 'Thriller', 10752: 'Válečný', 37: 'Western'
}

GENRE_FILTER = {"Vše": "Vše", "Komedie": 35, "Akční": 28, "Horor": 27, "Fantasy": 14, "Válečný": 10752, "Animovaný": 16}
LANG_FILTER = {"Vše": "Vše", "Anglicky": "en", "Německy": "de", "Španělsky": "es", "Hindsky": "hi"}

class MovieApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Náhodný film")
        self.viewed_movies = []

        self.create_widgets()
        self.load_info()

    def create_widgets(self):
        # Řádek 0 – Žánr
        self.genre_label = tk.Label(self.root, text="Žánr:")
        self.genre_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.genre_var = tk.StringVar(value="Vše")
        tk.OptionMenu(self.root, self.genre_var, *GENRE_FILTER.keys()).grid(row=0, column=1, padx=10, pady=5,
                                                                            sticky="w")

        # Řádek 1 – Od roku
        self.year_from_label = tk.Label(self.root, text="Od roku:")
        self.year_from_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.year_from_entry = tk.Entry(self.root, validate="key",
                                        validatecommand=(self.root.register(self.validate_year), "%P"))
        self.year_from_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Řádek 2 – Do roku
        self.year_to_label = tk.Label(self.root, text="Do roku:")
        self.year_to_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.year_to_entry = tk.Entry(self.root, validate="key",
                                      validatecommand=(self.root.register(self.validate_year), "%P"))
        self.year_to_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Řádek 3 – Jazyk
        self.lang_label = tk.Label(self.root, text="Původní jazyk:")
        self.lang_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.lang_var = tk.StringVar(value="Vše")
        tk.OptionMenu(self.root, self.lang_var, *LANG_FILTER.keys()).grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Řádek 4 – Tlačítka
        self.pick_button = tk.Button(self.root, text="Vybrat film", command=self.choose_movie)
        self.pick_button.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.history_button = tk.Button(self.root, text="Zobrazit historii", command=self.show_history)
        self.history_button.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Řádek 5 – Počet stran info
        self.count_info_label = tk.Label(self.root, text="Počet stažených stran: 0")
        self.count_info_label.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        # Řádek 6 – Zadej počet stran
        self.page_count_label = tk.Label(self.root, text="Počet stránek:")
        self.page_count_label.grid(row=6, column=0, padx=10, pady=5, sticky="e")
        self.page_count_entry = tk.Entry(self.root, validate="key",
                                         validatecommand=(self.root.register(self.validate_page_count), "%P"))
        self.page_count_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")

        # Řádek 7 – API klíč
        self.api_label = tk.Label(self.root, text="Zadej API klíč:")
        self.api_label.grid(row=7, column=0, padx=10, pady=5, sticky="e")
        self.api_entry = tk.Entry(self.root)
        self.api_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
        self.download_button = tk.Button(self.root, text="Stáhnout databázi filmů", command=self.start_download_thread)
        self.download_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        # Řádek 9 – Výsledek
        self.result_label = tk.Label(self.root, text="", wraplength=300)
        self.result_label.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    def validate_year(self, value):
        return value.isdigit() and len(value) <= 4 or value == ""

    def validate_page_count(self, value):
        return value.isdigit() and int(value) <= 500 or value == ""

    def start_download_thread(self):
        Thread(target=self.download_movies).start()

    def is_api_key_valid(self, api_key):
        url = "https://api.themoviedb.org/3/configuration"
        return requests.get(url, params={"api_key": api_key}).status_code == 200

    def download_movies(self):
        api_key = self.api_entry.get()
        if not api_key:
            messagebox.showerror("Chyba", "Zadej API klíč.")
            return
        if not self.is_api_key_valid(api_key):
            messagebox.showerror("Chyba", "Neplatný API klíč.")
            return

        pages = int(self.page_count_entry.get()) if self.page_count_entry.get() else 10
        url = "https://api.themoviedb.org/3/discover/movie"
        all_movies = []

        self.download_button.config(state="disabled")
        self.pick_button.config(state="disabled")

        for page in range(1, pages + 1):
            params = {
                "api_key": api_key,
                "language": "cs",
                "page": page,
                "sort_by": "popularity.desc"
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                all_movies.extend(response.json().get("results", []))
            time.sleep(0.5)

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(all_movies, f, ensure_ascii=False, indent=4)

        with open("info.json", "w", encoding="utf-8") as f:
            json.dump({"count": pages}, f, ensure_ascii=False, indent=4)

        self.count_info_label.config(text=f"Počet stažených stran: {pages}")
        self.download_button.config(state="normal")
        self.pick_button.config(state="normal")

    def choose_movie(self):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                movies = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Chyba", "Nejdřív stáhni databázi filmů.")
            return

        genre = GENRE_FILTER[self.genre_var.get()]
        lang = LANG_FILTER[self.lang_var.get()]
        min_year = self.year_from_entry.get()
        max_year = self.year_to_entry.get()

        candidates = []
        for movie in movies:
            if genre != "Vše" and genre not in movie["genre_ids"]:
                continue
            year = movie.get("release_date", "")[:4]
            if min_year and year < min_year: continue
            if max_year and year > max_year: continue
            if lang != "Vše" and movie["original_language"] != lang:
                continue
            candidates.append(movie)

        if not candidates:
            messagebox.showinfo("Info", "Žádný film neodpovídá filtru.")
            return

        chosen = random.choice(candidates)
        genres = [GENRE_MAPPING.get(gid, "Neznámý") for gid in chosen.get("genre_ids", [])]
        self.result_label.config(text=f"{chosen['title']} - {', '.join(genres)}")
        self.viewed_movies.append(chosen)
        webbrowser.open_new_tab(f"https://prehraj.to/hledej/{chosen['title']}")

    def show_history(self):
        if not self.viewed_movies:
            return

        history_win = tk.Toplevel(self.root)
        history_win.title("Historie zhlédnutých filmů")
        for movie in self.viewed_movies:
            title = movie.get("title", "Neznámý")
            year = movie.get("release_date", "")[:4]
            genres = [GENRE_MAPPING.get(gid, "Neznámý") for gid in movie.get("genre_ids", [])]
            label = tk.Label(history_win, text=f"{title} ({year}) – {', '.join(genres)}", anchor="w")
            label.pack(fill="x", padx=10, pady=2)

    def load_info(self):
        try:
            with open("info.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                count = data.get("count", 0)
                self.count_info_label.config(text=f"Počet stažených stran: {count}")
        except:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = MovieApp(root)
    root.mainloop()
