# interactive version of planform visualization

import json

from matplotlib import pyplot as plt
from matplotlib.widgets import Slider

from wyvern.layout.planform import (
    PlanformParameters,
    control_surface_points,
    full_planform_points,
    planform_span_stations,
    planform_stats,
)


def planform_viz_interactive(base_config: PlanformParameters):
    """
    Launches interactive visualization of planform parameters.

    UI:
    | Plot | Text Stats |
    |       Sliders     |
    """
    # styling
    plt.style.use("dark_background")
    font = {"family": "sans", "size": 10}
    plt.rc("font", **font)

    # find class attrs by type hint; get only float attrs
    attrs = [
        attr for attr, hint in base_config.__annotations__.items() if hint == float
    ]

    # create tiled layout for ui
    fig, axs = plt.subplot_mosaic([["plot", "stats"]], figsize=(12, 7))
    fig.subplots_adjust(bottom=0.04 * len(attrs) + 0.07)

    axs["plot"].set_title("Planform Visualization")
    axs["plot"].set_xlabel("x (mm)")
    axs["plot"].set_ylabel("y (mm)")
    axs["plot"].set_aspect("equal")
    axs["plot"].invert_yaxis()
    axs["stats"].set_title("Planform Stats")
    axs["stats"].axis("off")  # hide axes

    # Create elements to update when sliders change
    # main viz
    (planform_plot,) = axs["plot"].plot([], [], "-", color="white")
    (ctrl_srf_l,) = axs["plot"].plot([], [], "r-")
    (ctrl_srf_r,) = axs["plot"].plot([], [], "r-")

    # stats
    # text box for stats
    stats_text = axs["stats"].text(
        0,
        0.5,
        "Stats",
        horizontalalignment="left",
        verticalalignment="center",
        transform=axs["stats"].transAxes,
    )

    def _update_plot(_):
        # update all attrs
        for attr, slider in zip(attrs, sliders):
            setattr(base_config, attr, slider.val)

        # sanity check
        if (
            base_config.wing_halfspan + base_config.centerbody_halfspan
            < base_config.ctrl_surface_end_y
        ):
            base_config.ctrl_surface_end_y = (
                base_config.wing_halfspan + base_config.centerbody_halfspan
            )
            sliders[attrs.index("ctrl_surface_end_y")].set_val(
                base_config.ctrl_surface_end_y
            )
        elif (
            base_config.ctrl_surface_end_y
            > base_config.wing_halfspan + base_config.centerbody_halfspan
        ):
            base_config.wing_halfspan = (
                base_config.ctrl_surface_end_y - base_config.centerbody_halfspan
            )
            sliders[attrs.index("wing_halfspan")].set_val(base_config.wing_halfspan)

        # update plot
        df = planform_span_stations(base_config)
        pts = full_planform_points(df)
        ctl_surf_l_pts, ctl_surf_r_pts = control_surface_points(df)
        planform_plot.set_xdata(pts[:, 0])
        planform_plot.set_ydata(pts[:, 1])
        ctrl_srf_l.set_xdata(ctl_surf_l_pts[:, 0])
        ctrl_srf_l.set_ydata(ctl_surf_l_pts[:, 1])
        ctrl_srf_r.set_xdata(ctl_surf_r_pts[:, 0])
        ctrl_srf_r.set_ydata(ctl_surf_r_pts[:, 1])

        # recalculate areas
        stats = planform_stats(base_config)

        stats_text.set_text(
            f"Overall Area: {stats.loc[base_config.name, 'overall_area']/1e6:.4f} m^2\n"
            f"Overall AR: {stats.loc[base_config.name, 'overall_aspect_ratio']:.4f}\n"
            f"Wing Half Area: {stats.loc[base_config.name, 'wing_half_area']/1e6:.4f} m^2\n"
            f"Wing AR: {stats.loc[base_config.name, 'wing_aspect_ratio']:.4f}\n"
            f"Centerbody Half Area: {stats.loc[base_config.name, 'centerbody_half_area']/1e6:.4f} m^2\n"
            f"Centerbody AR: {stats.loc[base_config.name, 'centerbody_aspect_ratio']:.4f}\n"
            f"Overall Centroid (x): {stats.loc[base_config.name, 'overall_centroid']:.4f} mm\n"
            f"Wing Centroid (x): {stats.loc[base_config.name, 'wing_centroid']:.4f} mm\n"
            f"Centerbody Centroid (x): {stats.loc[base_config.name, 'centerbody_centroid']:.4f} mm\n"
            f"Proportion of Wing Area: {2*stats.loc[base_config.name, 'wing_half_area']/stats.loc[base_config.name, 'overall_area']:.4f}\n"
            f"Wing Mean Aerodynamic Chord: {stats.loc[base_config.name, 'wing_mean_aerodynamic_chord']:.4f} mm\n"
        )

        # resize plot to fit
        axs["plot"].relim()
        axs["plot"].autoscale_view()

        fig.canvas.draw_idle()

    # add axes for sliders
    axs.update(
        {
            f"sliders_{attr}": fig.add_axes([0.25, 0.04 * idx + 0.02, 0.55, 0.02])
            for (idx, attr) in enumerate(attrs)
        }
    )

    # we will have one slider per attribute
    sliders = [
        Slider(
            ax=axs[f"sliders_{attr}"],
            label=attr,
            valmin=0,
            valmax=getattr(base_config, attr) * 2
            if getattr(base_config, attr) > 1
            else 1,
            valinit=getattr(base_config, attr),
            valstep=5 if getattr(base_config, attr) > 1 else 0.01,
        )
        for attr in attrs
    ]

    for slider in sliders:
        slider.on_changed(_update_plot)

    _update_plot(None)

    plt.suptitle("Planform Tuner; Close Plot to Save Config")
    plt.show()

    # save final config
    for attr, slider in zip(attrs, sliders):
        setattr(base_config, attr, slider.val)

    return base_config


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
