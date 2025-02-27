# CutORCA - Ocean Grid Cutter

This script extracts specific ocean grid regions from a NetCDF dataset.

## 🚀 Usage

### Default run:
```bash
python CutORCA.py
```
Run with custom paths:
```bash
python CutORCA.py --input /path/to/custom_input.nc \
                  --output_dir /path/to/output/ \
                  --output_file custom_output.nc
```
## 📁 Configuration
* Default input file: /mnt/localssd/Data_nemo/Meshes_domains/Coordinates/Global/ORCA_R36_coord_new.nc
* Default output directory: /mnt/localssd/Data_nemo/Meshes_domains/Coordinates/Regional
* Default output file: arct_cutorca36_coord.nc
## 🛠 Requirements
* Python 3.8+
* Required libraries: numpy, xarray, matplotlib, cartopy
* Install dependencies:
```bash
pip install -r requirements.txt
```
## ❓ Troubleshooting
If cartopy is not installed correctly, install dependencies manually:
```bash
brew install geos proj  # MacOS
sudo apt install libgeos-dev libproj-dev  # Ubuntu/Debian
conda install -c conda-forge cartopy  # Windows (Conda)
```