# Uruguay Climate Change Projections & Variability Analysis

> A high-resolution, physics-grounded framework for diagnosing historical climate variability and projecting future scenarios over Uruguay and the broader SESA domain, built on CMIP5/6 multi-model ensembles and CRU observational benchmarks.

---

## Abstract

Southeastern South America (SESA) sits at the intersection of competing large-scale circulation drivers — the South Atlantic Convergence Zone (SACZ), the Low-Level Jet east of the Andes, and mid-latitude baroclinic systems — making it one of the most dynamically complex regions for near-term climate attribution and projection. Uruguay, located at the southern edge of SESA (~30–35°S), exhibits strong inter-annual precipitation variability linked to ENSO teleconnections and a detectable warming trend in surface temperature over recent decades.

This repository provides a reproducible, modular Python framework to:

1. **Quantify historical temperature and precipitation anomalies** from CRU gridded observations (1950–present).
2. **Evaluate CMIP5/6 model fidelity** over Uruguay using standard skill metrics (RMSE, annual bias, Variability Index).
3. **Derive future climate projections** from bias-corrected model ensembles under multiple Representative Concentration Pathways (RCPs) and Shared Socioeconomic Pathways (SSPs).
4. **Characterize low-level circulation changes** at 1000 hPa via linear trend analysis and regression diagnostics.

Outputs are intended to directly inform regional adaptation policy, hydrological risk assessment, and agricultural planning in Uruguay.

---

## Key Features

- **Vectorized spatial masking** — Country and departmental boundaries from official Uruguayan shapefiles are rasterized and applied as NumPy boolean masks, enabling fully vectorized regional averaging without Python-level loops. Regional means scale efficiently with ensemble size.
- **Physically consistent regridding** — Conservative interpolation (area-weighted) is implemented in `src/utils.py` using `scipy` spatial routines and `iris` cube transformations, preserving global flux integrals when downscaling coarse CMIP grids (~1°–2°) to the CRU reference grid (0.5°).
- **Multi-model ensemble handling** — Processes CMIP5 and CMIP6 archives in NetCDF4 format; supports lazy loading via `netCDF4` variable slicing to manage large ensemble memory footprints.
- **Comprehensive skill scoring** — Per-model metrics (RMSE, mean annual bias, Variability Index) computed over a common 1980–2014 historical baseline, with outputs serialized for ensemble ranking and model weighting.
- **Automated visualization pipeline** — Cartopy-based figures for climatological maps, difference maps (future minus baseline), and time series with overlaid uncertainty envelopes are generated reproducibly from a single pipeline call.

---

## Installation

**Requirements:** Python 3.9+, `conda` or `pip`.

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/uy-climate-projections.git
cd uy-climate-projections
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate.bat     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `cartopy` and `iris` require system-level libraries (GEOS, PROJ). On Linux, install via:
> ```bash
> sudo apt-get install libgeos-dev libproj-dev
> ```
> On macOS via Homebrew:
> ```bash
> brew install geos proj
> ```
> A `conda`-based install resolves these dependencies automatically:
> ```bash
> conda env create -f environment.yml
> conda activate uy-climate
> ```

---

## Project Structure

```
uy-climate-projections/
│
├── src/                        # Core analysis modules
│   ├── utils.py                # Regridding (conservative interp.), vectorized masking, I/O helpers
│   ├── anomalies.py            # Temperature & precipitation anomaly computation
│   ├── trends.py               # Linear trend estimation (Sen's slope, OLS) on wind fields
│   ├── metrics.py              # Model skill metrics: RMSE, annual bias, Variability Index (VI)
│   └── visualize.py            # Cartopy/Iris plotting routines for maps and time series
│
├── data/
│   ├── netcdf/                 # Raw NetCDF4 files
│   │   ├── cru/                # CRU TS4.x observational grids (tmp, pre)
│   │   └── cmip/               # CMIP5/6 model output (historical + scenario runs)
│   └── shapefiles/             # Official Uruguayan administrative boundaries (IGM/INE)
│       ├── uruguay_country.shp
│       └── departamentos/
│
├── outputs/                    # Generated figures (not tracked in git)
│   ├── climatologies/          # Baseline mean-state maps
│   ├── difference_maps/        # Future – baseline anomaly maps
│   └── timeseries/             # Regional-mean time series with ensemble spread
│
├── notebooks/                  # Exploratory Jupyter notebooks
│
├── requirements.txt
├── environment.yml             # Conda environment spec
└── README.md
```

The `src/` directory is intentionally flat; each module exposes a well-defined public API and imports only from `utils.py` to avoid circular dependencies. All file paths are resolved relative to the project root via a single `config.py` constant, making the pipeline portable across HPC and local environments.

---

## Methodology

### Observational Baseline (CRU)

Monthly gridded temperature (`tmp`) and precipitation (`pre`) fields from CRU TS4.07 serve as the observational reference. Data are loaded as masked NetCDF4 arrays, quality-flagged grid cells are excluded via the associated `stn` coverage file, and the Uruguay domain (53°W–58°W, 30°S–35°S) is extracted before further processing.

### Model Data (CMIP5/6)

Each model's historical simulation is regridded to the CRU 0.5° reference grid using conservative area-weighted interpolation (`src/utils.py: regrid_conservative()`). A common temporal baseline (1980–2014) is enforced across all models before anomaly computation.

### Bias Correction & Anomaly Computation

Temperature anomalies are expressed as departures from the 1980–2014 climatological mean. Precipitation anomalies are expressed as percentage departures. Spatial averages over Uruguay are computed using the vectorized shapefile mask; departmental sub-averages use the nested `departamentos/` mask stack.

### Skill Metrics

For each CMIP model *m*:

| Metric | Definition |
|---|---|
| **RMSE** | √[ (1/N) Σ (T̂ᵢ − Tᵢ)² ] over monthly climatology |
| **Annual Bias** | Mean(T̂_annual) − Mean(T_annual) |
| **Variability Index (VI)** | σ_model / σ_obs, where σ is inter-annual std. dev. |

Models are ranked by a composite score and optionally weighted for ensemble projection.

### Trend Analysis (Wind at 1000 hPa)

Zonal and meridional wind components at 1000 hPa are extracted from CMIP6 historical runs. Linear trends (OLS and Sen's slope) are computed per grid point over 1950–2014. Regression maps are produced showing the wind anomaly pattern regressed onto the Uruguay-mean temperature index.

---

## Usage

Run the full analysis pipeline:

```bash
python src/anomalies.py --variable tmp --baseline 1980 2014
python src/metrics.py --models cmip6 --output outputs/metrics_cmip6.csv
python src/trends.py --variable ua va --level 1000
python src/visualize.py --mode all
```

Or execute interactively via the provided notebooks in `notebooks/`.

---

## Data Sources

| Dataset | Version | Resolution | Reference |
|---|---|---|---|
| CRU TS | 4.07 | 0.5° × 0.5° | Harris et al. (2020) |
| CMIP5 | — | ~1°–2° | Taylor et al. (2012) |
| CMIP6 | — | ~0.25°–1° | Eyring et al. (2016) |
| Uruguay Shapefiles | IGM/INE 2023 | — | Instituto Geográfico Militar |

---

## Dependencies

| Package | Purpose |
|---|---|
| `netCDF4` | NetCDF4 file I/O and variable slicing |
| `numpy` | Vectorized array operations and masking |
| `scipy` | Spatial interpolation, statistical routines |
| `iris` | CF-convention cube handling and regridding |
| `cartopy` | Geospatial projections and map rendering |
| `matplotlib` | Base plotting backend |
| `geopandas` | Shapefile ingestion and rasterization |
| `pandas` | Tabular metric aggregation and export |

---

## Citation

If you use this code in published research, please cite this repository:

```
Arizmendi, F. (2024). uy-climate-projections: Uruguay Climate Change Projections &
Variability Analysis [Software]. GitHub.
https://github.com/ferariz/uy-climate-projections
```

---

## Contact

**Fernando Arizmendi, PhD**
Senior AI Engineer · Climate Scientist
📍 Montevideo, Uruguay
🔗 [GitHub](https://github.com/ferariz) · [LinkedIn](https://linkedin.com/in/fernando-arizmendi)
📧 <arizmendi.f@gmail.com>

---

## License

This project is licensed under the MIT License — see [`LICENSE`](LICENSE) for details.
