from wyvern.analysis.parameters import PayloadSizingParameters
from wyvern.analysis.payload_sweep import sensitivity_plot
from wyvern.data import ALL_COMPONENTS, RASSAM_CORRELATIONS
from wyvern.sizing import aerostructural_mass_ratio, total_component_mass

# calculate aerostructural mass ratio and fixed component masses first
total_fixed_mass = total_component_mass(ALL_COMPONENTS)
as_m_ratio = aerostructural_mass_ratio(RASSAM_CORRELATIONS, total_fixed_mass)

params = PayloadSizingParameters(
    as_mass_ratio=as_m_ratio,
    total_fixed_mass=total_fixed_mass,
    lift_to_drag_ratio=10,
    cruise_speed=11,
    turn_speed=10,
    propulsive_efficiency=0.5,
    configuration_bonus=1.3,
    short_takeoff=False,
    stability_distance=0,
)

# assess sensitivity to as_m_ratio
as_m_ratios = [0.40, 0.45, 0.50, 0.55]

payload_configs = [(8, i, 4) for i in range(0, 7)]

sensitivity_plot(payload_configs, params, "as_mass_ratio", as_m_ratios)

# assess sensitivity to lift-to-drag ratio
lift_to_drag_ratios = [6, 8, 10, 12]
sensitivity_plot(payload_configs, params, "lift_to_drag_ratio", lift_to_drag_ratios)

# assess sensitivity to turn speed
turn_speeds = [10, 12, 14, 16]
sensitivity_plot(payload_configs, params, "turn_speed", turn_speeds)
