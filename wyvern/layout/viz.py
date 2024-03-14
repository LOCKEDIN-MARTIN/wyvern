from matplotlib import pyplot as plt
from matplotlib import rcParams
from matplotlib.widgets import Slider

from wyvern.layout.planform import (
    PlanformParameters,
    centerbody_points,
    control_surface_points,
    full_planform_points,
    planform_span_stations,
    planform_stats,
    wing_points,
)


def planform_viz(configuration: PlanformParameters):
    """
    Visualize the planform.

    saving or showing the plot is up to the user.
    """
    df = planform_span_stations(configuration)
    pts = full_planform_points(df)
    ctl_surface_pts, ctl_surface_pts_mirror = control_surface_points(df)

    stats = planform_stats(configuration)
    centroid = stats.loc[configuration.name, "overall_centroid"]
    cb_centroid = stats.loc[configuration.name, "centerbody_centroid"]
    wing_centroid = stats.loc[configuration.name, "wing_centroid"]
    area = stats.loc[configuration.name, "overall_area"]
    cb_area = stats.loc[configuration.name, "centerbody_half_area"]
    wing_area = stats.loc[configuration.name, "wing_half_area"]

    # plotting
    plt.plot(pts[:, 0], pts[:, 1])
    plt.plot(
        ctl_surface_pts[:, 0],
        ctl_surface_pts[:, 1],
        label="hinge line",
        color="C1",
    )
    plt.plot(
        ctl_surface_pts_mirror[:, 0],
        ctl_surface_pts_mirror[:, 1],
        # no legend for this one
        color="C1",
    )
    plt.axhline(centroid, color="k", linestyle="--", label=f"X_c = {centroid:.2f} mm")
    plt.axhline(
        cb_centroid,
        color="C3",
        linestyle="--",
        label=f"X_c, CB = {cb_centroid:.2f} mm",
    )
    plt.axhline(
        wing_centroid,
        color="C2",
        linestyle="--",
        label=f"X_c, W = {wing_centroid:.2f} mm",
    )

    # styling
    plt.gca().invert_yaxis()
    plt.axis("equal")
    plt.grid(linewidth=0.5, alpha=0.5)
    plt.title(
        f"{configuration.name}\nArea: {2*wing_area:.3f} (W) + {2*cb_area:.3f} (CB) = {area:.3f} $m^2$"
    )
    plt.xlabel("Y (mm)")
    plt.ylabel("X (mm)")
    plt.legend()


def planform_viz_simple(configuration: PlanformParameters):
    """
    Simple planform visualization for cleaner output.

    Latex-ified

    saving or showing the plot is up to the user.
    """
    rcParams["text.usetex"] = True
    # use computer modern serif font for all text
    rcParams["font.family"] = "serif"

    df = planform_span_stations(configuration)
    pts = full_planform_points(df)

    wing_pts = wing_points(df)
    cb_pts = centerbody_points(df)

    # plotting
    plt.plot(
        pts[:, 0],
        pts[:, 1],
    )

    # shade in wing and centerbody
    (a1,) = plt.fill(wing_pts[:, 0], wing_pts[:, 1], color="C2", alpha=0.5)
    (a2,) = plt.fill(cb_pts[:, 0], cb_pts[:, 1], color="C3", alpha=0.5)

    plt.legend([a1, a2], ["Wing", "Centerbody"])

    # styling
    plt.gca().invert_yaxis()
    plt.axis("equal")
    plt.title(f"{configuration.name}")
    plt.xlabel("$y$ (mm)")
    plt.ylabel("$x$ (mm)")


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
            f"Overall Area: {stats.loc[base_config.name, 'overall_area']:.4f} m^2\n"
            f"Overall AR: {stats.loc[base_config.name, 'overall_aspect_ratio']:.4f}\n"
            f"Overall (Full) Span: {stats.loc[base_config.name, 'overall_span']:.4f} mm\n"
            f"Overall MAC: {stats.loc[base_config.name, 'overall_mean_aerodynamic_chord']:.4f} mm\n"
            f"Wing Half Area: {stats.loc[base_config.name, 'wing_half_area']:.4f} m^2\n"
            f"Wing AR: {stats.loc[base_config.name, 'wing_aspect_ratio']:.4f}\n"
            f"Centerbody Half Area: {stats.loc[base_config.name, 'centerbody_half_area']:.4f} m^2\n"
            f"Centerbody AR: {stats.loc[base_config.name, 'centerbody_aspect_ratio']:.4f}\n"
            f"Overall Centroid (x): {stats.loc[base_config.name, 'overall_centroid']:.4f} mm\n"
            f"Wing Centroid (x): {stats.loc[base_config.name, 'wing_centroid']:.4f} mm\n"
            f"Centerbody Centroid (x): {stats.loc[base_config.name, 'centerbody_centroid']:.4f} mm\n"
            f"Wing Mean Aerodynamic Chord: {stats.loc[base_config.name, 'wing_mean_aerodynamic_chord']:.4f} mm\n"
            f"Proportion of Wing Area: {2*stats.loc[base_config.name, 'wing_half_area']/stats.loc[base_config.name, 'overall_area']:.4f}\n"
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
            valmax=(
                getattr(base_config, attr) * 2 if getattr(base_config, attr) > 1 else 1
            ),
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
