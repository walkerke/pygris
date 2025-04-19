"""Legislative and voting district area functions"""

__author__ = "Kyle Walker <kyle@walker-data.com"

from pygris.helpers import _load_tiger, validate_state, validate_county

def congressional_districts(state = None, cb = False, resolution = "500k", year = None,
                            cache = False, subset_by = None, protocol = "http", timeout = 1800):

    """
    Load a congressional districts shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str 
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None (the default), congressional districts for the entire United States
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
        defaults to 2024.
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
    protocol : str
        The protocol to use for downloading the file. Defaults to "http".
    timeout : int
        The timeout for the download request in seconds. Defaults to 1800 (30 minutes).

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of congressional districts.


    Notes
    ----------
    See https://www.census.gov/programs-surveys/geography/guidance/geo-areas/congressional-dist.html for more information. 


    """

    if year is None:
        year = 2024
        print(f"Using the default year of {year}")
    
    if cb and year < 2013:
        raise ValueError("`cb = True` for congressional districts is unavailable prior to 2013.")

    if resolution not in ['500k', '5m', '20m']:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")

    if year in range(2018, 2023):
        congress = "116"
    elif year in [2016, 2017]:
        congress = "115"
    elif year in [2014, 2015]:
        congress = "114"
    elif year == 2013:
        congress = "113"
    elif year in [2011, 2012]:
        congress = "112"
    elif year == 2010:
        congress = "111"
    else:
        raise ValueError(f"Congressional districts are not available from pygris for {year}.")
    
    if cb:
        if year == 2013:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_cd{congress}_{resolution}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_cd{congress}_{resolution}.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CD/tl_{year}_us_cd{congress}.zip"
    

    cds = _load_tiger(url, cache = cache, subset_by = subset_by, protocol = protocol, timeout = timeout)

    if state is not None:
        if type(state) is not list:
            state = [state]
        valid_state = [validate_state(x) for x in state]
        cds = cds.query('STATEFP in @valid_state')

    return cds
        

def state_legislative_districts(state = None, house = "upper", cb = False,
                                year = None, cache = False, subset_by = None, protocol = "http", timeout = 1800):
    """
    Load a state legislative districts shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str 
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None, state legislative districts for the entire United States
        will be downloaded when cb is True and the year is 2019 or later.  
    house : str 
        Specify here whether you want boundaries for the "upper" or "lower" house. 
        Note: Nebraska has a unicameral legislature, so only "upper" will work for Nebraska.
    cb : bool 
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).
    year : int 
        The year of the TIGER/Line or cartographic boundary shapefile. If not specified,
        defaults to 2024.
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
    protocol : str
        The protocol to use for downloading the file. Defaults to "http".
    timeout : int
        The timeout for the download request in seconds. Defaults to 1800 (30 minutes).

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of state legislative districts.


    Notes
    ----------
    See https://www.census.gov/programs-surveys/geography/guidance/geo-areas/state-legis-dist.html for more information. 


    """
    
    if year is None:
        year = 2024
        print(f"Using the default year of {year}")
    

    if state is None:
        if year > 2018 and cb:
            state = "us"
            print("Retrieving state legislative districts for the entire United States.")
        else:
            raise ValueError("A state must be specified for this year/dataset combination.")
    else:
        state = validate_state(state)

    if house not in ["upper", "lower"]:
        raise ValueError("You must specify either 'upper' or 'lower' as an argument for house.")
    
    if house == "lower":
        type = "sldl"
    else:
        type = "sldu"

    
    if cb:
        if year == 2010:
            if type == "sldu":
                url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_{state}_610_u2_500k.zip"
            elif type == "sldl":
                url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_{state}_620_l2_500k.zip"
        elif year == 2013:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_{state}_{type}_500k.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state}_{type}_500k.zip"
    else:
        if year in [2000, 2010]:
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/{type.upper()}/{year}/tl_2010_{state}_{type}{str(year)[2:]}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/{type.upper()}/tl_{year}_{state}_{type}.zip"

    stateleg = _load_tiger(url, cache = cache, subset_by = subset_by, protocol = protocol, timeout = timeout)

    return stateleg

    
def voting_districts(state = None, county = None, cb = False,
                     year = 2020, cache = False, subset_by = None, protocol = "http", timeout = 1800):
    """
     Load a voting districts shapefile into Python as a GeoDataFrame

    Parameters
    ----------
    state : str 
        The state name, state abbreviation, or two-digit FIPS code of the desired state. 
        If None, voting districts for the entire United States
        will be downloaded when cb is True and the year is 2020.  
    county : str 
        The county name or three-digit FIPS code of the desired county. If None, voting
        districts for the selected state will be downloaded. 
    cb : bool 
        If set to True, download a generalized (1:500k) cartographic boundary file.  
        Defaults to False (the regular TIGER/Line file).
    year : int
        The year of the TIGER/Line or cartographic boundary shapefile. Available years 
        for voting districts are 2020 (for 2020 districts) and 2012 (for 2010 districts).
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
    protocol : str
        The protocol to use for downloading the file. Defaults to "http".
    timeout : int
        The timeout for the download request in seconds. Defaults to 1800 (30 minutes).

    Returns
    ----------
    geopandas.GeoDataFrame: A GeoDataFrame of voting districts.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch14GARM.pdf for more information.    
    
    
    """
    
    if year != 2020 and cb:
        raise ValueError("Cartographic boundary voting district files are only available for 2020.")
    
    if state is None:
        if year > 2018 and cb:
            state = "us"
            print("Retrieving voting districts for the entire United States")
        else:
            raise ValueError("A state must be specified for this year/dataset combination.")
    else:
        state = validate_state(state)
    

    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_{state}_vtd_500k.zip"

        vtds = _load_tiger(url, cache = cache, subset_by = subset_by, protocol = protocol, timeout = timeout)

        if county is None:
            return vtds
        else:
            if type(county) is not list:
                county = [county]
                valid_county = [validate_county(state, x) for x in county]
                vtds = vtds.query('COUNTYFP20 in @valid_county')
            
            return vtds
    else:
        if year == 2012:
            url = f"https://www2.census.gov/geo/tiger/TIGER2012/VTD/tl_2012_{state}_vtd10.zip"
        else:
            if county is not None:
                county = validate_county(state, county)
                url = f"https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/tl_2020_{state}{county}_vtd20.zip"
            else:
                url = f"https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/tl_2020_{state}_vtd20.zip"
        
        vtds = _load_tiger(url, cache = cache, subset_by = subset_by, protocol = protocol, timeout = timeout)

        return vtds