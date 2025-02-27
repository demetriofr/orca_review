# EXAMPLE_USAGE: How to run CutORCA.py with custom parameters
#
# Run with default settings:
#   python CutORCA.py
#
# Run with custom file paths:
#   python CutORCA.py --input /path/to/custom_input.nc \
#                     --output_dir /path/to/output/ \
#                     --output_file custom_output.nc

import argparse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Pacific region indices (loaded from .env)
PACIFIC_INDICES = {
    "y_min": int(os.getenv("PAC_FIRST_YIND", 7550)),
    "y_max": int(os.getenv("PAC_LAST_YIND", -2)),
    "x_min": int(os.getenv("PAC_FIRST_XIND", 1500)),
    "x_max": int(os.getenv("PAC_LAST_XIND", 5900)),
}

# Atlantic region indices (loaded from .env)
ATLANTIC_INDICES = {
    "y_min": int(os.getenv("ATL_FIRST_YIND", 7350)),
    "y_max": int(os.getenv("ATL_LAST_YIND", -1)),
}

# Default file paths (now from .env)
DEFAULT_INPUT_PATH = os.getenv("INPUT_PATH",
                               "/mnt/localssd/Data_nemo/Meshes_domains/Coordinates/Global/ORCA_R36_coord_new.nc"
                               )
DEFAULT_TARGET_PATH = os.getenv("TARGET_PATH", "/mnt/localssd/Data_nemo/Meshes_domains/Coordinates/Regional")
DEFAULT_TARGET_FILE = os.getenv("TARGET_FILE", "arct_cutorca36_coord.nc")


def get_args():
    """Parse command-line arguments."""

    # Set up argument parser to allow flexible file input/output
    parser = argparse.ArgumentParser(description="Process ORCA NetCDF file.")

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

    # Check if input file exists before proceeding
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"❌ ERROR: Input file '{args.input}' not found!")

    # Ensure the output directory exists
    try:
        os.makedirs(args.output_dir, exist_ok=True)
    except (PermissionError, OSError) as e:
        raise OSError(
            f"❌ ERROR: Unable to create or write to directory '{args.output_dir}'."
            f"Check permissions and path. ({e})"
        )

    return args
