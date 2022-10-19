"""Water and coastline functions"""

__author__ = "Kyle Walker <kyle@walker-data.com"

from .helpers import load_tiger, validate_state, validate_county, fips_codes
import pandas as pd
def area_water(state, county, year = None, cache = False, subset_by = None):
    """
    Load an area water shapefile into Python as a GeoDataFrame

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
    
    subset_by : tuple, int, slice, geopandas.GeoDataFrame, or geopandas.GeoSeries
        An optional directive telling pygris to return a subset of data using 
        underlying arguments in geopandas.read_file().  
        subset_by operates as follows:
            - If a user supplies a tuple of format (minx, miny, maxx, maxy), 
            it will be interpreted as a bounding box and rows will be returned
            that intersect that bounding box;

            - If a user supplies a integer or a slice object, the first n rows
            (or the rows defined by the slice object) will be returned;

            - If a user supplies an object of type geopandas.GeoDataFrame
            or of type geopandas.GeoSeries, rows that intersect the input 
            object will be returned. CRS misalignment will be resolved 
            internally.  
    
    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of water areas.


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

        county_water = []     
        
        for i in valid_county:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/AREAWATER/tl_{year}_{state}{i}_areawater.zip"
            w = load_tiger(url, cache = cache, subset_by = subset_by)
            county_water.append(w)
        
        all_w = pd.concat(county_water, ignore_index = True)

        return all_w


    else:
        valid_county = validate_county(state, county)
    
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/AREAWATER/tl_{year}_{state}{valid_county}_areawater.zip"
        w = load_tiger(url, cache = cache, subset_by = subset_by)

        return w

    

def linear_water(state, county, year = None, cache = False, subset_by = None):
    """
    Load a linear water shapefile into Python as a GeoDataFrame

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
    
    subset_by : tuple, int, slice, geopandas.GeoDataFrame, or geopandas.GeoSeries
        An optional directive telling pygris to return a subset of data using 
        underlying arguments in geopandas.read_file().  
        subset_by operates as follows:
            - If a user supplies a tuple of format (minx, miny, maxx, maxy), 
            it will be interpreted as a bounding box and rows will be returned
            that intersect that bounding box;

            - If a user supplies a integer or a slice object, the first n rows
            (or the rows defined by the slice object) will be returned;

            - If a user supplies an object of type geopandas.GeoDataFrame
            or of type geopandas.GeoSeries, rows that intersect the input 
            object will be returned. CRS misalignment will be resolved 
            internally.  
    
    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of linear water.


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

        county_water = []     
        
        for i in valid_county:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/LINEARWATER/tl_{year}_{state}{i}_linearwater.zip"
            w = load_tiger(url, cache = cache, subset_by = subset_by)
            county_water.append(w)
        
        all_w = pd.concat(county_water, ignore_index = True)

        return all_w


    else:
        valid_county = validate_county(state, county)
    
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/LINEARWATER/tl_{year}_{state}{valid_county}_linearwater.zip"
        w = load_tiger(url, cache = cache, subset_by = subset_by)

        return w

def coastline(year = None, cache = False):
    """
    Load an coastline shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. 

    cache : bool 
        If True, the function will download a Census shapefile to a cache directory 
        on the user's computer for future access.  If False, the function will load
        the shapefile directly from the Census website.  
        
    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of the US coastline.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information.
    
    """
    if year is None:
        year = 2021
        print(f"Using the default year of {year}")

    if year > 2016:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/COASTLINE/tl_{year}_us_coastline.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/COAST/tl_{year}_us_coastline.zip"
    
    return load_tiger(url, cache = cache)