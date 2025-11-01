import json
import os

# UWAGA: Nazwy plików są poprawione, aby pasowały do tych przesłanych:
LOCATIONS_DB_FILE = 'locations.json'
CARDS_DB_FILE = 'cards.json'
GAME_STATE_FILE = 'game_stat.json'

def load_json_file(filename):
    """Wczytuje plik JSON i zwraca jego zawartość."""
    try:
        # Zmieniono, aby używać ścieżki względnej, która działa z Flaskiem
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def save_json_file(filename, data):
    """Zapisuje dane (słownik) do pliku JSON."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True # Dodano zwrot True/False dla Flask
    except IOError:
        return False

def find_location_id_by_name(locations_db, search_name):
    """Znajduje ID lokacji po nazwie."""
    search_name_lower = search_name.lower()
    
    for location_id, data in locations_db.items():
        if data["name"].lower() == search_name_lower:
            return location_id
    
    # Usuwamy niepotrzebne printy i zwracamy None, aby Flask mógł obsłużyć błąd
    return None

# 👇 Nowa funkcja (zgodnie z TODO w oryginalnym pliku)
def find_card_id_by_name(cards_db, search_name):
    """Znajduje ID karty po nazwie."""
    search_name_lower = search_name.lower()
    
    for card_id, data in cards_db.items():
        if data["name"].lower() == search_name_lower:
            return card_id
            
    # Podobnie jak w find_location, zwracamy None w przypadku braku dopasowania
    return None

# UWAGA: Funkcja is_move_valid została uproszczona i dostosowana do używania ID karty i ID lokacji
def is_move_valid(game_state, locations_db, cards_db, player_name, card_id, location_id):
    """Waliduje ruch gracza (z wykorzystaniem ID karty i lokacji)."""
    if location_id not in locations_db:
        return False, "Nieprawidłowa lokalizacja (ID)."
    
    # Używamy 'occupied_by' do sprawdzenia zajętości (dla spójności z process_move)
    location_state = game_state.get("locations_state", {}).get(location_id, {})
    if location_state.get("occupied_by") is not None:
        return False, f"Lokalizacja jest już zajęta przez gracza {location_state['occupied_by']}."

    if card_id not in cards_db:
        return False, "Nieprawidłowa karta (ID)."
    
    # TODO: Sprawdź, czy gracz posiada kartę. (Logika dla Ciebie)
    
    return True, "Ruch jest prawidłowy."

# UWAGA: Funkcja process_move została zmieniona, aby używać ID karty i lokacji
def process_move(game_state, locations_db, cards_db, player_name, card_id, location_id):
    """Przetwarza poprawny ruch."""
    
    card_name = cards_db.get(card_id, {}).get("name", card_id) # Pobierz nazwę karty
    location_name = locations_db.get(location_id, {}).get("name", location_id) # Pobierz nazwę lokacji
    
    # Zapewnij istnienie klucza locations_state
    if "locations_state" not in game_state:
         game_state["locations_state"] = {}
         
    if location_id not in game_state["locations_state"]:
         game_state["locations_state"][location_id] = {"occupied_by": None} 

    # 1. Zaznacz lokację jako zajętą
    game_state["locations_state"][location_id]["occupied_by"] = player_name
    
    # 2. TODO: Przetwórz efekty i koszty
    
    move_summary = f"{player_name} played '{card_name}' on '{location_name}'."
    
    if "round_history" not in game_state:
        game_state["round_history"] = []
        
    game_state["round_history"].append({
        "player": player_name,
        "card": card_name,
        "location": location_name,
        "summary": move_summary
    })

    # 4. TODO: Przenieś kartę z ręki do zagranych

    return game_state
