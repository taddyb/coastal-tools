import hydromt
import pytest


def test_data_catalogs(
    nos_data_catalog_path,
    lynker_data_catalog_path,
):
    """Testing to ensure the data catalogs can be read through their YAML definitions

    Parameters
    ----------
    nos_data_catalog_path : str
        The path to the NOS data catalog
    lynker_data_catalog_path : str
        The path to the lynker-spatial data catalog
    """
    data_catalog = hydromt.DataCatalog(data_libs=[lynker_data_catalog_path, nos_data_catalog_path])
    try:
        _ = data_catalog.get_rasterdataset("dem")
        _ = data_catalog.get_rasterdataset("USGS_seamless_13")
        _ = data_catalog.get_rasterdataset("ncei_bathymetry")
    except FileNotFoundError as e:
        pytest.fail(f"Failed to initialize DataCatalog: {str(e)}")
