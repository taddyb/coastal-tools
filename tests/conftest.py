from io import StringIO
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr


@pytest.fixture
def lower_colorado_stofs_points() -> pd.DataFrame:
    """
    Pytest fixture that returns a DataFrame containing STOFS lon/lat coordinate data

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns:
        - ref_id: Reference point identifier
        - Lon: Longitude coordinate
        - Lat: Latitude coordinate
    """
    data = """ref_id,Lon,Lat
    1,-96.22029,28.57183
    2,-96.15505,28.58662
    3,-96.07669,28.61743
    4,-96.01858,28.61247
    5,-95.99234,28.57649
    6,-95.94361,28.59862
    7,-95.92857,28.64843
    8,-95.91665,28.69935"""

    return pd.read_csv(StringIO(data))

@pytest.fixture
def lower_colorado_start_time() -> np.datetime64:
    """The start time for the Lower Colorado River test case"""
    return np.datetime64('2023-04-01T01:00:00.000000000')

@pytest.fixture
def lower_colorado_end_time() -> np.datetime64:
    """The start time for the Lower Colorado River test case"""
    return np.datetime64('2023-04-03T00:00:00.000000000')

@pytest.fixture
def lower_colordao_boundary_forcings() -> xr.Dataset:
    """The boundary forcings for the Lower Colorado River test case"""
    forcing_path = Path(__file__).parent / "data/20230401_stofs_elev2D.th.nc"
    return xr.open_dataset(forcing_path)

@pytest.fixture
def lower_colorado_meterological_forcings() -> xr.Dataset:
    """The formatted meterological forcings for the Lower Colorado River test case"""
    forcing_path = Path(__file__).parent / "data/sflux_air_1.0001.nc"
    ds = xr.open_dataset(forcing_path)
    ds = ds.rio.write_crs("EPSG:4326", inplace=True)
    ds.raster.set_spatial_dims(x_dim="nx_grid", y_dim="ny_grid")
    ds = ds.rename({"rain": "precip"})
    return ds

@pytest.fixture
def lower_colorado_depth_definition() -> list[dict[str, int | str | float]]:
    """A sample depth definition for the Lower Colorado River"""
    return [
        {"elevtn": "dem", "zmin": 0.1, "zmax":25},
        {"elevtn": "USGS_seamless_13"},
    ]

@pytest.fixture
def lynker_data_catalog_path() -> str:
    """Pytest fixture that returns the path to the Lynker-Spatial data catalog"""
    return str(Path(__file__).parents[1] / "data/data_catalogs/lynker_spatial/gridded_data.yaml")

@pytest.fixture
def nos_data_catalog_path() -> str:
    """Pytest fixture that returns the path to the NOS coatal topobathymetry data catalog"""
    return str(Path(__file__).parents[1] / "data/data_catalogs/nos/coastal_lidar.yaml")

@pytest.fixture
def lower_colorado_data_catalogs(nos_data_catalog_path, lynker_data_catalog_path) -> list[str]:
    """A List of the data catalogs used for the Lower Colorado River test case"""
    return [
        nos_data_catalog_path,
        lynker_data_catalog_path
    ]

@pytest.fixture
def lower_colorado_predefined_grid() -> dict[str, int]:
    """A predefined grid for the Lower Colorado River test case"""
    return {
        "x0":-10687089,
        "y0":3321498,
        "dy":50,
        "dx":50,
        "nmax":150,
        "mmax":250,
        "rotation":24,
        "epsg":3857,
    }

@pytest.fixture
def lower_colorado_terminal_node() -> str:
    """The terminal node for the Lower Colorado River test case"""
    return "tnx-1000006230"

@pytest.fixture
def lower_colorado_terminal_watershed_boundary() -> str:
    """The terminal watershed boundary for the Lower Colorado River test case"""
    return "wb-2430687"

@pytest.fixture
def lower_colorado_cross_sections() -> pd.DataFrame:
    """The local cross sections for the Lower Colorado River test case"""
    cross_section_path = Path(__file__).parent / "data/lower_colorado_cross_sections.parquet"
    return pd.read_parquet(cross_section_path)

@pytest.fixture
def lower_colorado_path() -> Path:
    """The path to the Lower Colorado River test case"""
    return Path(__file__).parent / "data/lower_colorado_v22.gpkg"

@pytest.fixture
def lower_colorado_nexus_points(lower_colorado_path) -> gpd.GeoDataFrame:
    """The nexus points for the Lower Colorado River test case"""
    return gpd.read_file(lower_colorado_path, layer="nexus")

@pytest.fixture
def lower_colorado_divides(lower_colorado_path) -> gpd.GeoDataFrame:
    """The catchment divides for the Lower Colorado River test case"""
    return gpd.read_file(lower_colorado_path, layer="nexus")

@pytest.fixture
def lower_colorado_flowpaths(lower_colorado_path) -> gpd.GeoDataFrame:
    """The flowpaths for the Lower Colorado River test case"""
    return gpd.read_file(lower_colorado_path, layer="flowpaths")

@pytest.fixture
def lower_colorado_flowpath_attributes(lower_colorado_path) -> gpd.GeoDataFrame:
    """The flowpath attributes for the Lower Colorado River test case"""
    return gpd.read_file(lower_colorado_path, layer="flowpath-attributes-ml")
