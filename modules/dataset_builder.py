import xarray as xr
from utils.grid_utils import grid_selector


def create_ocean_dataset(dataset, extent, pac_patch=False):
    """
    Creates an xarray.Dataset for a specific ocean region.

    Parameters
    ----------
    dataset : xarray.Dataset
        The parent global ORCA coordinate file.
    extent : list
        Indices defining the region to cut [y_min, y_max, x_min, x_max].
    pac_patch : bool, optional (default: False)
        Pacific (True) or Atlantic (False) switch.

    Returns
    -------
    xarray.Dataset
        A dataset containing the selected ocean region.
    """

    # Define grid variables categorized by type
    variables = {
        "nav_lon", "nav_lat",  # Geographic coordinates (longitude, latitude)
        "glamt", "glamu", "glamv", "glamf",  # Grid cell center (T), U, V, and F points
        "gphit", "gphiu", "gphiv", "gphif",  # Geographical positions for T, U, V, F points
        "e1t", "e1u", "e1v", "e1f",  # Grid spacing in x-direction for T, U, V, F points
        "e2t", "e2u", "e2v", "e2f"   # Grid spacing in y-direction for T, U, V, F points
    }

    return xr.Dataset(
        data_vars={var: (["y", "x"], grid_selector(dataset, var, extent, pac_patch))
                   for var in sorted(variables)}
    )
