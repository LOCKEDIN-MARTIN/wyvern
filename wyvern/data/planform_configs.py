import json
from pathlib import Path

from wyvern.analysis.parameters import PlanformParameters

with open(Path(__file__).parent / "sources/planform_configurations.json", "r") as f:
    raw_configs = json.load(f)
    planforms = [PlanformParameters.from_dict(config) for config in raw_configs]

PLANFORM_CONFIGS = {p.name: p for p in planforms}
