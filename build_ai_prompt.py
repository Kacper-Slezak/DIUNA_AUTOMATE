import json

GAME_STATE_FILE = 'game_state.json'
AI_PLAYER_NAME = 'Peter'

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"BŁĄD KRYTYCZNY: Nie można wczytać pliku {file_path}. Błąd: {e}")
        return None

def generate_ai_prompt(game_state):
    
    game_state.load_json_file(GAME_STATE_FILE)
    if not game_state:
        return "BŁĄD KRYTYCZNY: Nie można wczytać stanu gry."
    
    prompt_lines = []
    prompt_lines.append("Uwaga teraz twoja kolej, Peter! Jesteś graczem w grze planszowej. Twoim zadaniem jest podjęcie najlepszego możliwego ruchu na podstawie aktualnego stanu gry.\n")
    prompt_lines.append("Aktualny stan gry jest następujący:\n")

    players_moves = {}

    if "round_history" in game_state :
        for move in game_state["round_history"]:
            player = move["player"]
            summary = move["summary"]
            if player not in players_moves:
                players_moves[player] = []
            players_moves[player].append(move["summary"])
    
    for player, moves in players_moves.items():
        prompt_lines.append(f"Ruchy gracza {player}:\n")
        for i, move_summary in enumerate(moves, 1):
            prompt_lines.append(f"    {i}. {move_summary}")
    
    prompt_lines.append(f"\nTeraz twój ruch ({AI_PLAYER_NAME}).")
    prompt_lines.append("Przeanalizuj poniższy stan JSON.")
    prompt_lines.append("\n### STAN GRY (Źródło Prawdy) ###")


    if "round_history" in game_state:
        del game_state["round_history"]
        
    # Sformatuj JSON
    game_state_json_string = json.dumps(game_state, indent=2, ensure_ascii=False)
    
    # --- Połącz wszystko ---
    final_prompt = "\n".join(prompt_lines)
    final_prompt += f"\n```json\n{game_state_json_string}\n```"

    return final_prompt

if __name__ == "__main__":
    final_prompt_text = generate_ai_prompt()
    if final_prompt_text:
        print("--- GOTOWY PROMPT DO WKLEJENIA DLA AI ---")
        print(final_prompt_text)
        
        try:
            with open("ai_prompt.txt", "w", encoding="utf-8") as f:
                f.write(final_prompt_text)
            print("\n(Powyższy prompt został też zapisany do pliku 'ai_prompt.txt')")
        except Exception as e:
            print(f"\nNie udało się zapisać promptu do pliku: {e}")
