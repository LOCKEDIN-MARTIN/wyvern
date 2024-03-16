import numpy as np
from matplotlib import pyplot as plt

from wyvern.analysis.parameters import PayloadSizingParameters
from wyvern.analysis.payload_sweep import sensitivity_plot, sweep_payload_configs
from wyvern.data import ALL_COMPONENTS
from wyvern.performance.models import QuadraticLDModel
from wyvern.sizing import total_component_mass

ld_model_qd = QuadraticLDModel(
    c_d0=0.02959, e_inviscid=0.9131, K=0.45, aspect_ratio=5.106458
)

# calculate aerostructural mass ratio and fixed component masses first
total_fixed_mass = total_component_mass(ALL_COMPONENTS)
cad_mass = 737  # g

params = PayloadSizingParameters(
    as_mass_ratio=0,
    total_fixed_mass=total_fixed_mass + cad_mass,
    aero_model=ld_model_qd,
    cruise_speed=10,
    turn_speed=10,
    planform_area=0.56595,
    propulsive_efficiency=0.521,
    configuration_bonus=1.3,
    short_takeoff=True,
    stability_distance=0,
)


payload_configs = [(8, i, 4) for i in range(0, 7)]

cad_masses = [600, 700, 740, 800, 900]

# plt.style.use("dark_background")
sensitivity_plot(
    payload_configs,
    params,
    "total_fixed_mass",
    [total_fixed_mass + i for i in cad_masses],
    "Sensitivity to Build Efficiency",
    labels=[f"{i} g structure, {i+total_fixed_mass:.0f} g OEW" for i in cad_masses],
)
plt.savefig("empty_weight_sensitivity.pdf", bbox_inches="tight")

# assess sensitivity to CD0
ld_models = [
    QuadraticLDModel(c_d0=c, e_inviscid=0.9131, K=0.45, aspect_ratio=5.106458)
    for c in [0.025, 0.03, 0.035, 0.04]
]
sensitivity_plot(
    payload_configs,
    params,
    "aero_model",
    ld_models,
    "Sensitivity to $C_{D0}$",
    labels=[f"$C_{{D0}} = {m.c_d0}$" for m in ld_models],
)
plt.savefig("cd0_sensitivity.pdf", bbox_inches="tight")


# single-payload config sensitivity


def sweep_param(
    var: str, params_list: list[PayloadSizingParameters], n_golf: int
) -> list[float]:

    return [
        sweep_payload_configs([(8, n_golf, 4)], param)[var] for param in params_list
    ]


# sensitivity to build efficiency
params_list = [
    PayloadSizingParameters(
        as_mass_ratio=0,
        total_fixed_mass=total_fixed_mass + cad_mass,
        aero_model=ld_model_qd,
        cruise_speed=10,
        turn_speed=10,
        planform_area=0.56595,
        propulsive_efficiency=0.521,
        configuration_bonus=1.3,
        short_takeoff=True,
        stability_distance=0,
    )
    for cad_mass in np.linspace(550, 950)
]

plt.figure(figsize=(5, 4))

for n_golf in [1, 2, 3, 4]:
    plt.plot(
        np.linspace(550, 950),
        sweep_param("total_flight_score", params_list, n_golf),
        label=f"{n_golf}",
    )
plt.xlabel("Structure Mass (g)")
plt.ylabel("Flight Score")
plt.title("Sensitivity to Build Efficiency", fontsize=10)
plt.grid(linewidth=0.5, alpha=0.5)
plt.legend(title="\# Golf Balls")
plt.axvline(x=cad_mass, color="k", linestyle="--", label="_")
plt.text(x=cad_mass - 10, y=25, s="Design Target", ha="right", va="bottom", rotation=90)
plt.savefig("single_payload_empty_weight_sensitivity.pdf", bbox_inches="tight")

# sensitivity to CD0

params_list = [
    PayloadSizingParameters(
        as_mass_ratio=0,
        total_fixed_mass=total_fixed_mass + cad_mass,
        aero_model=QuadraticLDModel(
            c_d0=c, e_inviscid=0.9131, K=0.45, aspect_ratio=5.106458
        ),
        cruise_speed=10,
        turn_speed=10,
        planform_area=0.56595,
        propulsive_efficiency=0.521,
        configuration_bonus=1.3,
        short_takeoff=True,
        stability_distance=0,
    )
    for c in np.linspace(0.02, 0.05)
]


plt.figure(figsize=(5, 4))

for n_golf in [1, 2, 3, 4]:
    plt.plot(
        np.linspace(0.02, 0.05),
        sweep_param("total_flight_score", params_list, n_golf),
        label=f"{n_golf}",
    )
plt.xlabel("$C_{D0}$")
plt.ylabel("Flight Score")
plt.title("Sensitivity to $C_{D0}$", fontsize=10)
plt.grid(linewidth=0.5, alpha=0.5)
plt.legend(title="\# Golf Balls")
plt.axvline(x=ld_model_qd.c_d0, color="k", linestyle="--", label="_")
plt.text(
    x=ld_model_qd.c_d0 - 0.001,
    y=55,
    s="Design Target",
    ha="right",
    va="bottom",
    rotation=90,
)
plt.savefig("single_payload_cd0_sensitivity.pdf", bbox_inches="tight")
