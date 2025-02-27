import xarray as xr
import os


def load_netcdf(file_path):
    """Load a NetCDF file and perform basic validation."""

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ ERROR: File '{file_path}' not found!")

    dataset = xr.open_dataset(file_path, engine="netcdf4").squeeze()

    if dataset is None or not isinstance(dataset, xr.Dataset):
        raise ValueError("❌ ERROR: Failed to load a valid NetCDF dataset. Please check the file format and path.")

    if 'x' not in dataset:
        raise KeyError(
            f"❌ ERROR: 'x' variable not found in NetCDF file! "
            f"Available variables: {list(dataset.variables.keys())}"
        )

    return dataset


def save_netcdf(dataset, target_path):
    """
    Save an xarray dataset to a NetCDF file.

    Parameters
    ----------
    dataset : xarray.Dataset
        The dataset to be saved.
    target_path : str
        The full path (directory + filename) to save the NetCDF file.

    Raises
    ------
    TypeError
        If `target_path` is not a valid string.
    OSError
        If there are issues creating the output directory.
    """

    if not isinstance(target_path, str):
        raise TypeError(f"❌ ERROR: Invalid path type '{type(target_path)}' for saving NetCDF file!")

    # Ensure the directory exists
    output_dir = os.path.dirname(target_path)
    try:
        os.makedirs(output_dir, exist_ok=True)
    except (PermissionError, OSError) as e:
        raise OSError(
            f"❌ ERROR: Unable to create or write to directory '{output_dir}'. Check permissions and path. ({e})"
        )

    # Save dataset
    dataset.to_netcdf(target_path)
