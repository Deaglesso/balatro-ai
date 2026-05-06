# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
# ]
# ///

import json

import numpy as np
import requests

from observations import gamestate_to_observation, pretty_print_gamestate

# BalatroBot API endpoint
URL = "http://127.0.0.1:12346"

def rpc(method: str, params: dict = {}) -> dict:
    """Send a JSON-RPC 2.0 request to the BalatroBot API."""
    response = requests.post(URL, json={
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    })
    data = response.json()
    # Raise if error, otherwise return result (contains game state)
    if "error" in data:
        raise Exception(data["error"]["message"])
    return data["result"]


def play_game(export_observations: bool = False, observations_path: str = "observations.npy"):
    """Play a complete game of Balatro.

    If export_observations is True, saves the observation trajectory to a numpy file.
    Returns a tuple of (won, observations).
    """
    # Return to menu and start a new game
    rpc("menu")
    state = rpc("start", {"deck": "CHECKERED", "stake": "WHITE", "seed": "8i2XLBPX"})
    print(f"Started game with seed: {state['seed']}")
    pretty_print_gamestate(state)

    observations = [gamestate_to_observation(state)]

    # Main game loop
    while state["state"] != "GAME_OVER":
        pretty_print_gamestate(state)
        with open(state["state"]+'.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(state["hand"], indent=2, ensure_ascii=False))
        match state["state"]:
            case "BLIND_SELECT":
                # Always select the current blind
                state = rpc("select")

            case "SELECTING_HAND":
                # Print hand for debugging to a file
                
                # Play the first 5 cards (simple strategy)
                num_cards = min(5, len(state["hand"]["cards"]))
                cards = list(range(num_cards))
                state = rpc("play", {"cards": cards})

            case "ROUND_EVAL":
                # Collect rewards and go to shop
                state = rpc("cash_out")

            case "SHOP":
                # Skip the shop and proceed to next round
                state = rpc("next_round")

            case _:
                # Handle any transitional states
                state = rpc("gamestate")

        observations.append(gamestate_to_observation(state))

    # Game ended
    if state["won"]:
        print(f"Victory! Final ante: {state['ante_num']}")
    else:
        print(f"Game over at ante {state['ante_num']}, round {state['round_num']}")

    if export_observations:
        np.save(observations_path, np.stack(observations))
        print(f"Saved {len(observations)} observations to {observations_path}")

    return state["won"], observations


if __name__ == "__main__":
    play_game(export_observations=True)