"""
train.py — PPO training with parallel Balatrobot instances
===========================================================
Trains the high-level strategy-selection agent using PPO
across N parallel Balatrobot instances (each on its own port).

Before running:
  1. Start N Balatrobot instances, one per port:
       uvx balatrobot serve --fast --no-shaders --fps-cap 1000 --gamespeed 4 --port 12346
       uvx balatrobot serve --fast --no-shaders --fps-cap 1000 --gamespeed 4 --port 12347
       uvx balatrobot serve --fast --no-shaders --fps-cap 1000 --gamespeed 4 --port 12348
       uvx balatrobot serve --fast --no-shaders --fps-cap 1000 --gamespeed 4 --port 12349

  2. Create save files for each port (run this once):
       python train.py --setup-only

  3. Start training:
       python train.py

Requirements:
  pip install stable-baselines3 gymnasium requests numpy
"""

import os
import argparse
import requests
import time
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor
from stable_baselines3.common.callbacks import (
    EvalCallback,
    CheckpointCallback,
    BaseCallback,
)
from stable_baselines3.common.utils import set_random_seed

from env import BalatroEnv, DECK, STAKE


# ─────────────────────────────────────────────────────────────
# CONFIG — edit these to match your setup
# ─────────────────────────────────────────────────────────────

PORTS = [12346, 12347, 12348, 12349]   # one Balatrobot per port

# Fixed seeds for reproducible training (one save file per port)
SEEDS = ["TRAIN01", "TRAIN02", "TRAIN03", "TRAIN04"]

SAVE_DIR      = "C:/tmp/balatro_saves"
MODEL_DIR     = "./models"
LOG_DIR       = "./logs"
TOTAL_STEPS   = 100_000   # increase for longer training
N_STEPS       = 256       # PPO rollout length per env
BATCH_SIZE    = 64
N_EPOCHS      = 10
LEARNING_RATE = 3e-4
GAMMA         = 0.99      # discount factor
EVAL_FREQ     = 2_000     # evaluate every N steps
CHECKPOINT_FREQ = 10_000  # save checkpoint every N steps


# ─────────────────────────────────────────────────────────────
# SAVE FILE SETUP
# ─────────────────────────────────────────────────────────────

def create_save_files():
    """
    Connect to each Balatrobot instance and create a fresh
    save file using the fixed seed for that port.
    Must be run once before training.
    """
    os.makedirs(SAVE_DIR, exist_ok=True)

    for port, seed in zip(PORTS, SEEDS):
        save_path = os.path.join(SAVE_DIR, f"fresh_{port}.jkr")
        url       = f"http://127.0.0.1:{port}"

        print(f"[port {port}] Creating save file with seed {seed}...")

        try:
            # Health check
            r = requests.post(url, json={
                "jsonrpc": "2.0", "method": "health", "params": {}, "id": 1
            }, timeout=5)
            if r.json()["result"]["status"] != "ok":
                print(f"  ❌ Port {port} not responding. Is Balatrobot running?")
                continue

            # Go to menu if not already there
            state_r = requests.post(url, json={
                "jsonrpc": "2.0", "method": "gamestate", "params": {}, "id": 1
            }, timeout=10)
            state = state_r.json()["result"]["state"]
            if state != "MENU":
                requests.post(url, json={
                    "jsonrpc": "2.0", "method": "menu", "params": {}, "id": 1
                }, timeout=10)

            # Start a fresh run
            requests.post(url, json={
                "jsonrpc": "2.0", "method": "start",
                "params": {"deck": DECK, "stake": STAKE, "seed": seed},
                "id": 1
            }, timeout=15)

            # Save it
            requests.post(url, json={
                "jsonrpc": "2.0", "method": "save",
                "params": {"path": save_path},
                "id": 1
            }, timeout=10)

            print(f"  ✅ Saved to {save_path}")

        except Exception as e:
            print(f"  ❌ Failed for port {port}: {e}")


# ─────────────────────────────────────────────────────────────
# ENV FACTORY
# ─────────────────────────────────────────────────────────────

def make_env(port: int, seed: str, rank: int):
    """Factory function for SubprocVecEnv."""
    save_path = os.path.join(SAVE_DIR, f"fresh_{port}.jkr")

    def _init():
        env = BalatroEnv(port=port, save_path=save_path, seed=seed)
        env.reset(seed=rank)   # different numpy seed per env
        return env

    set_random_seed(rank)
    return _init


# ─────────────────────────────────────────────────────────────
# CUSTOM CALLBACK: log strategy distribution
# ─────────────────────────────────────────────────────────────

class StrategyLogCallback(BaseCallback):
    """
    Logs how often each strategy is chosen during training.
    Useful for verifying the agent is actually exploring.
    """
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.strategy_counts = [0, 0, 0]

    def _on_step(self) -> bool:
        actions = self.locals.get("actions", [])
        for a in actions:
            if 0 <= a < 3:
                self.strategy_counts[a] += 1

        # Log every 1000 steps
        total = sum(self.strategy_counts)
        if total > 0 and total % 1000 < len(actions):
            self.logger.record("strategy/flush_pct",
                               100 * self.strategy_counts[0] / total)
            self.logger.record("strategy/pair_pct",
                               100 * self.strategy_counts[1] / total)
            self.logger.record("strategy/mult_pct",
                               100 * self.strategy_counts[2] / total)

        return True


# ─────────────────────────────────────────────────────────────
# MAIN TRAINING LOOP
# ─────────────────────────────────────────────────────────────

def train():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR,   exist_ok=True)

    print(f"Starting training with {len(PORTS)} parallel instances")
    print(f"Ports: {PORTS}")
    print(f"Total steps: {TOTAL_STEPS:,}")
    print()

    # Verify save files exist
    for port in PORTS:
        save_path = os.path.join(SAVE_DIR, f"fresh_{port}.jkr")
        if not os.path.exists(save_path):
            print(f"❌ Save file missing for port {port}: {save_path}")
            print("   Run: python train.py --setup-only")
            return

    # Build parallel environments
    print("Building parallel environments...")
    env_fns = [
        make_env(port, seed, rank)
        for rank, (port, seed) in enumerate(zip(PORTS, SEEDS))
    ]
    vec_env = SubprocVecEnv(env_fns)
    vec_env = VecMonitor(vec_env, LOG_DIR)
    print(f"✅ {len(PORTS)} environments ready\n")

    # Build eval env (single instance on first port)
    eval_env = SubprocVecEnv([make_env(PORTS[0], SEEDS[0], 99)])
    eval_env = VecMonitor(eval_env)

    # PPO model
    # Small network — the high-level decision is simple (3 actions)
    # Input: ~35 dimensional obs, output: Discrete(3)
    model = PPO(
        policy          = "MlpPolicy",
        env             = vec_env,
        n_steps         = N_STEPS,
        batch_size      = BATCH_SIZE,
        n_epochs        = N_EPOCHS,
        learning_rate   = LEARNING_RATE,
        gamma           = GAMMA,
        gae_lambda      = 0.95,
        clip_range      = 0.2,
        ent_coef        = 0.01,   # entropy bonus encourages exploration
        verbose         = 1,
        tensorboard_log = LOG_DIR,
        policy_kwargs   = dict(
            net_arch = [64, 64],   # small MLP — 2 hidden layers of 64
        ),
    )

    # Callbacks
    callbacks = [
        CheckpointCallback(
            save_freq   = CHECKPOINT_FREQ // len(PORTS),
            save_path   = MODEL_DIR,
            name_prefix = "balatro_ppo",
        ),
        EvalCallback(
            eval_env,
            eval_freq        = EVAL_FREQ // len(PORTS),
            best_model_save_path = os.path.join(MODEL_DIR, "best"),
            log_path         = LOG_DIR,
            deterministic    = True,
            render           = False,
        ),
        StrategyLogCallback(),
    ]

    # Train
    print("Starting PPO training...")
    print("Monitor with: tensorboard --logdir ./logs\n")
    t_start = time.time()

    model.learn(
        total_timesteps = TOTAL_STEPS,
        callback        = callbacks,
        progress_bar    = True,
    )

    elapsed = time.time() - t_start
    print(f"\nTraining complete in {elapsed/60:.1f} minutes")

    # Save final model
    final_path = os.path.join(MODEL_DIR, "balatro_ppo_final")
    model.save(final_path)
    print(f"Final model saved to {final_path}")

    vec_env.close()
    eval_env.close()


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only create save files, don't train",
    )
    args = parser.parse_args()

    if args.setup_only:
        create_save_files()
    else:
        # Auto-create save files if missing
        missing = [
            p for p in PORTS
            if not os.path.exists(os.path.join(SAVE_DIR, f"fresh_{p}.jkr"))
        ]
        if missing:
            print("Save files missing, creating them first...")
            create_save_files()
            print()
        train()
