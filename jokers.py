"""
jokers.py — Single source of truth for the joker whitelist
============================================================
Add jokers here ONLY. Both observations.py and strategy.py
import from this file so you never have to update two places.

To add a joker:
  1. Add an entry to JOKER_REGISTRY below
  2. Update the mod's ALLOWED_JOKER_LIST in rlSimplify.lua
     with the corresponding internal key (mod_key field)
  3. That's it — obs vector size updates automatically

To add a strategy:
  1. Add a value to the Strategy enum in strategy.py
  2. Add a preference dict for it in STRATEGY_PREFERRED_HANDS
  3. Tag relevant jokers with the new strategy in JOKER_REGISTRY
"""

# ─────────────────────────────────────────────────────────────
# JOKER REGISTRY
# Each entry:
#   display_name : exact in-game name (used in obs encoding)
#   mod_key      : internal Balatro key (used in rlSimplify.lua)
#   strategy_hint: which strategy this joker supports
#   note         : what it does (for reference)
# ─────────────────────────────────────────────────────────────

JOKER_REGISTRY = [
    # ── FLUSH strategy ──────────────────────────────────────
    {
        "display_name": "Droll Joker",
        "mod_key":      "j_droll_joker",
        "strategy":     "FLUSH_BUILD",
        "note":         "+10 Mult if played hand contains a Flush",
    },
    {
        "display_name": "Crafty Joker",
        "mod_key":      "j_crafty_joker",
        "strategy":     "FLUSH_BUILD",
        "note":         "+80 Chips if played hand contains a Flush",
    },
    {
        "display_name": "Lusty Joker",
        "mod_key":      "j_lusty_joker",
        "strategy":     "FLUSH_BUILD",
        "note":         "+3 Mult for each Heart card played",
    },
    {
        "display_name": "Greedy Joker",
        "mod_key":      "j_greedy_joker",
        "strategy":     "FLUSH_BUILD",
        "note":         "+3 Mult for each Diamond card played",
    },

    # ── PAIR strategy ────────────────────────────────────────
    {
        "display_name": "Jolly Joker",
        "mod_key":      "j_jolly",
        "strategy":     "PAIR_BUILD",
        "note":         "+8 Mult if played hand contains a Pair",
    },
    {
        "display_name": "Zany Joker",
        "mod_key":      "j_zany_joker",
        "strategy":     "PAIR_BUILD",
        "note":         "+12 Mult if played hand contains Three of a Kind",
    },
    {
        "display_name": "Mad Joker",
        "mod_key":      "j_mad_joker",
        "strategy":     "PAIR_BUILD",
        "note":         "+10 Mult if played hand contains Two Pair",
    },
    {
        "display_name": "Sly Joker",
        "mod_key":      "j_sly_joker",
        "strategy":     "PAIR_BUILD",
        "note":         "+50 Chips if played hand contains a Pair",
    },
    {
        "display_name": "Wily Joker",
        "mod_key":      "j_wily_joker",
        "strategy":     "PAIR_BUILD",
        "note":         "+100 Chips if played hand contains Three of a Kind",
    },

    # ── MULT strategy ────────────────────────────────────────
    {
        "display_name": "Joker",
        "mod_key":      "j_joker",
        "strategy":     "MULT_BUILD",
        "note":         "+4 Mult flat, always active",
    },
    {
        "display_name": "Abstract Joker",
        "mod_key":      "j_abstract_joker",
        "strategy":     "MULT_BUILD",
        "note":         "+3 Mult for each joker you own",
    },
    {
        "display_name": "Half Joker",
        "mod_key":      "j_half_joker",
        "strategy":     "MULT_BUILD",
        "note":         "+20 Mult if played hand has 3 or fewer cards",
    },
    {
        "display_name": "Scary Face",
        "mod_key":      "j_scary_face",
        "strategy":     "MULT_BUILD",
        "note":         "+30 Chips for each face card played",
    },
]

# ─────────────────────────────────────────────────────────────
# DERIVED LOOKUPS — don't edit these
# ─────────────────────────────────────────────────────────────

# display_name → index (used in observations.py)
JOKER_DISPLAY_NAMES = [j["display_name"] for j in JOKER_REGISTRY]
JOKER_INDEX         = {name: i for i, name in enumerate(JOKER_DISPLAY_NAMES)}
NUM_JOKERS          = len(JOKER_REGISTRY)

# mod_key → index (useful for debugging)
JOKER_KEY_INDEX = {j["mod_key"]: i for i, j in enumerate(JOKER_REGISTRY)}

# strategy → list of joker display names
JOKERS_BY_STRATEGY = {}
for j in JOKER_REGISTRY:
    s = j["strategy"]
    JOKERS_BY_STRATEGY.setdefault(s, [])
    JOKERS_BY_STRATEGY[s].append(j["display_name"])

# Lua list string — paste this directly into rlSimplify.lua
LUA_WHITELIST = (
    "local ALLOWED_JOKER_LIST = {\n"
    + "".join(f'    "{j["mod_key"]}",  -- {j["note"]}\n' for j in JOKER_REGISTRY)
    + "}"
)


if __name__ == "__main__":
    print(f"Total jokers: {NUM_JOKERS}\n")
    for strategy, names in JOKERS_BY_STRATEGY.items():
        print(f"{strategy}:")
        for name in names:
            print(f"  - {name}")
    print()
    print("Paste into rlSimplify.lua:")
    print(LUA_WHITELIST)
