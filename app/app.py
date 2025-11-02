# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
# import random <-- USUNIĘTE

from game_manager import load_json_file, save_json_file, is_move_valid, process_move
from build_ai_prompt import generate_ai_prompt, AI_PLAYER_NAME

# Użyjemy stałych z game_manager.py
from game_manager import LOCATIONS_DB_FILE, CARDS_DB_FILE, GAME_STATE_FILE

app = Flask(__name__)
app.secret_key = 'twoj_super_tajny_klucz_dune' 

def get_game_data():
    """Wczytuje i zwraca stan gry, karty i lokacje."""
    game_state = load_json_file(GAME_STATE_FILE)
    locations_db = load_json_file(LOCATIONS_DB_FILE)
    cards_db = load_json_file(CARDS_DB_FILE)
    
    return game_state, locations_db, cards_db

def get_player_names(game_state):
    """Pobiera nazwy graczy."""
    if game_state and "players" in game_state:
        return sorted(list(game_state["players"].keys()))
    return []

def get_available_locations(locations_db, game_state):
    """Zwraca listę wolnych lokacji."""
    available_locations = []
    
    for loc_id, loc_data in locations_db.items():
        location_state = game_state.get("locations_state", {}).get(loc_id, {})
        if location_state.get("occupied_by") is None:
             available_locations.append({
                "id": loc_id,
                "name": loc_data["name"]
            })
    return available_locations

# --- FUNKCJA draw_cards_for_ai() ZOSTAŁA USUNIĘTA ---

@app.route('/', methods=['GET', 'POST'])
def index():
    game_state, locations_db, cards_db = get_game_data()

    if game_state is None or locations_db is None or cards_db is None:
        flash("BŁĄD KRYTYCZNY: Nie można wczytać danych gry. Sprawdź pliki JSON.", "error")
        return render_template('error.html'), 500

    current_player = game_state.get("currentPlayer", "Nieznany Gracz")
    round_history = game_state.get("round_history", [])
    player_names = get_player_names(game_state)
    available_locations = get_available_locations(locations_db, game_state)
    
    # --- UPROSZCZONA LOGIKA MAPY KART ---
    # Traktuje wszystkich graczy tak samo, pobierając dane z 'deck_pool'
    player_card_map = {}
    player_states = game_state.get("players", {})
    
    for player_name, player_data in player_states.items():
        # Używaj 'deck_pool' dla WSZYSTKICH graczy
        card_ids_list = player_data.get("deck_pool", [])
        
        player_card_list = []
        for card_id in card_ids_list:
            if card_id in cards_db:
                player_card_list.append({
                    "id": card_id,
                    "name": cards_db[card_id].get("name", card_id)
                })
        
        player_card_map[player_name] = sorted(player_card_list, key=lambda x: x['name'])
    # --- KONIEC UPROSZCZONEJ LOGIKI ---


    if request.method == 'POST':
        player_name_input = request.form.get('player_name')
        card_id_input = request.form.get('card_id')
        location_id_input = request.form.get('location_id')

        is_valid, message = is_move_valid(game_state, locations_db, cards_db, player_name_input, card_id_input, location_id_input)

        if is_valid:
            new_game_state = process_move(game_state, locations_db, cards_db, player_name_input, card_id_input, location_id_input)
            
            if save_json_file(GAME_STATE_FILE, new_game_state):
                 flash(f"Sukces! Ruch gracza {player_name_input} zagrany.", "success")
            else:
                 flash("BŁĄD KRYTYCZNY: Nie można zapisać stanu gry na dysku.", "error")
        else:
            flash(f"Ruch niepoprawny: {message}", "error")
        
        return redirect(url_for('index'))

    return render_template('index.html', 
        current_player=current_player,
        round_history=round_history,
        player_names=player_names,
        player_card_map=player_card_map,
        locations=available_locations,
        ai_player_name=AI_PLAYER_NAME
    )

@app.route('/ai_prompt')
def ai_prompt():
    game_state, _, _ = get_game_data()
    
    if game_state is None:
        flash("BŁĄD KRYTYCZNY: Nie można wczytać danych gry.", "error")
        return render_template('error.html'), 500
        
    prompt_text = generate_ai_prompt(game_state) 
    
    return render_template('ai_prompt.html', 
        prompt_text=prompt_text,
        ai_player_name=AI_PLAYER_NAME
    )
    
@app.route('/reset_board')
def reset_board():
    """Pozwala na reset zajętych lokacji dla nowej rundy."""
    game_state, _, _ = get_game_data()
    if game_state:
        # 1. Reset lokacji
        if "locations_state" in game_state:
            for loc_id in game_state["locations_state"]:
                game_state["locations_state"][loc_id]["occupied_by"] = None
        
        game_state["round_history"] = []
        game_state["round"] = game_state.get("round", 0) + 1

        # 2. CAŁA LOGIKA TASOWANIA AI USUNIĘTA
        # Aplikacja nie musi już tego śledzić.

        if save_json_file(GAME_STATE_FILE, game_state):
            flash("Plansza została zresetowana, rozpoczęto nową rundę!", "success")
        else:
            flash("BŁĄD: Nie udało się zapisać zmian stanu gry.", "error")
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("Uruchamianie serwera na adresie http://0.0.0.0:5000")
    print("Aby uzyskać dostęp z innych komputerów, użyj adresu IP Twojego komputera, np. http://192.168.1.10:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)