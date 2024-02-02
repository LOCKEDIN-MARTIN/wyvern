from wyvern.performance.models import QuadraticLDModel
from wyvern.utils.constants import RHO


def cL_required(speed_ms: float, wing_loading_Nm2: float):
    """
    Calculate the lift coefficient required for a given speed and wing loading.
    """
    return wing_loading_Nm2 / (0.5 * RHO * speed_ms**2)


def thrust_required(
    ld_model: QuadraticLDModel, speed_ms: float, wing_loading_Nm2: float
):
    """
    Calculate the thrust required for a given speed and wing loading.
    """
    cL = cL_required(speed_ms, wing_loading_Nm2)
    cD = ld_model.c_D(cL)
    return 0.5 * RHO * speed_ms**2 * cD * wing_loading_Nm2


def power_required(
    ld_model: QuadraticLDModel, speed_ms: float, wing_loading_Nm2: float
):
    """
    Calculate the power required for a given speed and wing loading.
    """
    return thrust_required(ld_model, speed_ms, wing_loading_Nm2) * speed_ms
