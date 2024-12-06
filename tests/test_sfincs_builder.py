from pathlib import Path

import geopandas as gpd
import pytest
from hydromt_sfincs import SfincsModel

import coastal_tools as coast


def test_initialize_sfincs_model(
    tmp_path: Path,
    lower_colorado_data_catalogs: list[str],
    lower_colorado_predefined_grid: dict[str, int],
    lower_colorado_depth_definition: list[dict[str, int | str | float]],
):
    """Testing the initialization of a SFINCS model

    Parameters
    ----------
    tmp_path : Path
        a tmp path to write SFINCS outputs to
    lower_colorado_data_catalogs : list[str]
        a list of data catalogs to be used in the SFINCS model
    lower_colorado_predefined_grid : dict[str, int]
        a predefined grid for the SFINCS model
    lower_colorado_depth_definition : list[dict[str, int  |  str  |  float]]
        a list of dictionaries that define the depth of the model
    """
    try:
        _ = coast.initialize_sfincs_model(
            str(tmp_path),
            lower_colorado_data_catalogs,
            lower_colorado_predefined_grid,
            lower_colorado_depth_definition,
        )
    except FileNotFoundError as e:
        pytest.fail(f"Failed to initialize SFINCS model: {str(e)}")


def test_add_hydrofabric_outflow(
    lower_colorado_base_sfincs_model: SfincsModel,
    lower_colorado_divides: gpd.GeoDataFrame,
    lower_colorado_nexus_points: gpd.GeoDataFrame,
    lower_colorado_terminal_node: str,
):
    """Testing the addition of outflow nodes to a SFINCS model

    Parameters
    ----------
    lower_colorado_base_sfincs_model : SfincsModel
        a base SFINCS model object with a defined grid
    lower_colorado_divides : gpd.GeoDataFrame
        the divides of the hydrofabric
    lower_colorado_nexus_points : gpd.GeoDataFrame
        the nexus points of the hydrofabric
    lower_colorado_terminal_node : str
        the terminal node of the hydrofabric that will be the outflow into the ocean
    """
    try:
        _ = coast.add_hydrofabric_outflow(
            lower_colorado_base_sfincs_model,
            lower_colorado_divides,
            lower_colorado_nexus_points,
            lower_colorado_terminal_node)
    except FileNotFoundError as e:
        pytest.fail(f"Failed to add hydrofabric outflow: {str(e)}")
