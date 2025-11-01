# build_ai_prompt.py
import json

AI_PLAYER_NAME = 'Peter'


def generate_ai_prompt(game_state_data):
    """
    Generates the AI prompt text from the game state dictionary.
    
    Args:
        game_state_data (dict): The current state of the game.
        
    Returns:
        str: The final prompt text.
    """
    if not game_state_data:
        return "BŁĄD KRYTYCZNY: Nie można wczytać stanu gry."

    # Tworzę kopię, aby bezpiecznie usunąć 'round_history' tylko z kopii JSONa do wklejenia
    game_state = game_state_data.copy()
    
    prompt_lines = []
    prompt_lines.append("Uwaga teraz twoja kolej, Peter! Jesteś graczem w grze planszowej. Twoim zadaniem jest podjęcie najlepszego możliwego ruchu na podstawie aktualnego stanu gry.\n")
    prompt_lines.append("Aktualny stan gry jest następujący:\n")

    players_moves = {}

    # Zbieranie ruchów z historii
    if "round_history" in game_state : #
        for move in game_state["round_history"]:
            player = move["player"]
            summary = move["summary"]
            if player not in players_moves:
                players_moves[player] = []
            players_moves[player].append(move["summary"])
    
    # Usuwamy 'round_history' z game_state przed formatowaniem JSONa
    # Oryginalny kod też to robił: del game_state["round_history"]
    # To jest kluczowe, bo AI ma dostać tylko stan, a nie historię
    history_to_display = game_state.pop("round_history", []) # Używamy pop, żeby mieć historię do wyświetlenia i usunąć ją ze stanu JSON
    
    for player, moves in players_moves.items():
        prompt_lines.append(f"Ruchy gracza {player}:\n")
        for i, move_summary in enumerate(moves, 1):
            prompt_lines.append(f"    {i}. {move_summary}")
    
    prompt_lines.append(f"\nTeraz twój ruch ({AI_PLAYER_NAME}).")
    prompt_lines.append("Przeanalizuj poniższy stan JSON.")
    prompt_lines.append("\n### STAN GRY (Źródło Prawdy) ###")
        
    # Sformatuj JSON
    game_state_json_string = json.dumps(game_state, indent=2, ensure_ascii=False)
    
    # --- Połącz wszystko ---
    final_prompt = "\n".join(prompt_lines)
    final_prompt += f"\n```json\n{game_state_json_string}\n```"

    return final_prompt

