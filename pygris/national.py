"""National cartographic boundary file functions"""

__author__ = "Kyle Walker <kyle@walker-data.com"

from pygris.helpers import load_tiger

def regions(resolution = "500k", year = None, cache = False):
    """
    Load a US Census regions shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    resolution: The resolution of the cartographic boundary file; only applies if 
                the cb argument is set to True. The default is "500k"; options also
                include "5m" (1:5 million) and "20m" (1:20 million)
    
    year: The year of the cartographic boundary shapefile. If not specified,
          defaults to 2021.

    cache: If True, the function will download a Census shapefile to a cache directory 
           on the user's computer for future access.  If False, the function will load
           the shapefile directly from the Census website.  

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of US regions.
    """

    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if resolution not in ["500k", "5m", "20m"]:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")

    url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_region_{resolution}.zip"

    rgns = load_tiger(url, cache = cache)

    return rgns


def nation(resolution = "500k", year = None, cache = False):
    """
    Load a US national boundary shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    resolution: The resolution of the cartographic boundary file; only applies if 
                the cb argument is set to True. The default is "500k"; options also
                include "5m" (1:5 million) and "20m" (1:20 million)
    
    year: The year of the cartographic boundary shapefile. If not specified,
          defaults to 2021.

    cache: If True, the function will download a Census shapefile to a cache directory 
           on the user's computer for future access.  If False, the function will load
           the shapefile directly from the Census website.  

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of the US boundary.
    """

    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if resolution not in ["500k", "5m", "20m"]:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")

    url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_nation_{resolution}.zip"

    nat = load_tiger(url, cache = cache)

    return nat


def divisions(resolution = "500k", year = None, cache = False):
    """
    Load a US Census divisions shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    resolution: The resolution of the cartographic boundary file; only applies if 
                the cb argument is set to True. The default is "500k"; options also
                include "5m" (1:5 million) and "20m" (1:20 million)
    
    year: The year of the cartographic boundary shapefile. If not specified,
          defaults to 2021.

    cache: If True, the function will download a Census shapefile to a cache directory 
           on the user's computer for future access.  If False, the function will load
           the shapefile directly from the Census website.  

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of US Census divisions.
    """

    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if resolution not in ["500k", "5m", "20m"]:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")

    url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_division_{resolution}.zip"

    div = load_tiger(url, cache = cache)

    return div