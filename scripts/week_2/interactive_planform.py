import json

from wyvern.analysis.parameters import PlanformParameters
from wyvern.layout.viz import planform_viz_interactive

if __name__ == "__main__":
    NF_844_A = PlanformParameters(
        name="NF-844-A",
        centerbody_halfspan=200,
        centerbody_chord=780,
        midbody_y=170,
        midbody_xle=120,
        midbody_chord=600,
        wing_root_le=360,
        wing_root_chord=360,
        wing_halfspan=700,
        wing_taper_ratio=0.33333,
        wing_root_le_sweep_angle=40,
        ctrl_surface_start_y=600,
        ctrl_surface_end_y=800,
        ctrl_surface_x_over_c=0.3,
    )
    updated_config = planform_viz_interactive(NF_844_A)

    # save config
    with open("revised_config.json", "w") as f:
        json.dump(updated_config.to_dict, f, indent=4)

    print("Saved revised config to revised_config.json")
