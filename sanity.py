from observations import gamestate_to_observation, OBS_SIZE, pretty_print_observation
import numpy as np

# Test with empty state
obs = gamestate_to_observation({})
print(f"OBS_SIZE = {OBS_SIZE}")
print(f"obs.shape = {obs.shape}")
pretty_print_observation(obs)