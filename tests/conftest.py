from io import StringIO
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from hydromt_sfincs import SfincsModel

import coastal_tools as coast


@pytest.fixture
def lower_colorado_stofs_points():
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
    4,-96.01858,28.61247
    5,-95.99234,28.57649
    6,-95.94361,28.59862
    7,-95.92857,28.64843"""

    return pd.read_csv(StringIO(data))

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
def lower_colorado_base_sfincs_model(lower_colorado_data_catalogs, lower_colorado_predefined_grid, lower_colorado_depth_definition, tmp_path):
    """Creates a base model for the Lower Colorado River test case"""
    sf = coast.initialize_sfincs_model(
        str(tmp_path),
        lower_colorado_data_catalogs,
        lower_colorado_predefined_grid,
        lower_colorado_depth_definition
    )
    return sf

@pytest.fixture
def lower_colorado_terminal_node() -> str:
    """The terminal node for the Lower Colorado River test case"""
    return "tnx-1000006230"

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
