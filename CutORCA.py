import os
# Data processing libs.
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

from utils.config import get_args, PACIFIC_INDICES, ATLANTIC_INDICES
from utils.netcdf_utils import load_netcdf, save_netcdf
from modules.dataset_builder import create_ocean_dataset

# Improvement: Move argument parsing to a separate module (config.py)
# to keep the main script cleaner and more maintainable.
args = get_args()

# Improvement: Move NetCDF loading and validation to a separate module (netcdf_utils.py)
# to keep the main script cleaner and improve reusability.
# Load dataset
pcf = load_netcdf(args.input)

# Set parameters.
x_middle = int(pcf['x'].size / 2)

# Calculate Atlantic x-indices dynamically
atl_first_xind = PACIFIC_INDICES["x_max"] + (x_middle - PACIFIC_INDICES["x_max"]) * 2 + 1
atl_last_xind = pcf['x'].size - PACIFIC_INDICES["x_min"] + 1

# Use Pacific and Atlantic indices from config
pac_first_yind, pac_last_yind, pac_first_xind, pac_last_xind = (
    PACIFIC_INDICES["y_min"], PACIFIC_INDICES["y_max"],
    PACIFIC_INDICES["x_min"], PACIFIC_INDICES["x_max"]
)
atl_first_yind, atl_last_yind = ATLANTIC_INDICES["y_min"], ATLANTIC_INDICES["y_max"]


# Saving properties

# Construct full output file path
target_path = os.path.join(args.output_dir, args.output_file)

# Improvement: Move the grid selection logic to a separate module (grid_utils.py)
# to improve code modularity and reusability.
# Patch processing
# Dataset creation


# Improvement: Created a separate module for dataset creation
# This improves modularity, reusability, and makes `CutORCA.py` cleaner

# Atlantic patch as xarray Dataset
atl_extent = [atl_first_yind, atl_last_yind, atl_first_xind, atl_last_xind]
atl_dataset = create_ocean_dataset(pcf, atl_extent, pac_patch=False)


# Pacific patch as xarray Dataset
pac_extent = [pac_first_yind, pac_last_yind, pac_first_xind, pac_last_xind]
pac_dataset = create_ocean_dataset(pcf, pac_extent, pac_patch=True)


whole_dataset = xr.concat([atl_dataset, pac_dataset], dim='y')

# Save the final dataset
save_netcdf(whole_dataset, target_path)

# TODO: Some visualization?

# Improvement
# TODO: Further improvements 🚀
#
# 🔹 Add logging instead of print statements (utils/logger.py)
#     - Use logging instead of print for better debugging and monitoring
#     - Log errors, warnings, and key execution steps
#
# 🔹 Implement unit tests (tests/)
#     - Use pytest to test core functions (e.g., grid_selector, load_netcdf)
#     - Ensure correct handling of missing variables and file errors
#
# 🔹 Improve error handling
#     - Catch and log unexpected exceptions
#     - Provide user-friendly error messages
#
# 🔹 Optimize dataset processing
#     - Investigate performance bottlenecks in grid slicing
#     - Consider parallelization for large datasets
#
# 🔹 Enhance configuration management
#     - Move more parameters to .env/config file
#     - Allow users to configure regions dynamically
#
# 🔹 Add visualization
#     - Generate plots/maps using matplotlib/cartopy for dataset preview
#     - Save sample images with coordinate overlays
