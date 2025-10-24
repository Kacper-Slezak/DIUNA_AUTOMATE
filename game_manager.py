import json
import os

LOCATIONS_DB_FILE = 'locations_db.json'
CARDS_DB_FILE = 'cards_db.json'
GAME_STATE_FILE = 'game_state.json'

def load_json_file(filename):
    """Wczytuje plik JSON i zwraca jego zawartość."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"BŁĄD KRYTYCZNY: Nie znaleziono pliku {filename}!")
        return None
    except json.JSONDecodeError:
        print(f"BŁĄD KRYTYCZNY: Plik {filename} jest uszkodzony lub nie jest JSONem!")
        return None

def save_json_file(filename, data):
    """Zapisuje dane (słownik) do pliku JSON."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"BŁĄD KRYTYCZNY: Nie można zapisać do pliku {filename}. Błąd: {e}")

def print_game_state(game_state):
    """
    Prints the current game state in a readable format.

    Args:
        game_state (dict): The current state of the game.
    """
    if "round_history" in game_state and game_state["round_history"]:
        for move in game_state["round_history"]:
            print(f"- {move['summary']}")
    else:
        print("(Brak ruchów w tej rundzie)")
    print("---------------------------\n")

def is_move_valid(game_state, locations_db, cards_db, player_name, card_name, location_id):
    if location_id not in locations_db:
        return False, "Nieprawidłowa lokalizacja."
    if game_state["locations_state"][location_id]["owner"] is not None:
        zajmującycy = game_state["locations_state"][location_id]["owner"]
        return False, f"Lokalizacja jest już zajęta przez gracza {zajmującycy}."
    if card_name not in cards_db:
        return False, "Nieprawidłowa karta."
    TODO: Dodaj więcej reguł walidacji ruchu tutaj.
    TODO: Sprawdź, czy gracz posiada kartę.
    TODO: Sprawdź, czy karta może być zagrana w danej lokalizacji.    
    return True, "Ruch jest prawidłowy."
    
def process_move(game_state, locations_db, player_name, card_name, location_id):
    
    print(f"Ruch poprawny. Gracz {player_name} gra '{card_name}' na '{location_id}'.")
    
    game_state["locations_state"][location_id]["occupied_by"] = player_name
    
    # 2. TODO: Przetwórz efekty i koszty
    # (Tutaj odejmujesz koszty, dodajesz zasoby, itp.)
    # ...

    move_summary = f"{player_name} played '{card_name}' on '{location_id}'."
    
    # TODO: Rozbuduj summary o efekty
    # np. "Helen played 'Gathering Machine' on 'Hagga Basin' (Cost: 1 Woda, Gain: 6 Przypraw)."

    if "round_history" not in game_state:
        game_state["round_history"] = []
        
    game_state["round_history"].append({
        "player": player_name,
        "card": card_name,
        "location": location_id,
        "summary": move_summary
    })

    # 4. TODO: Przenieś kartę z ręki do zagranych

    return game_state

def find_location_id_by_name(locations_db, search_name):
    search_name_lower = search_name.lower()
    
    for location_id, data in locations_db.items():
        if data["name"].lower() == search_name_lower:
            return location_id

    possible_matches = []
    for location_id, data in locations_db.items():
        if search_name_lower in data["name"].lower():
            possible_matches.append(location_id)
            
    if len(possible_matches) == 1:
        return possible_matches[0]
    elif len(possible_matches) > 1:
        print(f"BŁĄD: Nazwa '{search_name}' pasuje do wielu lokacji. Bądź bardziej precyzyjny.")
        return None
    else:
        print(f"BŁĄD: Nie znaleziono lokacji o nazwie podobnej do '{search_name}'.")
        return None

def main():
    locations_db = load_json_file(LOCATIONS_DB_FILE)
    cards_db = load_json_file(CARDS_DB_FILE)
    if not locations_db or not cards_db:
        return

    print("Witaj w Asystencie Gry 'Dune: Imperium'!")
    print("Wpisz 'koniec' aby zakończyć.")
    while True:
        game_state = load_json_file(GAME_STATE_FILE)
        if not game_state:
            break
            
        os.system('cls' if os.name == 'nt' else 'clear')
        print_game_state(game_state)

        player_name = input("Kto wykonuje ruch?: ")
        if player_name.lower() == 'koniec':
            break
        
        # TODO: Zrób to samo dla kart! (find_card_id_by_name)
        card_name = input(f"Jakiej karty używa {player_name}?: ")
        if card_name.lower() == 'koniec':
            break

        location_name_input = input("Na jaką lokację idzie? (Nazwa lokacji): ")
        if location_name_input.lower() == 'koniec':
            break

        location_id = find_location_id_by_name(locations_db, location_name_input)

        # TODO: Tłumaczenie nazwy karty na ID karty
        # card_id = find_card_id_by_name(cards_db, card_name_input)


        if is_move_valid(game_state, locations_db, cards_db, player_name, card_name, location_id):
            
            game_state = process_move(game_state, locations_db, player_name, card_name, location_id)
            
            save_json_file(GAME_STATE_FILE, game_state)
            print("Zapisano nowy stan gry i dodano ruch do historii.")
            
        else:
            print("Ruch niepoprawny. Spróbuj ponownie.")
            
        input("\nNaciśnij Enter, aby kontynuować...")

if __name__ == "__main__":
    main()