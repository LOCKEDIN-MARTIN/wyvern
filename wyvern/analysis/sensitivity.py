import inspect
from typing import Callable

from pandas import DataFrame


def param_sweep(
    func: Callable, params: tuple, param_name: str, param_values: list, **kwargs
) -> DataFrame:
    """Apply parametric sweep to a function over a single parameter.

    Parameters
    ----------
    func : Callable
        Function to assess.
    params : tuple
        Parameters to pass to the function.
    param_name : str
        Name of the parameter to vary.
    param_values : list
        List of values to vary the parameter over.

    Returns
    -------
    DataFrame
        Dataframe of results.
    """
    results = {}

    # Introspect function signature to get parameter names
    func_params = inspect.signature(func).parameters.keys()
    # get index of parameter to vary
    try:
        param_idx = list(func_params).index(param_name)
    except ValueError:
        raise ValueError(f"Parameter {param_name} not found in function signature.")

    # allow for dot-access to sub-parameters for Dataclasses
    if "." in param_name:
        param_name, sub_param_name = param_name.split(".")
    else:
        sub_param_name = None

    for param_value in param_values:
        # make a copy of the params
        params_ = list(params)

        # set the parameter value
        if sub_param_name is not None:
            params_[param_idx].__dict__[sub_param_name] = param_value
        else:
            params_[param_idx] = param_value

        results[param_value] = func(*params_, **kwargs)

    return DataFrame(results).T


def finite_diff_sensitivity(
    func: Callable, params: tuple, param_name: str, dx: float = 1e-6, **kwargs
):
    """Calculate the sensitivity of a function wrt a parameter using finite difference.

    Parameters
    ----------
    func : Callable
        Function to assess.
    params : tuple
        Parameters to pass to the function.
    param_name : str
        Name of the parameter to vary. Assumes the parameter is a float type.
    dx : float, optional
        Size of the finite difference, by default 1e-6.

    Returns
    -------
    float
        Sensitivity of the function wrt the parameter.

    Algorithm
    ---------
    Uses 2nd order central difference.
    """
    # make a copy of the params
    params_ = list(params)

    # Introspect function signature to get parameter names
    func_params = inspect.signature(func).parameters.keys()
    # get index of parameter to vary
    try:
        param_idx = list(func_params).index(param_name)
    except ValueError:
        raise ValueError(f"Parameter {param_name} not found in function signature.")

    # make sure the parameter is a float
    if not isinstance(params_[param_idx], float):
        raise TypeError(f"Parameter {param_name} must be a float.")

    # allow for dot-access to sub-parameters for Dataclasses
    if "." in param_name:
        param_name, sub_param_name = param_name.split(".")
    else:
        sub_param_name = None

    # get the baseline value
    if sub_param_name is not None:
        baseline = params_[param_idx].__dict__[sub_param_name]
    else:
        baseline = params_[param_idx]

    # set the parameter value
    if sub_param_name is not None:
        params_[param_idx].__dict__[sub_param_name] = baseline + dx
    else:
        params_[param_idx] = baseline + dx

    # get the value at the perturbed point
    perturbed_fwd = func(*params_, **kwargs)

    # set the parameter value
    if sub_param_name is not None:
        params_[param_idx].__dict__[sub_param_name] = baseline - dx
    else:
        params_[param_idx] = baseline - dx

    perturbed_bwd = func(*params_, **kwargs)

    # calculate the sensitivity
    return (perturbed_fwd - perturbed_bwd) / (2 * dx)
