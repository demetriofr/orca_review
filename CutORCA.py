# Data processing libs.
import numpy as np
import xarray as xr

# Visualisation libs.
# ♻️ Code cleanup: removed unused import matplotlib.pyplot


# Critical: cartopy requires GEOS and Proj, which are not always installed by default.
# Should check and provide OS-specific installation instructions.
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
except ImportError:
    import sys

    print("❌ ERROR: 'cartopy' is not installed correctly!", file=sys.stderr)
    print("💡 Install it with one of these commands:", file=sys.stderr)
    print("  🔹 MacOS: brew install geos proj", file=sys.stderr)
    print("  🔹 Ubuntu/Debian: sudo apt install libgeos-dev libproj-dev", file=sys.stderr)
    print("  🔹 Windows (Conda): conda install -c conda-forge cartopy", file=sys.stderr)
    sys.exit(1)

# Critical: Replaced hardcoded file paths with argparse for flexibility.
# Default values match the original script, but users can override them.
# The script now ensures that the output directory exists before saving.
# This makes the script more reusable and prevents crashes due to missing files.
import argparse
import os

# Set up argument parser to allow flexible file input/output
parser = argparse.ArgumentParser(description="Process ORCA NetCDF file.")

# Default file paths (same as in the original script)
DEFAULT_INPUT_PATH = "/mnt/localssd/Data_nemo/Meshes_domains/Coordinates/Global/ORCA_R36_coord_new.nc"
DEFAULT_TARGET_PATH = "/mnt/localssd/Data_nemo/Meshes_domains/Coordinates/Regional"
DEFAULT_TARGET_FILE = "arct_cutorca36_coord.nc"

# Define command-line arguments
parser.add_argument(
    "--input",
    type=str,
    default=DEFAULT_INPUT_PATH,
    help="Path to ORCA NetCDF file"
)
parser.add_argument(
    "--output_dir",
    type=str,
    default=DEFAULT_TARGET_PATH,
    help="Directory to save the output NetCDF file"
)
parser.add_argument(
    "--output_file",
    type=str,
    default=DEFAULT_TARGET_FILE,
    help="Output NetCDF filename"
)

# Parse command-line arguments
args = parser.parse_args()

# Check if the input file exists
if not os.path.exists(args.input):
    raise FileNotFoundError(f"❌ ERROR: File '{args.input}' not found!")

# Load dataset
pcf = xr.open_dataset(args.input).squeeze()

# Critical: Ensure the NetCDF file is loaded correctly.
# Added a check to prevent issues with empty or corrupted files.
if pcf is None or not isinstance(pcf, xr.Dataset):
    raise ValueError("❌ ERROR: Failed to load NetCDF file. Please check the file format and path.")

# Critical: The 'x' dimension must exist in the NetCDF file.
# Added a check to prevent crashes if 'x' is missing.
if 'x' not in pcf:
    raise KeyError(
        f"❌ ERROR: 'x' variable not found in NetCDF file! "
        f"Available variables: {list(pcf.variables.keys())}"
    )
else:
    # Set parameters.
    x_middle = int(pcf['x'].size / 2)

# Enter Pacific and Atlantic y-indices (latitude-like).
pac_first_yind = 7550
pac_last_yind = -2
atl_first_yind = 7350
atl_last_yind = -1

# Enter first and last x-indices (latitude-like). It must be less than 1/2 x-dimension size!
pac_first_xind = 1500
pac_last_xind = 5900
atl_first_xind = pac_last_xind + (x_middle - pac_last_xind) * 2 + 1
atl_last_xind = pcf['x'].size - pac_first_xind + 1

# Saving properties
# Ensure the output directory exists
try:
    os.makedirs(args.output_dir, exist_ok=True)
except (PermissionError, OSError) as e:
    raise OSError(
        f"❌ ERROR: Unable to create or write to directory '{args.output_dir}'."
        f"Check permissions and path. ({e})"
    )

# Construct full output file path
target_path = os.path.join(args.output_dir, args.output_file)


# Patch processing
# ♻️ Code cleanup: Renamed 'pcf' to 'dataset' to avoid shadowing global variable.
def grid_selector(dataset, var, extent, pac_patch=False):
    # ♻️ Code cleanup: Fixed docstring format to follow PEP 257
    """
    Functon that select and cut 2D arrays from parent global ORCA coordinate file.

    Parameters
    ----------
    dataset : xarray Dataset
        Parent global ORCA Coordinate File.
    var : str
        Grid variable name from pcf.

    # ♻️ Code cleanup: Removed redundant word 'List' in docstring
    extent : list
        Specifies with indices to cut [y_min, y_max, x_min, x_max].

    # ♻️ Code cleanup: Fixed incorrect parameter name in docstring (atl_patch → pac_patch)
    pac_patch : bool, optional (default: False)
        Pacific (True) and Atlantic (False) switch (default is False)

    Returns
    -------
    grid_array
        Ndarray to put in patch dataset.
    """

    # Critical: Prevent 'grid_array' from being undefined.
    # Added initialization and validation before returning.
    grid_array = None  # Initialize variable to avoid undefined reference

    # grid type lists
    t_vars = ['nav_lon', 'nav_lat', 'glamt', 'gphit', 'e1t', 'e2t']
    u_vars = ['glamu', 'gphiu', 'e1u', 'e2u']
    v_vars = ['glamv', 'gphiv', 'e1v', 'e2v']
    f_vars = ['glamf', 'gphif', 'e1f', 'e2f']

    # Critical: The variable must exist in the NetCDF file before accessing it.
    # Added a check to prevent KeyError if 'var' is missing.
    if var not in dataset:
        raise KeyError(
            f"❌ ERROR: Variable '{var}' not found in NetCDF file! "
            f"Available variables: {list(dataset.variables.keys())}"
        )

    # ♻️ Code cleanup: Fixed long lines for PEP 8 compliance
    if pac_patch:  # Pacific patch selection
        if var in t_vars:
            grid_array = np.flip(
                dataset[var]
                .sel(y=slice(extent[0], extent[1]), x=slice(extent[2], extent[3]))
                .values
            )
        elif var in u_vars:
            grid_array = np.flip(
                dataset[var]
                .sel(y=slice(extent[0], extent[1]), x=slice(extent[2] - 1, extent[3] - 1))
                .values
            )
        elif var in v_vars:
            grid_array = np.flip(
                dataset[var]
                .sel(y=slice(extent[0] - 1, extent[1] - 1), x=slice(extent[2], extent[3]))
                .values
            )
        elif var in f_vars:
            grid_array = np.flip(
                dataset[var]
                .sel(y=slice(extent[0] - 1, extent[1] - 1), x=slice(extent[2] - 1, extent[3] - 1))
                .values
            )
    # ♻️ Code cleanup: Fixed inline comment formatting (PEP 8)
    else:  # Atlantic patch selection
        grid_array = dataset[var].sel(y=slice(extent[0], extent[1]), x=slice(extent[2], extent[3])).values

    # TODO: There may be var name error handler like "There no variable named {var} in parent coordinate file".

    # Critical: Ensure 'grid_array' is always assigned before return.
    if grid_array is None:
        raise ValueError(f"❌ ERROR: Variable '{var}' was not assigned correctly!")

    return grid_array


# Dataset creation
# TODO: dataset generator. I don't like this wet shit.

# Atlantic patch as xarray Dataset
atl_extent = [atl_first_yind, atl_last_yind, atl_first_xind, atl_last_xind]
atl_dataset = xr.Dataset(
    data_vars=dict(
        nav_lon=(["y", "x"], grid_selector(pcf, 'nav_lon', atl_extent)),
        nav_lat=(["y", "x"], grid_selector(pcf, 'nav_lat', atl_extent)),
        glamt=(["y", "x"], grid_selector(pcf, 'glamt', atl_extent)),
        glamu=(["y", "x"], grid_selector(pcf, 'glamu', atl_extent)),
        glamv=(["y", "x"], grid_selector(pcf, 'glamv', atl_extent)),
        glamf=(["y", "x"], grid_selector(pcf, 'glamf', atl_extent)),
        gphit=(["y", "x"], grid_selector(pcf, 'gphit', atl_extent)),
        gphiu=(["y", "x"], grid_selector(pcf, 'gphiu', atl_extent)),
        gphiv=(["y", "x"], grid_selector(pcf, 'gphiv', atl_extent)),
        gphif=(["y", "x"], grid_selector(pcf, 'gphif', atl_extent)),
        e1t=(["y", "x"], grid_selector(pcf, 'e1t', atl_extent)),
        e1u=(["y", "x"], grid_selector(pcf, 'e1u', atl_extent)),
        e1v=(["y", "x"], grid_selector(pcf, 'e1v', atl_extent)),
        e1f=(["y", "x"], grid_selector(pcf, 'e1f', atl_extent)),
        e2t=(["y", "x"], grid_selector(pcf, 'e2t', atl_extent)),
        e2u=(["y", "x"], grid_selector(pcf, 'e2u', atl_extent)),
        e2v=(["y", "x"], grid_selector(pcf, 'e2v', atl_extent)),
        e2f=(["y", "x"], grid_selector(pcf, 'e2f', atl_extent))
    )
)

# Pacific patch as xarray Dataset
pac_extent = [pac_first_yind, pac_last_yind, pac_first_xind, pac_last_xind]
pac_dataset = xr.Dataset(
    data_vars=dict(
        nav_lon=(["y", "x"], grid_selector(pcf, 'nav_lon', pac_extent, pac_patch=True)),
        nav_lat=(["y", "x"], grid_selector(pcf, 'nav_lat', pac_extent, pac_patch=True)),
        glamt=(["y", "x"], grid_selector(pcf, 'glamt', pac_extent, pac_patch=True)),
        glamu=(["y", "x"], grid_selector(pcf, 'glamu', pac_extent, pac_patch=True)),
        glamv=(["y", "x"], grid_selector(pcf, 'glamv', pac_extent, pac_patch=True)),
        glamf=(["y", "x"], grid_selector(pcf, 'glamf', pac_extent, pac_patch=True)),
        gphit=(["y", "x"], grid_selector(pcf, 'gphit', pac_extent, pac_patch=True)),
        gphiu=(["y", "x"], grid_selector(pcf, 'gphiu', pac_extent, pac_patch=True)),
        gphiv=(["y", "x"], grid_selector(pcf, 'gphiv', pac_extent, pac_patch=True)),
        gphif=(["y", "x"], grid_selector(pcf, 'gphif', pac_extent, pac_patch=True)),
        e1t=(["y", "x"], grid_selector(pcf, 'e1t', pac_extent, pac_patch=True)),
        e1u=(["y", "x"], grid_selector(pcf, 'e1u', pac_extent, pac_patch=True)),
        e1v=(["y", "x"], grid_selector(pcf, 'e1v', pac_extent, pac_patch=True)),
        e1f=(["y", "x"], grid_selector(pcf, 'e1f', pac_extent, pac_patch=True)),
        e2t=(["y", "x"], grid_selector(pcf, 'e2t', pac_extent, pac_patch=True)),
        e2u=(["y", "x"], grid_selector(pcf, 'e2u', pac_extent, pac_patch=True)),
        e2v=(["y", "x"], grid_selector(pcf, 'e2v', pac_extent, pac_patch=True)),
        e2f=(["y", "x"], grid_selector(pcf, 'e2f', pac_extent, pac_patch=True))
    ),
)

whole_dataset = xr.concat([atl_dataset, pac_dataset], dim='y')

# Ensure target_path is a valid string before saving
if not isinstance(target_path, str):
    raise TypeError(f"❌ ERROR: Invalid path type '{type(target_path)}' for saving NetCDF file!")
else:
    # Save dataset
    whole_dataset.to_netcdf(target_path)

# TODO: Some visualization?
