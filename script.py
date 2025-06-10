import json
import tkinter as tk
from idlelib.history import History
from sys import prefix
import atexit
from threading import Thread
import requests
import time
import random
import webbrowser
from datetime import datetime


# Tvůj API klíč
api_key = '8b1c37144ec00c601ff2be34b1be74c8'  # <-- sem si vlož svůj klíč

# Slovník ID -> Název žánru
genre_mapping = {
    28: 'Akční',
    12: 'Dobrodružný',
    16: 'Animovaný',
    35: 'Komedie',
    80: 'Krimi',
    99: 'Dokumentární',
    18: 'Drama',
    10751: 'Rodinný',
    14: 'Fantasy',
    36: 'Historický',
    27: 'Horor',
    10402: 'Hudební',
    9648: 'Mysteriózní',
    10749: 'Romantický',
    878: 'Sci-Fi',
    10770: 'TV film',
    53: 'Thriller',
    10752: 'Válečný',
    37: 'Western'
}
genre_map = {"Vše": "Vše","Komedie": 35, "Akční": 28, "Horor": 27, "Fantasy": 14, "Válečný": 10752, "Animovaný": 16}
lang_map = {"Vše": "Vše","Anglicky": "en", "Německy": "de", "Španělsky": "es", "Hindsky":"hi"}

# Vytvoření hlavního okna
root = tk.Tk()
root.title("Náhodný film")
viewed_movies = []


# Vytvoření textového pole pro uživatelský vstup

def RunningThread():
    Download_button.config(state="disabled")
    OK_button.config(state="disabled")
    thread = Thread(target=DownloadMovies)
    thread.start()

# Funkce pro získání vybraného žánru

def clear_json_on_exit():
    with open("data.json", "w") as file:
        json.dump([], file)  # nebo [] podle struktury


# Funkce pro vyhledání filmu podle žánru

def DownloadMovies():
    count_of_pages = 10

    count_choice = (count_of_movies_entry.get())
    # Získáme vstup uživatele
    if count_choice:
        count_of_pages = int(count_choice)
    else:
        count_of_pages = 10
    base_url = 'https://api.themoviedb.org/3/discover/movie'
    popular_movies = []  # Pole na uložení všech filmů

    for page in range(1, count_of_pages + 1):
        params = {
            'api_key': api_key,
            'language': 'cs',
            'page': page,
            'sort_by': 'popularity.desc'
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            popular_movies.extend(data['results'])  # Přidání filmů z aktuální stránky
        else:
            print(f"Chyba při stahování stránky {page}: {response.status_code}")
        time.sleep(0.5)  # Pauza mezi požadavky

    if not popular_movies:
        print("No movies found.")
        return
    SaveMovies(popular_movies)
    SaveInfo(count_of_pages)
    Download_button.config(state="normal")
    OK_button.config(state="normal")

def ReadInfo():
    try:
        with open("info.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            count = data.get("count",0)
            count_info_label.config(text= ("Počet stažených stran: "+str(count)))
    except:
        pass
def FilterMovies():
    pass

def SaveMovies(popular_movies: list):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(popular_movies, f, ensure_ascii=False, indent=4)

def SaveInfo(count: int):
    count_info_label.config(text="Počet stažených stran: "+str(count))
    with open("info.json", "w", encoding="utf-8") as i:
        json.dump({"count": count}, i, ensure_ascii=False, indent=4)

def ChooseMovie():
    with open("data.json", "r", encoding="utf-8") as f:
        popular_movies = json.load(f)


    user_choice = genre_map[selected_genre.get()]
    min_year_choice= min_year_entry.get().strip().upper()
    max_year_choice= max_year_entry.get().strip().upper()
    lang_choice= lang_map[selected_lang.get()]


    if min_year_choice != "" and max_year_choice != "":
        if int(min_year_choice) > int(max_year_choice):
            return

    canditates = []


    for each_movie in popular_movies:
        if each_movie is None:
            continue
        if user_choice != "Vše":
            if user_choice in each_movie['genre_ids']:
                pass
            else:
                continue

        if min_year_choice and each_movie['release_date'][:4].isdigit():
            if int(min_year_choice) <= int(str(each_movie['release_date'][:4])):
                pass
            else:
                continue
        if max_year_choice and each_movie['release_date'][:4].isdigit():
            if int(max_year_choice) >= int(str(each_movie['release_date'][:4])):
                pass
            else:
                continue
        if lang_choice != "Vše":
            if lang_choice == str(each_movie['original_language']):
                pass
            else:
                continue
        canditates.append(each_movie)

    if len(canditates) == 0:
        return

    random_movie = random.choice(canditates)  # Vyber náhodný film



    movie_genres = [genre_mapping.get(genre_id, 'Neznámý') for genre_id in random_movie['genre_ids']]
    result_label.configure(text=f"{random_movie['title']} \n {', '.join(movie_genres)}")
    viewed_movies.append(random_movie)
    url = f"https://prehraj.to/hledej/{random_movie['title']}"
    webbrowser.open_new_tab(url)
# Vstupní pole pro zadání žánru
def validate_input(new_value):
    if new_value == "":
        return True  # umožní mazání
    return new_value.isdigit() and len(new_value) <= 4

        # povolit průběžné zadávání, ale kontrolovat rozsah až při 4 číslicích

def validate_count(new_value):
    if new_value == "":
        return True
    if new_value.isdigit():
        return int(new_value) <= 500
    return False

def ShowViewMovies():
    if not viewed_movies:
        return  # Není co zobrazovat

    view_window = tk.Toplevel(root)
    view_window.title("Zobrazené filmy")

    label = tk.Label(view_window, text="Zobrazené filmy:")
    label.pack()

    for movie in viewed_movies:
        title = movie.get('title', 'Neznámý název')
        year = movie.get('release_date', '')[:4]
        genres = [genre_mapping.get(genre_id, 'Neznámý') for genre_id in movie.get('genre_ids', [])]
        movie_info = f"{title} ({year}) – {', '.join(genres)}"
        tk.Label(view_window, text=movie_info, anchor="w").pack(fill="x", padx=10, pady=2)

genre_info = tk.Label(root, text="Žánr")
genre_info.pack()

selected_genre = tk.StringVar()
selected_genre.set("Vše")  # Výchozí hodnota
genre_menu = tk.OptionMenu(root, selected_genre, *genre_map.keys())
genre_menu.pack()



# Registrace validátorů
vcmd_year = (root.register(validate_input), '%P')
vcmd_count = (root.register(validate_count), '%P')

# Rok "Od"
year_info = tk.Label(root, text="Od roku")
year_info.pack()

min_year_entry = tk.Entry(root, validate='key', validatecommand=vcmd_year)
min_year_entry.pack()

# Rok "Do"
year_info = tk.Label(root, text="Do roku")
year_info.pack()

max_year_entry = tk.Entry(root, validate='key', validatecommand=vcmd_year)
max_year_entry.pack()


# Tlačítko pro zpracování

year_info = tk.Label(root, text="Původní jazyk")
year_info.pack()
selected_lang = tk.StringVar()
selected_lang.set("Vše")  # Výchozí hodnota
lang_menu = tk.OptionMenu(root, selected_lang, *lang_map.keys())
lang_menu.pack()


empty_label = tk.Label(root, text="")
empty_label.pack()
OK_button = tk.Button(root, text="Vybrat film", command=ChooseMovie)
OK_button.pack()

history_button = tk.Button(root, text="Ukaž historii", command=ShowViewMovies)
history_button.pack()


# Místo pro zobrazení výsledku
result_label = tk.Label(root, text="")
result_label.pack()


count_info_label = tk.Label(root, text="0")
count_info_label.pack()



count_label = tk.Label(root, text="Počet stránek")
count_label.pack()


count_of_movies_entry = tk.Entry(root,validate='key', validatecommand=vcmd_count)
count_of_movies_entry.pack()



Download_button = tk.Button(root, text="Stáhnout databázi filmů", command= RunningThread)
Download_button.pack()
ReadInfo()







# Zaregistruj funkci, která se zavolá při ukončení
# Spuštění hlavní smyčky pro GUI
root.mainloop()
