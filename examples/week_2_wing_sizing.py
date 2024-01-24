from wyvern.analysis.parameters import WingSizingParameters
from wyvern.data.planform_configs import PLANFORM_CONFIGS
from wyvern.performance.aerodynamics import flight_estimates
from wyvern.sizing.wing_sizing import wing_loading_estimate

params = WingSizingParameters(
    takeoff_power=180,
    takeoff_thrust=9.25,
    aspect_ratio=4.8,
    sweep_angle=30,
    airfoil_cl_max=0.9,
    s_wet_s_ref=2.1,
    c_fe=0.02,
    cruise_speed=12,
    turn_speed=11,
    stall_speed=8,
    oswald_efficiency=0.9,
    takeoff_headwind=3,
    takeoff_distance=7.5,
    ground_cl=0.1,
    rolling_resistance_coefficient=0.1,
)

takeoff_mass = 1627  # g

df = wing_loading_estimate(params, takeoff_mass)
print(df)

w_s_design = min(df["W/S"])
print(f"Design wing loading: {w_s_design:.3f} kg/m^2")
print(f"Design wing area: {takeoff_mass / 1000 / w_s_design:.3f} m^2")


results = flight_estimates(params, PLANFORM_CONFIGS["NF-844-B-REV1"], takeoff_mass)
print(results)

print(results.to_latex(float_format="%.3f"))
