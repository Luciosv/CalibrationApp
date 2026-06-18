# test_models.py

from models.simulation_config import (
    SimulationConfig
)

config = SimulationConfig()

print(
    "Profundidad:",
    config.total_depth
)

for tissue in config.active_tissues:

    print(
        tissue.name,
        tissue.start_depth,
        tissue.end_depth
    )