from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr

import coastal_tools as coast


def test_lower_colorado_sfincs_setup(
    tmp_path: Path,
    lower_colorado_data_catalogs: list[str],
    lower_colorado_depth_definition: list[dict[str, int | str | float]],
    lower_colorado_predefined_grid: dict[str, int],
    lower_colorado_divides: gpd.GeoDataFrame,
    lower_colorado_nexus_points: gpd.GeoDataFrame,
    lower_colorado_terminal_node: str,
    lower_colorado_flowpaths: gpd.GeoDataFrame,
    lower_colorado_flowpath_attributes: gpd.GeoDataFrame,
    lower_colorado_start_time: np.datetime64,
    lower_colorado_end_time: np.datetime64,
    lower_colorado_stofs_points: pd.DataFrame,
    lower_colordao_boundary_forcings: xr.Dataset,
    lower_colorado_meterological_forcings: xr.Dataset,
    lower_colorado_cross_sections: pd.DataFrame
):

    try:
        sf = coast.initialize_sfincs_model(
            str(tmp_path),
            lower_colorado_data_catalogs,
            lower_colorado_predefined_grid,
            lower_colorado_depth_definition,
        )
    except FileNotFoundError as e:
        pytest.fail(f"Failed to initialize SFINCS model: {str(e)}")
    try:
        sf = coast.add_hydrofabric_outflow(
            sf,
            lower_colorado_divides,
            lower_colorado_nexus_points,
            lower_colorado_terminal_node)
    except FileNotFoundError as e:
        pytest.fail(f"Failed to add hydrofabric outflow: {str(e)}")
    try:
        sf.setup_river_inflow(
            rivers=lower_colorado_flowpaths, keep_rivers_geom=True
        )
    except FileNotFoundError as e:
        pytest.fail(f"Failed to add river inflow: {str(e)}")
    try:
        sf = coast.setup_subgrid(
            sf,
            lower_colorado_depth_definition,
            lower_colorado_flowpath_attributes,
        )
    except FileNotFoundError as e:
        pytest.fail(f"Failed to setup subgrid: {str(e)}")
    try:
        sf = coast.setup_water_level_boundaries(
            sf,
            lower_colorado_start_time,
            lower_colorado_end_time,
            lower_colorado_stofs_points,
            lower_colordao_boundary_forcings,
        )
    except ValueError as e:
        pytest.fail(f"Failed to setup water level boundaries: {str(e)}")
    sf = coast.setup_meterological_forcings(
        sf,
        lower_colorado_meterological_forcings
    )
    sf = coast.setup_observational_cross_sections(
        sf,
        lower_colorado_cross_sections,
    )
