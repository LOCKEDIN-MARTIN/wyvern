from matplotlib import pyplot as plt
from matplotlib import rcParams

from wyvern.analysis.parameters import PayloadSizingParameters
from wyvern.analysis.payload_sweep import sweep_payload_configs
from wyvern.data import ALL_COMPONENTS, RASSAM_CORRELATIONS
from wyvern.performance.models import QuadraticLDModel
from wyvern.sizing import aerostructural_mass_ratio, total_component_mass

rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"

ld_model = QuadraticLDModel(
    c_d0=0.02959, e_inviscid=0.9131, K=0.45, aspect_ratio=5.106458
)

# calculate aerostructural mass ratio and fixed component masses first
total_fixed_mass = total_component_mass(ALL_COMPONENTS)
as_mass = 737  # g

params = PayloadSizingParameters(
    as_mass_ratio=0,
    total_fixed_mass=total_fixed_mass + as_mass,
    aero_model=ld_model,
    cruise_speed=10,
    turn_speed=10,
    planform_area=0.56595,
    propulsive_efficiency=0.521,
    configuration_bonus=1.3,
    short_takeoff=True,
    stability_distance=0,
)

payload_configs = [(0, 0, 0)] + [(8, i, 4) for i in range(0, 7)]
results = sweep_payload_configs(payload_configs, params)

results.to_csv("payload_sensitivity_study.csv", index=False)

# get legacy data from PDR
params_pdr = PayloadSizingParameters(
    as_mass_ratio=aerostructural_mass_ratio(RASSAM_CORRELATIONS, total_fixed_mass),
    total_fixed_mass=total_fixed_mass,
    aero_model=QuadraticLDModel(
        c_d0=0.032, e_inviscid=0.95, K=0.45, aspect_ratio=5.106458
    ),
    cruise_speed=10,
    turn_speed=10,
    planform_area=0.56595,
    propulsive_efficiency=0.521,
    configuration_bonus=1.3,
    short_takeoff=True,
    stability_distance=0,
)
results_pdr = sweep_payload_configs(payload_configs, params_pdr)


fig, ax = plt.subplots(figsize=(5, 4))
ax.plot(
    results["num_golf_balls"][1:],
    results["total_flight_score"][1:],
    marker="o",
    label="FDR",
    color="k",
)
ax.plot(
    results_pdr["num_golf_balls"][1:],
    results_pdr["total_flight_score"][1:],
    marker="o",
    label="PDR",
    color="r",
    linestyle="--",
)
ax.set_xlabel("Number of Golf Balls")
ax.set_ylabel("Flight Score")
ax.grid(linewidth=0.5, alpha=0.5)
ax.title.set_text("Flight Score vs. Payload")
ax.title.set_fontsize(10)
ax.legend(frameon=False)

# save the figure
# fig.savefig("flight_score_vs_payload.png", dpi=500, bbox_inches="tight", transparent=True)
fig.savefig("flight_score_vs_payload.pdf", bbox_inches="tight")
