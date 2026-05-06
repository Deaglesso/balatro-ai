import numpy as np

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
SUITS = ["C", "D", "H", "S"]

SUIT_SYMBOLS = {
    "C": "♣",
    "D": "♦",
    "H": "♥",
    "S": "♠",
}

RANK_LABELS = {
    "A": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "T": "10",
    "J": "J",
    "Q": "Q",
    "K": "K",
}


def card_to_string(card: dict) -> str:
    """Convert a raw card dict into a human-readable string."""
    value = card.get("value", {}) or {}
    rank = value.get("rank", "?")
    suit = value.get("suit", "?")
    state = card.get("state", {}) or {}
    hidden = isinstance(state, dict) and bool(state.get("hidden", False))
    if hidden:
        return "??"
    rank_label = RANK_LABELS.get(rank, rank)
    suit_symbol = SUIT_SYMBOLS.get(suit, suit)
    return f"{rank_label}{suit_symbol}"


def pretty_print_gamestate(raw_state: dict) -> None:
    """Print a compact Balatro gamestate summary."""
    hand = raw_state.get("hand", {}) or {}
    cards = hand.get("cards", []) or []
    hand_cards = ", ".join(card_to_string(card) for card in cards)
    hand_cards = f"[{hand_cards}]"

    round_info = raw_state.get("round", {}) or {}
    
    # Get current blind score
    blinds = raw_state.get("blinds", {}) or {}
    current_blind_score = 0
    for blind_type in ["small", "big", "boss"]:
        blind = blinds.get(blind_type, {}) or {}
        if blind.get("status") == "CURRENT":
            current_blind_score = blind.get("score", 0)
            break

    print(hand_cards)
    print(
        f"Hands: {round_info.get('hands_left', 0)}, "
        f"Discards: {round_info.get('discards_left', 0)}"
    )
    print(
        f"Round Score: {int(round_info.get('chips', 0))} / {int(current_blind_score)}"
    )
    print(
        f"Round: {raw_state.get('round_num', 0)}, "
        f"Ante: {raw_state.get('ante_num', 0)}, "
        f"Money: {raw_state.get('money', 0)}"
    )


def gamestate_to_observation(raw_state: dict) -> np.ndarray:
    """Convert raw Balatro gamestate into a minimal flat numpy observation vector.

    Observation layout (23 values total):
    0: ante_num
    1: round_num
    2: money
    3: current_blind_score
    4: hand_count
    5: hands_left
    6: discards_left
    
    7-22: 8 card slots, 2 values each (rank_idx, suit_idx):
      - rank_idx: 0-12 (or -1 for hidden)
      - suit_idx: 0-3 (or -1 for hidden)
    """
    obs = np.zeros(23, dtype=np.float32)

    obs[0] = float(raw_state.get("ante_num", 0))
    obs[1] = float(raw_state.get("round_num", 0))
    obs[2] = float(raw_state.get("money", 0))

    # Get current blind score
    blinds = raw_state.get("blinds", {}) or {}
    current_blind_score = 0
    for blind_type in ["small", "big", "boss"]:
        blind = blinds.get(blind_type, {}) or {}
        if blind.get("status") == "CURRENT":
            current_blind_score = blind.get("score", 0)
            break
    obs[3] = float(current_blind_score)

    hand = raw_state.get("hand", {}) or {}
    cards = hand.get("cards", []) or []
    obs[4] = float(len(cards))

    round_info = raw_state.get("round", {}) or {}
    obs[5] = float(round_info.get("hands_left", 0))
    obs[6] = float(round_info.get("discards_left", 0))

    # Encode cards: 8 slots, 2 values per card (rank_idx, suit_idx)
    for i in range(8):
        if i < len(cards):
            card = cards[i]
            value = card.get("value", {}) or {}
            rank = value.get("rank", "")
            suit = value.get("suit", "")

            rank_idx = RANKS.index(rank) if rank in RANKS else -1
            suit_idx = SUITS.index(suit) if suit in SUITS else -1

            obs[7 + i * 2] = float(rank_idx)
            obs[7 + i * 2 + 1] = float(suit_idx)
        else:
            # Empty slot
            obs[7 + i * 2] = -1.0
            obs[7 + i * 2 + 1] = -1.0

    return obs
