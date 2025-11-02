import json
import os

# UWAGA: Nazwy plików są poprawione, aby pasowały do tych przesłanych:
LOCATIONS_DB_FILE = 'locations.json'
CARDS_DB_FILE = 'cards.json'
GAME_STATE_FILE = 'game_stat.json'

def load_json_file(filename):
    """Wczytuje plik JSON i zwraca jego zawartość."""
    try:
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
        return True 
    except IOError:
        return False

def find_location_id_by_name(locations_db, search_name):
    """Znajduje ID lokacji po nazwie."""
    search_name_lower = search_name.lower()
    for location_id, data in locations_db.items():
        if data["name"].lower() == search_name_lower:
            return location_id
    return None

def find_card_id_by_name(cards_db, search_name):
    """Znajduje ID karty po nazwie."""
    search_name_lower = search_name.lower()
    for card_id, data in cards_db.items():
        if data["name"].lower() == search_name_lower:
            return card_id
    return None

def is_move_valid(game_state, locations_db, cards_db, player_name, card_id, location_id):
    """Waliduje ruch gracza (z wykorzystaniem ID karty i lokacji)."""
    
    # --- Walidacja 1: Lokacja i Karta ---
    if location_id not in locations_db:
        return False, "Nieprawidłowa lokalizacja (ID)."
    if card_id not in cards_db:
        return False, "Nieprawidłowa karta (ID)."

    location_data = locations_db[location_id]
    card_data = cards_db[card_id]

    # --- Walidacja 2: Zajętość Lokacji ---
    location_state = game_state.get("locations_state", {}).get(location_id, {})
    if location_state.get("occupied_by") is not None:
        return False, f"Lokalizacja jest już zajęta przez gracza {location_state['occupied_by']}."

    # --- Walidacja 3: Posiadanie Karty (JEDEN SPOSÓB DLA WSZYSTKICH) ---
    player_state = game_state.get("players", {}).get(player_name, {})
    player_pool = player_state.get("deck_pool", [])
    
    if card_id not in player_pool:
        return False, f"Gracz {player_name} nie posiada karty '{card_data['name']}' w swojej puli kart (deck_pool)."
            
    # --- Walidacja 4: Symbol Agenta ---
    required_symbol = location_data.get("symbol_required")
    card_symbols = card_data.get("agent_symbols", [])
    
    if required_symbol and required_symbol not in card_symbols:
        return False, f"Karta '{card_data['name']}' (symbole: {card_symbols}) nie pasuje do lokacji '{location_data['name']}' (wymagany symbol: {required_symbol})."

    # --- Walidacja 5: Koszt Lokacji ---
    location_cost = location_data.get("cost", [])
    player_resources = player_state.get("resources", {})

    for cost_item in location_cost:
        if cost_item.get("type") == "resource":
            resource_name = cost_item.get("resource")
            required_amount = cost_item.get("amount", 0)
            player_has = player_resources.get(resource_name, 0)
            
            if player_has < required_amount:
                return False, f"Gracz {player_name} nie ma wystarczająco zasobów. Wymagane: {required_amount} {resource_name}, Posiadane: {player_has}."

    return True, "Ruch jest prawidłowy."


def process_move(game_state, locations_db, cards_db, player_name, card_id, location_id):
    """Przetwarza poprawny ruch."""
    
    card_name = cards_db.get(card_id, {}).get("name", card_id)
    location_name = locations_db.get(location_id, {}).get("name", location_id)
    location_data = locations_db.get(location_id, {})
    
    # 1. Zapewnij istnienie klucza locations_state
    if "locations_state" not in game_state:
         game_state["locations_state"] = {}
         
    if location_id not in game_state["locations_state"]:
         game_state["locations_state"][location_id] = {"occupied_by": None} 

    # 2. Zaznacz lokację jako zajętą
    game_state["locations_state"][location_id]["occupied_by"] = player_name
    
    # 3. Przetwórz koszty
    player_state = game_state.get("players", {}).get(player_name, {})
    player_resources = player_state.get("resources", {})
    location_cost = location_data.get("cost", [])
    
    for cost_item in location_cost:
        if cost_item.get("type") == "resource":
            resource_name = cost_item.get("resource")
            resource_amount = cost_item.get("amount", 0)
            current_amount = player_resources.get(resource_name, 0)
            player_resources[resource_name] = current_amount - resource_amount
            
    # 4. Dodaj do historii
    move_summary = f"{player_name} played '{card_name}' on '{location_name}'."
    if "round_history" not in game_state:
        game_state["round_history"] = []
        
    game_state["round_history"].append({
        "player": player_name,
        "card": card_name,
        "location": location_name,
        "summary": move_summary
    })
    return game_state

