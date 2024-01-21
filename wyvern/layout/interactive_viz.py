# interactive version of planform visualization

from matplotlib import pyplot as plt
from matplotlib.widgets import Slider

from wyvern.layout.geom_utils import area_of_points
from wyvern.layout.planform import (
    PlanformParameters,
    centerbody_points,
    full_planform_points,
    planform_span_stations,
    wing_points,
)


def planform_viz_interactive(base_config: PlanformParameters):
    """
    Launches interactive visualization of planform parameters.
    """
    # Sliders corresponding to planform parameters

    # find class attrs by type hint; get only float attrs
    attrs = [
        attr for attr, hint in base_config.__annotations__.items() if hint == float
    ]

    # we will have one slider per attribute
    sliders = [
        Slider(
            ax=plt.axes([0.35, 0.1 + 0.06 * idx, 0.55, 0.05]),
            label=attr,
            valmin=0,
            valmax=getattr(base_config, attr) * 3,
            valinit=getattr(base_config, attr),
            valstep=0.01,
        )
        for (idx, attr) in enumerate(attrs)
    ]
    plt.title("Parameters")

    # main plot
    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ax.set_title("Planform Visualization")
    ax.invert_yaxis()

    # update plot when sliders are changed
    df = planform_span_stations(base_config)
    pts = full_planform_points(df)
    wing_pts = wing_points(df)
    cb_pts = centerbody_points(df)

    area = area_of_points(pts)

    cb_area = area_of_points(cb_pts)
    wing_area = area_of_points(wing_pts)
    ax.set_title(
        f"Area: {2*wing_area/1e6:.3f} (W) + {2*cb_area/1e6:.3f} (CB) = {area/1e6:.3f} $m^2$"
    )

    (planform_plot,) = ax.plot(pts[:, 0], pts[:, 1], "k-")

    def _update_plot(_):
        # update all attrs
        for attr, slider in zip(attrs, sliders):
            setattr(base_config, attr, slider.val)

        # update plot
        df = planform_span_stations(base_config)
        pts = full_planform_points(df)
        planform_plot.set_xdata(pts[:, 0])
        planform_plot.set_ydata(pts[:, 1])
        fig.canvas.draw_idle()

        # recalculate areas
        area = area_of_points(pts)

        cb_area = area_of_points(cb_pts)
        wing_area = area_of_points(wing_pts)
        ax.set_title(
            f"Area: {2*wing_area/1e6:.3f} (W) + {2*cb_area/1e6:.3f} (CB) = {area/1e6:.3f} $m^2$"
        )

    for slider in sliders:
        slider.on_changed(_update_plot)

    plt.show()


if __name__ == "__main__":
    NF_844_A = PlanformParameters(
        name="NF-844-A",
        centerbody_halfspan=170,
        centerbody_chord=650,
        midbody_y=140,
        midbody_xle=100,
        midbody_chord=500,
        wing_root_le=300,
        wing_root_chord=300,
        wing_halfspan=600,
        wing_taper_ratio=0.33333,
        wing_root_le_sweep_angle=40,
        ctrl_surface_start_y=500,
        ctrl_surface_end_y=700,
        ctrl_surface_x_over_c=0.3,
    )
    planform_viz_interactive(NF_844_A)
