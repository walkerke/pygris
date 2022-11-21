from pygris.helpers import _load_tiger

def native_areas(cb = False, year = None, cache = False, subset_by = None):
    """
    Load an American Indian / Alaska Native / Native Hawaiian areas shapefile into Python as a GeoDataFrame

    Parameters
    ----------
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
    geopandas.GeoDataFrame: A GeoDataFrame of American Indian / Alaska Native / Native Hawaiian areas.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch5GARM.pdf for more information. 


    """
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_aiannh_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/AIANNH/tl_{year}_us_aiannh.zip"
    
    return _load_tiger(url, cache = cache, subset_by = subset_by)


def tribal_subdivisions_national(cb = False, year = None, cache = False, subset_by = None):
    """
    Load an American Indian Tribal Subdivision National shapefile into Python as a GeoDataFrame

    Parameters
    ----------
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
    geopandas.GeoDataFrame: A GeoDataFrame of American Indian Tribal Subdivisions.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch5GARM.pdf for more information. 


    """
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_aitsn_500k.zip"
    else:
        if year < 2015:            
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/AITS/tl_{year}_us_aitsn.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/AITSN/tl_{year}_us_aitsn.zip"

    return _load_tiger(url, cache = cache, subset_by = subset_by)


def alaska_native_regional_corporations(cb = False, year = None, cache = False, subset_by = None):
    """
    Load an Alaska Native Regional Corporation shapefile into Python as a GeoDataFrame

    Parameters
    ----------
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
    geopandas.GeoDataFrame: A GeoDataFrame of Alaska Native Regional Corporations.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch5GARM.pdf for more information. 


    """
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_02_anrc_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ANRC/tl_{year}_02_anrc.zip"
    
    return _load_tiger(url, cache = cache, subset_by = subset_by)


def tribal_block_groups(cb = False, year = None, cache = False, subset_by = None):
    """
    Load a Tribal block groups shapefile into Python as a GeoDataFrame

    Parameters
    ----------
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
    geopandas.GeoDataFrame: A GeoDataFrame of Tribal block groups.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch5GARM.pdf for more information. 


    """
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_tbg_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TBG/tl_{year}_us_tbg.zip"
    
    return _load_tiger(url, cache = cache, subset_by = subset_by)



def tribal_tracts(cb = False, year = None, cache = False, subset_by = None):
    """
    Load a Tribal Census tracts shapefile into Python as a GeoDataFrame

    Parameters
    ----------
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
    geopandas.GeoDataFrame: A GeoDataFrame of Tribal Census tracts.


    Notes
    ----------
    See https://www2.census.gov/geo/pdfs/reference/GARM/Ch5GARM.pdf for more information. 


    """
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_ttract_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TTRACT/tl_{year}_us_ttract.zip"
    
    return _load_tiger(url, cache = cache, subset_by = subset_by)