"""Metropolitan area functions"""

__author__ = "Kyle Walker <kyle@walker-data.com"

from pygris.helpers import load_tiger

def core_based_statistical_areas(cb = False, resolution = "500k", year = None, cache = False):
    """
    Load a core-based statistical areas shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    cb: If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

    resolution: The resolution of the cartographic boundary file; only applies if 
                the cb argument is set to True. The default is "500k"; options also
                include "5m" (1:5 million) and "20m" (1:20 million)
    
    year: The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
          defaults to 2021.

    cache: If True, the function will download a Census shapefile to a cache directory 
           on the user's computer for future access.  If False, the function will load
           the shapefile directly from the Census website.  

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of core-based statistical areas


    Notes
    ----------
    Core-based statistical areas include metropolitan and micropolitan statistical areas.  
    See https://www.census.gov/programs-surveys/metro-micro.html for more information. 


    """
    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if resolution not in ["500k", "5m", "20m"]:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")

    if year == 2022:
        raise ValueError("CBSAs for 2022 are not yet defined due to the re-organization of counties in Connecticut.")
    
    if cb:
        if year == 2010:
            if resolution == "5m":
                raise ValueError("`resolution = '5m' is unavailable for 2010.")
            
            url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_us_310_m1_{resolution}.zip"
        else:
            if year == 2013:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_cbsa_{resolution}.zip"
            else:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_cbsa_{resolution}.zip"
    else:
        if year == 2010:
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/CBSA/2010/tl_2010_us_cbsa10.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CBSA/tl_{year}_us_cbsa.zip"
    
    return load_tiger(url, cache = cache)


def urban_areas(cb = False, year = None, cache = False):
    """
    Load a urbanized areas shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    cb: If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).
    
    year: The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
          defaults to 2021.

    cache: If True, the function will download a Census shapefile to a cache directory 
           on the user's computer for future access.  If False, the function will load
           the shapefile directly from the Census website.  

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of urbanized areas


    Notes
    ----------
    Urbanized areas are not yet defined for 2020; shapefiles use the old 2010 definitions.
    See https://www.census.gov/programs-surveys/geography/guidance/geo-areas/urban-rural.html for more information. 


    """
    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if cb:
        if year == 2013:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_ua10_500k.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_ua10_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/UAC/tl_{year}_us_uac10.zip"
    
    return load_tiger(url, cache = cache)


def combined_statistical_areas(cb = False, resolution = "500k", year = None, cache = False):
    """
    Load a combined statistical areas shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    cb: If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

    resolution: The resolution of the cartographic boundary file; only applies if 
                the cb argument is set to True. The default is "500k"; options also
                include "5m" (1:5 million) and "20m" (1:20 million)
    
    year: The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
          defaults to 2021.

    cache: If True, the function will download a Census shapefile to a cache directory 
           on the user's computer for future access.  If False, the function will load
           the shapefile directly from the Census website.  

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of urbanized areas


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information. 


    """
    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if resolution not in ["500k", "5m", "20m"]:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")
    
    if cb:
        if year == 2013:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_csa_{resolution}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_csa_{resolution}.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CSA/tl_{year}_us_csa.zip"
    
    return load_tiger(url, cache = cache)


def metro_divisions(cb = False, resolution = "500k", year = None, cache = False):
    """
    Load a metropolitan divisions shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    cb: If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

    resolution: The resolution of the cartographic boundary file; only applies if 
                the cb argument is set to True. The default is "500k"; options also
                include "5m" (1:5 million) and "20m" (1:20 million)
    
    year: The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
          defaults to 2021.

    cache: If True, the function will download a Census shapefile to a cache directory 
           on the user's computer for future access.  If False, the function will load
           the shapefile directly from the Census website.  

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of metropolitan divisions


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information. 


    """
    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if resolution not in ["500k", "5m", "20m"]:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")

    if year == 2022:
        raise ValueError("Metropolitan divisions for 2022 are not yet defined due to the re-organization of counties in Connecticut.")
    
    if cb:
        if year == 2013:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_metdiv_{resolution}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_metdiv_{resolution}.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CBSA/tl_{year}_us_metdiv.zip"
    
    return load_tiger(url, cache = cache)


def new_england(type = "necta", cb = False, year = None, cache = False):
    """
    Load a metropolitan divisions shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    cb: If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

    resolution: The resolution of the cartographic boundary file; only applies if 
                the cb argument is set to True. The default is "500k"; options also
                include "5m" (1:5 million) and "20m" (1:20 million)
    
    year: The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
          defaults to 2021.

    cache: If True, the function will download a Census shapefile to a cache directory 
           on the user's computer for future access.  If False, the function will load
           the shapefile directly from the Census website.  

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of metropolitan divisions


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information. 


    """
    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if type == "necta":
        if cb:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_necta_500k.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/NECTA/tl_{year}_us_necta.zip"

        return load_tiger(url, cache = cache)

    elif type == "combined":
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CNECTA/tl_{year}_us_cnecta.zip"

        return load_tiger(url, cache = cache)

    elif type == "divisions":
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/NECTADIV/tl_{year}_us_nectadiv.zip"

        return load_tiger(url, cache = cache)

    else:
        raise ValueError("Invalid NECTA type; valid values include 'necta' (the default), 'combined', and 'divisions'.")