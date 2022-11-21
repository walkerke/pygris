"""Transportation dataset functions"""

__author__ = "Kyle Walker <kyle@walker-data.com"

from .helpers import _load_tiger, validate_state, validate_county, fips_codes
import pandas as pd

def roads(state, county, year = None, cache = False, subset_by = None):

    """
    Load a roads shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str 
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
    county : str or list
        The county name or three-digit FIPS code of the desired county, or a list of such counties. 
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. 
    cache : bool 
        If True, the function will download a Census shapefile to a cache directory 
        on the user's computer for future access.  If False, the function will load
        the shapefile directly from the Census website.      
    subset_by : tuple, int, slice, dict, geopandas.GeoDataFrame, or geopandas.GeoSeries
        An optional directive telling pygris to return a subset of data using 
        underlying arguments in geopandas.read_file().  
        subset_by operates as follows:
            * If a user supplies a tuple of format (minx, miny, maxx, maxy), 
            it will be interpreted as a bounding box and rows will be returned
            that intersect that bounding box;
            * If a user supplies a integer or a slice object, the first n rows
            (or the rows defined by the slice object) will be returned;
            * If a user supplies an object of type geopandas.GeoDataFrame
            or of type geopandas.GeoSeries, rows that intersect the input 
            object will be returned. CRS misalignment will be resolved 
            internally.  
            * A dict of format {"address": "buffer_distance"} will return rows
            that intersect a buffer of a given distance (in meters) around an 
            input address.  
    
    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of roads.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information.
    
    """

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    state = validate_state(state)

    if type(county) is list:
        valid_county = [validate_county(state, x) for x in county]

        county_roads = []     
        
        for i in valid_county:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ROADS/tl_{year}_{state}{i}_roads.zip"
            r = _load_tiger(url, cache = cache, subset_by = subset_by)
            county_roads.append(r)
        
        all_r = pd.concat(county_roads, ignore_index = True)

        return all_r


    else:
        valid_county = validate_county(state, county)
    
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ROADS/tl_{year}_{state}{valid_county}_roads.zip"
        r = _load_tiger(url, cache = cache, subset_by = subset_by)

        return r


def primary_roads(year = None, cache = False, subset_by = None):

    """
    Load a primary roads shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. 
    cache : bool 
        If True, the function will download a Census shapefile to a cache directory 
        on the user's computer for future access.  If False, the function will load
        the shapefile directly from the Census website.      
    subset_by : tuple, int, slice, dict, geopandas.GeoDataFrame, or geopandas.GeoSeries
        An optional directive telling pygris to return a subset of data using 
        underlying arguments in geopandas.read_file().  
        subset_by operates as follows:
            * If a user supplies a tuple of format (minx, miny, maxx, maxy), 
            it will be interpreted as a bounding box and rows will be returned
            that intersect that bounding box;
            * If a user supplies a integer or a slice object, the first n rows
            (or the rows defined by the slice object) will be returned;
            * If a user supplies an object of type geopandas.GeoDataFrame
            or of type geopandas.GeoSeries, rows that intersect the input 
            object will be returned. CRS misalignment will be resolved 
            internally.  
            * A dict of format {"address": "buffer_distance"} will return rows
            that intersect a buffer of a given distance (in meters) around an 
            input address.  
    
    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of primary roads.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information.
    
    """

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/PRIMARYROADS/tl_{year}_us_primaryroads.zip"
    r = _load_tiger(url, cache = cache, subset_by = subset_by)

    return r


def primary_secondary_roads(state, year = None, cache = False, subset_by = None):

    """
    Load a primary & secondary roads shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str 
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. 
    cache : bool 
        If True, the function will download a Census shapefile to a cache directory 
        on the user's computer for future access.  If False, the function will load
        the shapefile directly from the Census website.      
    subset_by : tuple, int, slice, dict, geopandas.GeoDataFrame, or geopandas.GeoSeries
        An optional directive telling pygris to return a subset of data using 
        underlying arguments in geopandas.read_file().  
        subset_by operates as follows:
            * If a user supplies a tuple of format (minx, miny, maxx, maxy), 
            it will be interpreted as a bounding box and rows will be returned
            that intersect that bounding box;
            * If a user supplies a integer or a slice object, the first n rows
            (or the rows defined by the slice object) will be returned;
            * If a user supplies an object of type geopandas.GeoDataFrame
            or of type geopandas.GeoSeries, rows that intersect the input 
            object will be returned. CRS misalignment will be resolved 
            internally.  
            * A dict of format {"address": "buffer_distance"} will return rows
            that intersect a buffer of a given distance (in meters) around an 
            input address.  
    
    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of primary and secondary roads.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information.
    
    """

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    state = validate_state(state)
    
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/PRISECROADS/tl_{year}_{state}_prisecroads.zip"

    r = _load_tiger(url, cache = cache, subset_by = subset_by)

    return r


def rails(year = None, cache = False, subset_by = None):

    """
    Load a railroads shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. 
    cache : bool 
        If True, the function will download a Census shapefile to a cache directory 
        on the user's computer for future access.  If False, the function will load
        the shapefile directly from the Census website.      
    subset_by : tuple, int, slice, dict, geopandas.GeoDataFrame, or geopandas.GeoSeries
        An optional directive telling pygris to return a subset of data using 
        underlying arguments in geopandas.read_file().  
        subset_by operates as follows:
            * If a user supplies a tuple of format (minx, miny, maxx, maxy), 
            it will be interpreted as a bounding box and rows will be returned
            that intersect that bounding box;
            * If a user supplies a integer or a slice object, the first n rows
            (or the rows defined by the slice object) will be returned;
            * If a user supplies an object of type geopandas.GeoDataFrame
            or of type geopandas.GeoSeries, rows that intersect the input 
            object will be returned. CRS misalignment will be resolved 
            internally.  
            * A dict of format {"address": "buffer_distance"} will return rows
            that intersect a buffer of a given distance (in meters) around an 
            input address.  
    
    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of railroads.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information.
    
    """

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/RAILS/tl_{year}_us_rails.zip"
    r = _load_tiger(url, cache = cache, subset_by = subset_by)

    return r


def address_ranges(state, county, year = None, cache = False, subset_by = None):

    """
    Load an address ranges shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str 
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
    county : str or list
        The county name or three-digit FIPS code of the desired county, or a list of such counties. 
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. 
    cache : bool 
        If True, the function will download a Census shapefile to a cache directory 
        on the user's computer for future access.  If False, the function will load
        the shapefile directly from the Census website.      
    subset_by : tuple, int, slice, dict, geopandas.GeoDataFrame, or geopandas.GeoSeries
        An optional directive telling pygris to return a subset of data using 
        underlying arguments in geopandas.read_file().  
        subset_by operates as follows:
            * If a user supplies a tuple of format (minx, miny, maxx, maxy), 
            it will be interpreted as a bounding box and rows will be returned
            that intersect that bounding box;
            * If a user supplies a integer or a slice object, the first n rows
            (or the rows defined by the slice object) will be returned;
            * If a user supplies an object of type geopandas.GeoDataFrame
            or of type geopandas.GeoSeries, rows that intersect the input 
            object will be returned. CRS misalignment will be resolved 
            internally.  
            * A dict of format {"address": "buffer_distance"} will return rows
            that intersect a buffer of a given distance (in meters) around an 
            input address.  
    
    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of address ranges.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information.
    
    """

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    state = validate_state(state)

    if type(county) is list:
        valid_county = [validate_county(state, x) for x in county]

        county_ranges = []     
        
        for i in valid_county:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ADDRFEAT/tl_{year}_{state}{i}_addrfeat.zip"
            r = _load_tiger(url, cache = cache, subset_by = subset_by)
            county_ranges.append(r)
        
        all_r = pd.concat(county_ranges, ignore_index = True)

        return all_r


    else:
        valid_county = validate_county(state, county)
    
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ADDRFEAT/tl_{year}_{state}{valid_county}_addrfeat.zip"
        r = _load_tiger(url, cache = cache, subset_by = subset_by)

        return r