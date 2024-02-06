from matplotlib import pyplot as plt

from wyvern.analysis.parameters import PayloadSizingParameters
from wyvern.analysis.payload_sweep import sensitivity_plot
from wyvern.data import ALL_COMPONENTS, RASSAM_CORRELATIONS
from wyvern.performance.models import CNSTLDModel, QuadraticLDModel
from wyvern.sizing import aerostructural_mass_ratio, total_component_mass

ld_model_cnst = CNSTLDModel(ld=9.39)
ld_model_qd = QuadraticLDModel(c_d0=0.0318, e_inviscid=0.95, K=0.45, aspect_ratio=5.1)

# calculate aerostructural mass ratio and fixed component masses first
total_fixed_mass = total_component_mass(ALL_COMPONENTS)
as_m_ratio = aerostructural_mass_ratio(RASSAM_CORRELATIONS, total_fixed_mass)

params = PayloadSizingParameters(
    as_mass_ratio=as_m_ratio,
    total_fixed_mass=total_fixed_mass,
    aero_model=ld_model_cnst,
    cruise_speed=10,
    turn_speed=10,
    planform_area=0.566,
    propulsive_efficiency=0.5,
    configuration_bonus=1.3,
    short_takeoff=False,
    stability_distance=0,
)

# assess sensitivity to as_m_ratio
as_m_ratios = [0.40, 0.45, 0.50, 0.55]

payload_configs = [(8, i, 4) for i in range(0, 7)]

plt.style.use("dark_background")
sensitivity_plot(
    payload_configs,
    params,
    "as_mass_ratio",
    as_m_ratios,
    "Sensitivity to Structural Mass Fraction (at CNST L/D)",
)

# assess sensitivity to lift-to-drag ratio
ld_models = [CNSTLDModel(ld=i) for i in range(8, 12)]
sensitivity_plot(
    payload_configs,
    params,
    "aero_model",
    ld_models,
    "Sensitivity to L/D",
)

# swap in the quadratic model
params.aero_model = ld_model_qd
sensitivity_plot(
    payload_configs,
    params,
    "as_mass_ratio",
    as_m_ratios,
    "Sensitivity to Structural Mass Fraction (w/Drag Polar)",
)

# assess sensitivity to turn speed
turn_speeds = [9, 10, 11]
sensitivity_plot(
    payload_configs, params, "turn_speed", turn_speeds, "Sensitivity to Turn Speed"
)

# assess sensitivity to flight speed
cruise_speeds = [9, 10, 11, 12]
sensitivity_plot(
    payload_configs,
    params,
    "cruise_speed",
    cruise_speeds,
    "Sensitivity to Cruise Speed",
)
