from pathlib import Path

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


def _get_predefined_data_catalogs(data_dir) -> list[str]:
    ngei_lib = data_dir / "nos/coastal_lidar.yml"
    lynker_lib = data_dir / "lynker_spatial/gridded_data.yml"
    return [
        ngei_lib,
        lynker_lib
    ]
    
def _get_predefined_grid() -> dict[str, int]:    
    # TODO replace with zarr store
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
    
def _get_predefined_depth() -> list[dict[str, int | str | float]]:
    # TODO replace with zarr store
    return [
        {"elevtn": "dem", "zmin": 0.1, "zmax":25},
        {"elevtn": "USGS_seamless_13"},
    ]
  
def initialize_sfincs_model(
    root: str,
    flowpath_id: str | None = None,
) -> SfincsModel:
    data_dir = Path(__file__).parents[3] / "data/data_catalogs"
    predefined_catalogs = _get_predefined_data_catalogs(data_dir)
    sf = SfincsModel(data_libs=predefined_catalogs, root=root, mode="w+")
    input_data = _get_predefined_grid()
    sf.setup_grid(**input_data)
    depth_datasets = _get_predefined_depth()
    sf.setup_dep(datasets_dep=depth_datasets)
    sf.setup_mask_active(zmin=0.3, reset_mask=True)
    return sf


def add_hydrofabric_outflow(
    sf: SfincsModel,
    divides: gpd.GeoDataFrame,
    nexus: gpd.GeoDataFrame,
    terminal_node: str = "tnx-1000006230",
):
    terminal_nexus = nexus[nexus["id"] == terminal_node]
    include_mask = gpd.GeoDataFrame({
        "id": pd.concat([terminal_nexus["id"], divides["id"]]),
        "geometry": pd.concat([terminal_nexus["geometry"], divides["geometry"].to_crs(terminal_nexus.crs)]),
    })
    sf.setup_mask_bounds(btype="waterlevel", include_mask=include_mask, reset_bounds=True, zmax=0)
    return sf

def setup_subgrid(
    sf: SfincsModel,
    flowpath_attributes: gpd.GeoDataFrame,
):
    gdf_riv = sf.geoms["rivers_inflow"].copy()
    attr = flowpath_attributes[flowpath_attributes["id"] == gdf_riv["id"].values[0]]
    attr.columns
    gdf_riv["rivwth"] = attr["TopWdth"].values # width [m]
    gdf_riv["manning"] = attr["n"].values  # manning coefficient [s.m-1/3]
    gdf_riv["rivdph"] = attr["Y"].values # depth [m]
    gdf_riv[["geometry", "rivwth","rivdph" , "manning"]]
    # gdf_riv = sf.geoms["rivers_inflow"].copy()
    # flowpath_attributes[flowpath_attributes["id"] == gdf_riv["id"]]
    datasets_riv = [{"centerlines": gdf_riv}]
    gdf_riv_buf = gdf_riv.assign(geometry=gdf_riv.buffer(gdf_riv['rivwth']/2))
    da_manning = sf.grid.raster.rasterize(gdf_riv_buf, "manning", nodata=np.nan)

    datasets_rgh = [{"manning": da_manning}]

    sf.setup_subgrid(
        datasets_dep=_get_predefined_depth(),
        datasets_rgh=datasets_rgh,
        datasets_riv=datasets_riv,
        nr_subgrid_pixels=5,
        write_dep_tif=True,
        write_man_tif=False,
    )
    return sf

def setup_water_level_boundaries(
    sf: SfincsModel,
    start_time,
    end_time,
    boundary_points = pd.DataFrame,
    boundary_forcings = xr.Dataset,
):
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

    # and the actual water levels, in this case for input location 1 a water level rising from 0 to 2 meters and back to 0:
    bzspd = pd.DataFrame(index=time.values, columns=index, data=bzs)
    sf.set_forcing_1d(df_ts=bzspd, gdf_locs=bnd)
    return sf

def setup_meterological_forcings(
    sf: SfincsModel,
    forcings: xr.Dataset,
):
    ds = sf.data_catalog.get_rasterdataset(
        forcings,
        bbox=[
            _ds.lon.values.min(),
            _ds.lat.values.min(),
            _ds.lon.values.max(),
            _ds.lat.values.max()
        ],
        buffer=100,  # Add buffer in pixels
        variables=["precip"],
        geom=sf.region,
        meta={"version": "1"},
    )
    sf.set_forcing(data=ds, name='precip')
    
def setup_observational_cross_sections(
    sf: SfincsModel,
    df: pd.DataFrame,
    terminal_catchment: str = "wb-2430687",
):
    mask = df["id"] == terminal_catchment
    local_cross_sections = df[mask]

    lines = []
    attributes = []

    for cs_id, group in local_cross_sections.groupby('cs_id'):
        group = group.sort_values('relative_distance')
        line = LineString(zip(group['X'].values, group['Y'].values))
        attr = {
            'cs_id': cs_id,
            'name': f"CS_{cs_id}", 
            'length': group['cs_lengthm'].iloc[0],
            'Z_min': group['Z'].min() 
        }

        lines.append(line)
        attributes.append(attr)

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(attributes, geometry=lines)

    # Set CRS - assuming your coordinates are in meters
    # You'll need to set the correct EPSG code for your data
    gdf = gdf.set_crs(epsg="5070", inplace=True)
    sf.setup_observation_lines(
        locations=gdf, merge=True
    )
