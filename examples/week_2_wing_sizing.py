from wyvern.analysis.parameters import WingSizingParameters
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

df = wing_loading_estimate(params, 1627)
print(df)
