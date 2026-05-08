# BalatroRL Simplifier

Steamodded mod for Strategy-Conditioned RL research (Group 7).

## What it does

| Feature | Behaviour |
|---|---|
| Blind selection | Auto-selected — agent never sees BLIND_SELECT state |
| Joker whitelist | Only 20 whitelisted jokers appear in shop |
| Planets / Tarots / Spectrals | Removed from shop entirely |
| Booster packs | Removed from shop entirely |
| Vouchers | Removed from shop entirely |

## Installation

1. Copy the entire `BalatroRL/` folder into your Balatro `Mods/` directory.
   - Windows: `%AppData%/Balatro/Mods/`
2. Make sure Steamodded 1.0.0-beta-1224a is installed.
3. Launch Balatro. You should see the `BalatroRL` badge in the mods menu.

## Editing the joker whitelist

Open `main.lua` and find the `JOKER_WHITELIST` table at the top.
Add or remove jokers by name (must match the exact in-game name).

## Debug logs

Enable debug mode in Balatrobot to see the mod's log messages:
```
uvx balatrobot serve --fast --no-shaders --fps-cap 1000 --gamespeed 4 --debug
```
Look for lines prefixed with `[BalatroRL]`.
