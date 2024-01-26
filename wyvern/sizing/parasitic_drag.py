def cd0_zeroth_order(c_fe: float, s_wet_s_ref) -> float:
    """Estimate the parasitic drag coefficient using a crude method.

    Parameters
    ----------
    c_fe : float
        Skin friction coefficient.
    s_wet_s_ref : float
        Wetted area to wing area ratio.

    Returns
    -------
    float
        parasitic drag coefficient.
    """
    return c_fe * s_wet_s_ref


def cd0_buildup():
    """Estimate the parasitic drag coefficient using a more detailed method."""
    pass
