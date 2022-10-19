"""General Census enumeration unit functions"""

__author__ = "Kyle Walker <kyle@walker-data.com"

from .helpers import load_tiger, validate_state, validate_county, fips_codes
import pandas as pd

def counties(state = None, cb = False, resolution = '500k', year = None, cache = False, subset_by = None):
    """
    Load a counties shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None (the default), counties for the entire United States
        will be downloaded.  

    cb : bool 
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

    resolution : str 
        The resolution of the cartographic boundary file; only applies if 
        the cb argument is set to True. The default is "500k"; options also
        include "5m" (1:5 million) and "20m" (1:20 million)
    
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
        defaults to 2021.

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
    geopandas.GeoDataFrame: A GeoDataFrame of counties.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch4GARM.pdf for more information. 


    """
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if resolution not in ['500k', '5m', '20m']:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")
    
    if cb is True:
        if year in [1990, 2000]:
            yr = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/PREVGENZ/co/co{yr}shp/co99_d{yr}_shp.zip"
        elif year == 2010:
            url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_us_050_00_{resolution}.zip"
        elif year in [2011, 2012]:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_county_{resolution}.zip"            
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_county_{resolution}.zip"
            
    else:
        if year == 1990:
            raise ValueError("Please specify `cb = True` to get 1990 data.")
        elif year in [2000, 2010]:
            yr = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/COUNTY/{year}/tl_2010_us_county{yr}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/COUNTY/tl_{year}_us_county.zip"

    ctys = load_tiger(url, cache = cache, subset_by = subset_by)

    if state is not None:
        if type(state) is not list:
            state = [state]
        valid_state = [validate_state(x) for x in state]
        ctys = ctys.query('STATEFP in @valid_state')

    return ctys

def tracts(state = None, county = None, cb = False, year = None, cache = False, subset_by = None):
    """
     Load a Census tracts shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str 
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None, Census tracts for the entire United States
        will be downloaded when cb is True and the year is 2020.  

    county : str
        The county name or three-digit FIPS code of the desired county. If None, Census tracts
        for the selected state will be downloaded. 

    cb : bool 
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

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
    geopandas.GeoDataFrame: A GeoDataFrame of Census tracts.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch10GARM.pdf for more information.    
    
    
    """
    if year is None:
        print("Using the default year of 2021")
        year = 2021

    if state is None:
        if year > 2018 and cb is True:
            state = 'us'
            print("Retrieving Census tracts for the entire United States")
        else:
            raise ValueError("A state is required for this year/dataset combination.")
    else:
        state = validate_state(state)
    
    if cb is True:
        if year in [1990, 2000]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/PREVGENZ/tr/tr{suf}shp/tr{state}_d{suf}_shp.zip"
        elif year == 2010:
            url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_{state}_140_00_500k.zip"
        elif year > 2013:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state}_tract_500k.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_{state}_tract_500k.zip"
    else:
        if year == 1990:
            raise ValueError("Please specify `cb = True` to get 1990 data.")
        elif year in [2000, 2010]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/TRACT/{year}/tl_2010_{state}_tract{suf}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state}_tract.zip"

    trcts = load_tiger(url, cache = cache, subset_by = subset_by)

    if county is not None:
        if type(county) is not list:
            county = [county]
        valid_county = [validate_county(state, x) for x in county]
        trcts = trcts.query('COUNTYFP in @valid_county')

    return trcts


def block_groups(state = None, county = None, cb = False, year = None, cache = False, subset_by = None):
    """
     Load a Census block groups shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str 
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None, Census tracts for the entire United States
        will be downloaded when cb is True and the year is 2020.  

    county : str
        The county name or three-digit FIPS code of the desired county. If None, block groups
        for the selected state will be downloaded. 

    cb : bool 
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

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
    geopandas.GeoDataFrame: A GeoDataFrame of Census block groups.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch10GARM.pdf for more information.    
    
    
    """
    if year is None:
        print("Using the default year of 2021")
        year = 2021

    if state is None:
        if year > 2018 and cb is True:
            state = 'us'
            print("Retrieving Census block groups for the entire United States")
        else:
            raise ValueError("A state is required for this year/dataset combination.")
    else:
        state = validate_state(state)
    
    if cb is True:
        if year in [1990, 2000]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/PREVGENZ/bg/bg{suf}shp/bg{state}_d{suf}_shp.zip"
        elif year == 2010:
            url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_{state}_150_00_500k.zip"
        elif year > 2013:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state}_bg_500k.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_{state}_bg_500k.zip"
    else:
        if year == 1990:
            raise ValueError("Please specify `cb = True` to get 1990 data.")
        elif year in [2000, 2010]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/BG/{year}/tl_2010_{state}_bg{suf}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/BG/tl_{year}_{state}_bg.zip"

    bgs = load_tiger(url, cache = cache, subset_by = subset_by)

    if county is not None:
        if type(county) is not list:
            county = [county]
        valid_county = [validate_county(state, x) for x in county]
        bgs = bgs.query('COUNTYFP in @valid_county')

    return bgs


def school_districts(state = None, type = "unified", cb = False, year = None, cache = False, subset_by = None):
    """
    Load a school districts shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str 
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None, Census tracts for the entire United States
        will be downloaded when cb is True and the year is 2020.  

    type : str 
        One of "unified", "elementary", or "secondary".  

    cb : bool 
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

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
    geopandas.GeoDataFrame: A GeoDataFrame of school district boundaries.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information. 


    """
    if year is None:
        print("Using the default year of 2021")
        year = 2021

    if state is None:
        if year > 2018 and cb is True:
            state = "us"
            print("Retrieving school districts for the entire United States")
        else:
            raise ValueError("A state must be specified for this year/dataset combination.")
    else:
        state = validate_state(state)
    
    if type == "unified":
        type = "unsd"
    elif type == "elementary":
        type = "elsd"
    elif type == "secondary":
        type = "scsd"
    else:
        raise ValueError("Invalid school district type.\nValid types are 'unified', 'elementary', and 'secondary'.")

    if cb is True:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state}_{type}_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/{type.upper()}/tl_{year}_{state}_{type}.zip"

    
    return load_tiger(url, cache = cache, subset_by = subset_by)


def states(cb = True, resolution = "500k", year = None, cache = False):
    """
    Load a states shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    cb : bool 
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

    resolution : str 
        The resolution of the cartographic boundary file; only applies if 
        the cb argument is set to True. The default is "500k"; options also
        include "5m" (1:5 million) and "20m" (1:20 million)
    
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
        defaults to 2021.

    cache : bool 
        If True, the function will download a Census shapefile to a cache directory 
        on the user's computer for future access.  If False, the function will load
        the shapefile directly from the Census website.  

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of states.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch4GARM.pdf for more information. 


    """

    if resolution not in ["500k", "5m", "20m"]:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")
    
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        if year in [1990, 2000]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/PREVGENZ/st/st{suf}shp/st99_d{suf}_shp.zip"
        elif year == 2010:
            url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_us_040_00_{resolution}.zip"
        else:
            if year > 2013:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_state_{resolution}.zip"
            else:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_state_{resolution}.zip"
    else:
        if year == 1990:
            raise ValueError("Please specify `cb = True` to get 1990 data.")
        elif year in [2000, 2010]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/STATE/{year}/tl_2010_us_state{suf}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/STATE/tl_{year}_us_state.zip"
    
    return load_tiger(url, cache = cache)

def pumas(state = None, cb = False, year = None, cache = False, subset_by = None):
    """
    Load a public use microdata area (PUMA) shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None, PUMAs for the entire United States
        will be downloaded if available for that dataset / year combination.  

    cb : bool 
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).
  
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
        defaults to 2021.

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
    geopandas.GeoDataFrame: A GeoDataFrame of PUMAs.


    Notes
    ----------
    2020 PUMAs are available with `year = 2022` and later.  PUMAs are not available in the 2020 and 2021 CB files; 
    use `year = 2019` or earlier to retrieve 2010 PUMAs.  
    
    See https://www.census.gov/programs-surveys/geography/guidance/geo-areas/pumas.html for more information. 


    """
    
    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if state is None:
        if year == 2019 and cb:
            state = "us"
            print("Retrieving PUMAs for the entire United States")
        else:
            raise ValueError("A year must be specified for this year/dataset combination.")
    else:
        state = validate_state(state)
    

    if year > 2021:
        suf = "20"
    else:
        suf = "10"
    
    if cb:
        if year in [2020, 2021]:
            raise ValueError("Cartographic boundary PUMAs are not yet available for years after 2019. Use the argument `year = 2019` instead to request your data.")    
        else:
            if year == 2013:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_{state}_puma{suf}_500k.zip"
            else:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state}_puma{suf}_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/PUMA/tl_{year}_{state}_puma{suf}.zip"

    pm = load_tiger(url, cache = cache, subset_by = subset_by)

    return pm

    
def places(state = None, cb = False, year = None, cache = False, subset_by = None):

    """
    Load a Census-designated places shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None (the default), places for the entire United States
        will be downloaded.  

    cb : bool 
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).
 
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
        defaults to 2021.

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
    geopandas.GeoDataFrame: A GeoDataFrame of Census-designated places.


    Notes
    ----------   
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch9GARM.pdf for more information. 

    """

    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if state is None:
        if year == 2019 and cb:
            state = "us"
            print("Retrieving Census-designated places for the entire United States")
        else:
            raise ValueError("A year must be specified for this year/dataset combination.")
    else:
        state = validate_state(state)
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state}_place_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/PLACE/tl_{year}_{state}_place.zip"

    return load_tiger(url, cache = cache, subset_by = subset_by)


def zctas(cb = False, starts_with = None, year = None, state = None, cache = False, subset_by = None):

    """
    Load a zip code tabulation areas (ZCTAs) shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    cb : bool
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).

    starts_with : str or list
        A string (or list of strings) representing the beginning characters of the 
        ZCTAs to be returned by the function.  

    year : int
        The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
        defaults to 2021.

    state : str
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None (the default), ZCTAs for the entire United States
        will be downloaded if available for that year / dataset combination.  

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
    geopandas.GeoDataFrame: A GeoDataFrame of zip code tabulation areas.


    Notes
    ----------   
    ZCTAs are approximations of zip codes, which themselves are not formally defined as areas
    by the United States Postal Service.  In turn, not all zip codes will have corresponding 
    ZCTAs.  For these reasons, ZCTAs are not recommended for spatial analysis and should 
    be used with appropriate caution.  

    See https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html for more information. 

    """

    if year is None:
        year = 2021
        print(f"Using the default year of {year}")
    
    if state is not None and year > 2010:
        raise ValueError("ZCTAs are only available by state for 2000 and 2010.")
    
    if state is not None and year == 2010 and cb:
        raise ValueError("ZCTAs are only available by state for 2010 when cb = FALSE.")
    
    if year == 1990:
        raise ValueError("Zip Code Tabulation Areas are only available beginning with the 2000 Census.")
    
    if state is not None:
        state = validate_state(state)
    
    if not cache:
        Warning("ZCTAs can take several minutes to download.\nTo cache the data and avoid re-downloading in future sessions, use the argument `cache = True`.")
    

    if cb:
        if year == 2000:
            if state is None:
                url = "https://www2.census.gov/geo/tiger/PREVGENZ/zt/z500shp/zt99_d00_shp.zip"
            else:
                url = f"https://www2.census.gov/geo/tiger/PREVGENZ/zt/z500shp/zt{state}_d00_shp.zip"
        elif year == 2010:
            url = "https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_us_860_00_500k.zip"
        elif year >= 2020:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_zcta520_500k.zip"
        else:
            if year == 2013:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_zcta510_500k.zip"
            else:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_zcta510_500k.zip"
    else:
        if year >= 2020:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ZCTA520/tl_{year}_us_zcta520.zip"
        else:
            if year in [2000, 2010]:
                suf = str(year)[2:]

                if state is None:
                    url = f"https://www2.census.gov/geo/tiger/TIGER2010/ZCTA5/{year}/tl_2010_us_zcta5{suf}.zip"
                else:
                    url = f"https://www2.census.gov/geo/tiger/TIGER2010/ZCTA5/{year}/tl_2010_{state}_zcta5{suf}.zip"
            else:
                url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ZCTA5/tl_{year}_us_zcta510.zip"
    
    zcta = load_tiger(url, cache = cache, subset_by = subset_by)

    if starts_with is not None:
        cols = zcta.columns.tolist()

        zcta_ix = [i for i, j in enumerate(cols) if j.startswith("ZCTA")][0]

        zcta_col = cols[zcta_ix]

        if type(starts_with) is not list:
            zcta_sub = zcta.loc[zcta[zcta_col].str.startswith(expr)]
        else:
            tmp = ["^" + i for i in starts_with]
            expr = "|".join(tmp)
            zcta_sub = zcta.loc[zcta[zcta_col].str.contains(expr)]        

        return zcta_sub
    
    else:
        return zcta
        

def blocks(state, county = None, year = None, cache = False, subset_by = None):
    """
     Load a Census blocks shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str, required
        The state name, state abbreviation, or two-digit FIPS code of the desired state.

    county : str
        The county name or three-digit FIPS code of the desired county. If None, blocks
        for the selected state will be downloaded. 

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
    geopandas.GeoDataFrame: A GeoDataFrame of Census blocks.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/TGRSHP2020_TechDoc.pdf for more information.    
    
    
    """

    if year is None:
        year = 2021
        print(f"Using the default year of {year}")

    if year == 1990:
        raise ValueError("Block files are not available for 1990.")

    state = validate_state(state)

    if not cache:
        Warning("Block shapefiles can take several minutes to download.\nConsider using `cache = True` to store block shapefiles\nin a local cache and avoid future downloads.")

    if year in [2000, 2010]:
        suf = str(year)[2:]
        if county is not None:
            county = validate_county(state, county)
        
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/TABBLOCK/{year}/tl_2010_{state}{county}_tabblock{suf}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/TABBLOCK/{year}/tl_2010_{state}_tabblock{suf}.zip"
    elif year in range(2011, 2014):
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TABBLOCK/tl_{year}_{state}_tabblock.zip"
    elif year in range(2014, 2020):
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TABBLOCK/tl_{year}_{state}_tabblock10.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TABBLOCK20/tl_{year}_{state}_tabblock20.zip"

    blks = load_tiger(url, cache = cache, subset_by = subset_by)

    if county is not None and year > 2010:
        if year > 2019:
            if type(county) is not list:
                county = [county]
            valid_county = [validate_county(state, x) for x in county]
            blks = blks.query('COUNTYFP20 in @valid_county')
        else:
            if type(county) is not list:
                county = [county]
            valid_county = [validate_county(state, x) for x in county]
            blks = blks.query('COUNTYFP10 in @valid_county')
    
    return blks


