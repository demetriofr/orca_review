import numpy as np


def validate_indices(dataset, extent):
    """
    Ensures indices do not go out of dataset bounds.

    Parameters
    ----------
    dataset : xarray.Dataset
        The parent global ORCA coordinate file.
    extent : list
        Indices defining the region to cut [y_min, y_max, x_min, x_max].

    Returns
    -------
    tuple
        Corrected indices (y_min, y_max, x_min, x_max).
    """
    y_min = max(0, extent[0] - 1)
    y_max = min(dataset.dims["y"], extent[1] - 1)
    x_min = max(0, extent[2] - 1)
    x_max = min(dataset.dims["x"], extent[3] - 1)
    return y_min, y_max, x_min, x_max


def grid_selector(dataset, var, extent, pac_patch=False):
    """
    Function that selects and cuts 2D arrays from the parent global ORCA coordinate file.

    Parameters
    ----------
    dataset : xarray.Dataset
        Parent global ORCA Coordinate File.
    var : str
        Grid variable name from the dataset.
    extent : list
        Indices defining the region to cut [y_min, y_max, x_min, x_max].
    pac_patch : bool, optional (default: False)
        Pacific (True) or Atlantic (False) switch.

    Returns
    -------
    grid_array : np.ndarray
        Extracted 2D array for use in the patch dataset.

    Raises
    ------
    KeyError
        If `var` is not found in the NetCDF dataset.
    ValueError
        If `var` is not a recognized grid variable.
        If `grid_array` was not correctly assigned.
    """

    grid_array = None  # Initialize variable to avoid undefined reference

    # grid type lists
    t_vars = ['nav_lon', 'nav_lat', 'glamt', 'gphit', 'e1t', 'e2t']
    u_vars = ['glamu', 'gphiu', 'e1u', 'e2u']
    v_vars = ['glamv', 'gphiv', 'e1v', 'e2v']
    f_vars = ['glamf', 'gphif', 'e1f', 'e2f']
    valid_vars = t_vars + u_vars + v_vars + f_vars  # Combined list for cleaner checks

    # Added a check to prevent KeyError if 'var' is missing.
    if var not in dataset:
        raise KeyError(
            f"❌ ERROR: Variable '{var}' not found in NetCDF file! "
            f"Available variables: {list(dataset.variables.keys())}"
        )

    # Improvement: Added an extra validation step to ensure the variable belongs to expected grid types.
    # The dataset may contain other variables that are not relevant for grid processing.
    # This check prevents unintended selections and improves error handling.
    if var not in valid_vars:
        raise ValueError(f"❌ ERROR: Unknown variable '{var}'. Expected one of the following variables {valid_vars}.")

    # Critical: Prevents index out of bounds error when extent[0] == 0
    # Ensures y and x indices stay within dataset boundaries
    # Prevent index out of bounds error
    y_min, y_max, x_min, x_max = validate_indices(dataset, extent)

    # Select data based on variable type
    if pac_patch:  # Pacific patch selection
        if var in t_vars:
            grid_array = np.flip(dataset[var].sel(y=slice(*extent[:2]), x=slice(*extent[2:4])).values)
        elif var in u_vars:
            grid_array = np.flip(dataset[var].sel(y=slice(*extent[:2]), x=slice(extent[2] - 1, extent[3] - 1)).values)
        elif var in v_vars:
            grid_array = np.flip(dataset[var].sel(y=slice(y_min, y_max), x=slice(*extent[2:4])).values)
        elif var in f_vars:
            grid_array = np.flip(dataset[var].sel(y=slice(y_min, y_max), x=slice(x_min, x_max)).values)
    else:  # Atlantic patch selection
        grid_array = dataset[var].sel(y=slice(*extent[:2]), x=slice(*extent[2:4])).values

    if grid_array is None:
        raise ValueError(f"❌ ERROR: Variable '{var}' was not assigned correctly!")

    return grid_array
