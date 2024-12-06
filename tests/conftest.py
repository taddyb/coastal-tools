from io import StringIO
from pathlib import Path

import pandas as pd
import pytest


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
def lynker_data_catalog_path():
    """
    Pytest fixture that returns the path to the Lynker-Spatial data catalog

    Returns
    -------
    str
        Path to the Lynker data catalog
    """
    return Path(__file__).parents[1] / "data/data_catalogs/lynker_spatial/gridded_data.yaml"

@pytest.fixture
def nos_data_catalog_path():
    """
    Pytest fixture that returns the path to the NOS coatal topobathymetry data catalog

    Returns
    -------
    str
        Path to the NOS data catalog
    """
    return Path(__file__).parents[1] / "data/data_catalogs/nos/coastal_lidar.yaml"
