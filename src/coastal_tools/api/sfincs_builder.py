import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from hydromt_sfincs import SfincsModel, utils
from shapely.geometry import LineString

__all__ = [
    "initialize_sfincs_model",
    "setup_subgrid",
    "add_hydrofabric_outflow",
    "setup_meterological_forcings",
    "setup_water_level_boundaries",
    "setup_observational_cross_sections"
]


def initialize_sfincs_model(
    root: str,
    data_catalog_definition: list[str],
    grid_definition: dict[str, int],
    depth_definition: list[dict[str, int | str | float]],
) -> SfincsModel:
    """A fucntion to initialize a SFINCS model given a data catalog and depth definition

    Parameters
    ----------
    root : str
        The root path to where SFINCS will write its output
    data_catalog_definition : list[str]
        A list of data catalogs to be used in the SFINCS model
    grid_definition : dict[str, int]
        A predefined grid for the SFINCS model
    depth_definition : list[dict[str, int  |  str  |  float]]
        A list of dictionaries that define the depth of the model

    Returns
    -------
    SfincsModel
        An initialized SFINCS model
    """
    sf = SfincsModel(data_libs=data_catalog_definition, root=root, mode="w+")
    sf.setup_grid(**grid_definition)
    sf.setup_dep(datasets_dep=depth_definition)
    sf.setup_mask_active(zmin=0.3, reset_mask=True)
    return sf


def add_hydrofabric_outflow(
    sf: SfincsModel,
    divides: gpd.GeoDataFrame,
    nexus: gpd.GeoDataFrame,
    terminal_node: str,
) -> SfincsModel:
    """Adds outflow nodes to the SFINCS model

    Parameters
    ----------
    sf : SfincsModel
        A base SFINCS model object with a defined grid
    divides : gpd.GeoDataFrame
        the divides of the hydrofabric
    nexus : gpd.GeoDataFrame
        the nexus points of the hydrofabric
    terminal_node : str
        the terminal node of the hydrofabric that will be the outflow into the ocean

    Returns
    -------
    SfincsModel
        An updated SFINCS model with the outflow nodes added
    """
    terminal_nexus = nexus[nexus["id"] == terminal_node]
    include_mask = gpd.GeoDataFrame({
        "id": pd.concat([terminal_nexus["id"], divides["id"]]),
        "geometry": pd.concat([terminal_nexus["geometry"], divides["geometry"].to_crs(terminal_nexus.crs)]),
    })
    sf.setup_mask_bounds(btype="waterlevel", include_mask=include_mask, reset_bounds=True, zmax=0)
    return sf

def setup_subgrid(
    sf: SfincsModel,
    depth_definition: list[dict[str, int | str | float]],
    flowpath_attributes: gpd.GeoDataFrame,
) -> SfincsModel:
    """A wrapper function to set up subgrid definitions using the hydrofabric flowpath attributes

    Parameters
    ----------
    sf : SfincsModel
        The base SFINCS model object
    flowpath_attributes : gpd.GeoDataFrame
        the flowpath attributes of the hydrofabric

    Returns
    -------
    SfincsModel
        the updated SFCINS model with the subgrid definitions added
    """
    gdf_riv = sf.geoms["rivers_inflow"].copy()
    attr = flowpath_attributes[flowpath_attributes["id"] == gdf_riv["id"].values[0]]
    gdf_riv["rivwth"] = attr["TopWdth"].values # width [m]
    gdf_riv["manning"] = attr["n"].values  # manning coefficient [s.m-1/3]
    gdf_riv["rivdph"] = attr["Y"].values # depth [m]
    gdf_riv[["geometry", "rivwth","rivdph" , "manning"]]
    datasets_riv = [{"centerlines": gdf_riv}]
    gdf_riv_buf = gdf_riv.assign(geometry=gdf_riv.buffer(gdf_riv['rivwth']/2))
    da_manning = sf.grid.raster.rasterize(gdf_riv_buf, "manning", nodata=np.nan)

    datasets_rgh = [{"manning": da_manning}]

    sf.setup_subgrid(
        datasets_dep=depth_definition,
        datasets_rgh=datasets_rgh,
        datasets_riv=datasets_riv,
        nr_subgrid_pixels=5,
        write_dep_tif=True,
        write_man_tif=False,
    )
    return sf

def setup_water_level_boundaries(
    sf: SfincsModel,
    start_time: np.datetime64,
    end_time: np.datetime64,
    boundary_points: pd.DataFrame,
    boundary_forcings: xr.Dataset,
) -> SfincsModel:
    """A function to define the water level forcings and boundaries for the SFINCS model

    Parameters
    ----------
    sf : SfincsModel
        A base SFINCS model object
    start_time : np.datetime64
        The start time of the water level boundary
    end_time : np.datetime64
        The end time of the water level boundary
    boundary_points : pd.DataFrame
        A DataFrame containing the boundary points
    boundary_forcings : xr.Dataset
        An xarray dataset containing the boundary forcings

    Returns
    -------
    SfincsModel
        An updated SFINCS model with the water level boundaries
    """
    sf.setup_config(
        tref=pd.Timestamp(start_time).strftime('%Y%m%d %H%M%S'),
        tstart=pd.Timestamp(start_time).strftime('%Y%m%d %H%M%S'),
        tstop=pd.Timestamp(end_time).strftime('%Y%m%d %H%M%S'),
    )
    pnts = gpd.points_from_xy(boundary_points["Lon"], boundary_points["Lat"])
    index = list(range(len(boundary_points)))
    bnd = gpd.GeoDataFrame(index=index, geometry=pnts, crs="EPSG:4326").to_crs(epsg=3857)
    bnd.index = bnd.index + 1

    start_time_seconds = boundary_forcings.time.attrs["start_time"]
    org_time = boundary_forcings.time.values
    adjusted_time = pd.to_datetime(boundary_forcings.time.values) + pd.Timedelta(seconds=start_time_seconds)

    adjusted_time_np = np.array(adjusted_time, dtype='datetime64[ns]')
    start_idx = np.where(adjusted_time_np == start_time)[0]
    stop_idx = np.where(adjusted_time_np == end_time)[0]

    stofs_filtered = boundary_forcings.sel(time=slice(org_time[start_idx][0], org_time[stop_idx][0]))
    bzs = stofs_filtered.time_series.values.squeeze()

    time = pd.date_range(
        start=utils.parse_datetime(pd.Timestamp(boundary_forcings.time.values[0]).to_pydatetime()),
        end=utils.parse_datetime(pd.Timestamp(boundary_forcings.time.values[-1]).to_pydatetime()),
        periods=bzs.shape[0],
    )

    bzspd = pd.DataFrame(index=time.values, columns=index, data=bzs)
    sf.set_forcing_1d(df_ts=bzspd, gdf_locs=bnd)
    return sf

def setup_meterological_forcings(
    sf: SfincsModel,
    forcings: xr.Dataset,
) -> SfincsModel:
    """A function to set up the meteorological forcings for the SFINCS model

    Parameters
    ----------
    sf : SfincsModel
        The base SFINCS model object
    forcings : xr.Dataset
        The meteorological forcings
    """
    ds: xr.Dataset = sf.data_catalog.get_rasterdataset(
        forcings,
        bbox=[
            forcings.lon.values.min(),
            forcings.lat.values.min(),
            forcings.lon.values.max(),
            forcings.lat.values.max()
        ],
        buffer=100,  # Add buffer in pixels
        variables=["precip"],
        geom=sf.region,
        meta={"version": "1"},
    ) # type: ignore
    sf.set_forcing(data=ds, name='precip')
    return sf

def setup_observational_cross_sections(
    sf: SfincsModel,
    cross_sections: pd.DataFrame,
    crs: str = "5070",
) -> SfincsModel:
    """A function to set up observational cross sections for the SFINCS model

    Parameters
    ----------
    sf : SfincsModel
        The base SFINCS model object
    cross_sections : pd.DataFrame
        A DataFrame containing the observational cross sections
    crs : str
        The coordinate reference system of the cross sections

    Returns
    -------
    SfincsModel
        An updated SFINCS model with the observational cross sections
    """
    lines = []
    attributes = []

    for cs_id, group in cross_sections.groupby('cs_id'):
        group = group.sort_values('relative_distance')

        # inside of the cross-section data from Lynker-Spatial the point data is defined via X and Y coordinates
        line = LineString(zip(group['X'].values, group['Y'].values, strict=False))
        attr = {
            'cs_id': cs_id,
            'name': f"CS_{cs_id}",
            'length': group['cs_lengthm'].iloc[0],
            'Z_min': group['Z'].min()
        }

        lines.append(line)
        attributes.append(attr)

    gdf = gpd.GeoDataFrame(attributes)
    gdf['geometry'] = lines
    gdf = gdf.set_crs(epsg=crs, inplace=True)
    sf.setup_observation_lines(
        locations=gdf, merge=True
    )
    return sf
