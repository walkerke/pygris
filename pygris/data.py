import requests
import pandas as pd
import numpy as np
import appdirs
import os
from pygris.enumeration_units import states, counties, tracts, block_groups, blocks
from pygris.geometry import _get_geometry
import warnings


def get_census(dataset, variables, year = None, params = {}, 
               return_geoid = False, guess_dtypes = False):
    """
    Make a request to a US Census Bureau API endpoint

    Parameters
    --------------
    dataset : str
        The dataset name; browse https://api.census.gov/data.html for options.
        The name will be the componet of the API URL that follows "data/" or 
        the year.  For example, 1-year ACS data will be "acs/acs1". 
    variables : str or list
        A string (or list of strings) representing the variables requested from the 
        API. Datasets have 'variables.html' pages that can be viewed to find 
        variable IDs, e.g. "https://api.census.gov/data/2017/acs/acs1/variables.html". 
    year : int
        The year of the dataset, e.g. 2021. Not all datasets use a year, so leave 
        blank if so (such as the timeseries APIs). 
    params : dict
        A dict of parameters to send with your API request.  This will 
        vary based on the API you are using. You don't need to include
        variables in the request, but other optional parameters 
        will be included here. 
    return_geoid : bool
        If True, `get_census()` will attempt to assemble a GEOID column 
        from contextual information in the dataset that is suitable for 
        merging to Census shapes acquired with pygris.  This won't make sense
        / won't work for all datasets, so use this option with caution. 
        Defaults to False. 
    guess_dtypes : bool
        The Census APIs return all columns as strings, but many data 
        columns should be treated as numbers.  If True, `get_census()` 
        will scan the columns and try to guess which columns should be
        converted to numeric and do so. Users may want to leave this
        option False (the default) and convert columns on a 
        case-by-case basis.  

    Returns
    -------------
    A Pandas DataFrame of data from the requested US Census dataset.

    Notes
    -------------
    This function is a low-level interface to the Census APIs provided for convenience. For a full-featured, Pythonic
    interface to the US Census Bureau APIs, I would recommend using the cenpy package (https://cenpy-devs.github.io/cenpy/index.html)

    `get_census()` is inspired by Hannah Recht's work on the censusapi R package (https://www.hrecht.com/censusapi/).  

    """

    endpoint = "https://api.census.gov/data"

    if type(variables) is not list:
        variables = [variables]

    if year is None:
        base = f"{endpoint}/{dataset}"
    else:
        base = f"{endpoint}/{year}/{dataset}"

    # get request must be <50, split it and run each chunk (adapted from cenpy)
    data = []
    n_chunks = np.ceil(len(variables) / 50)
    for chunk in np.array_split(variables, n_chunks):

        joined_vars = ",".join(chunk)

        params.update({'get': joined_vars})

        req = requests.get(url = base, params = params)

        if req.status_code != 200:
            raise SyntaxError(f"Request failed. The Census Bureau error message is {req.text}")

        df = pd.DataFrame(req.json()[1:], columns=req.json()[0])

        if return_geoid:
            # find the columns that are not in variables
            my_cols = list(df.columns)

            # if 'state' is not in the list of columns, don't assemble the GEOID; too much
            # ambiguity among possible combinations across the various endpoints
            if "state" not in my_cols:
                raise ValueError("`return_geoid` is not supported for this geography hierarchy.")

            # Identify the position of the state column in my_cols, and
            # extract all the columns that follow it
            state_ix = my_cols.index("state")

            geoid_cols = my_cols[state_ix:]

            # Assemble the GEOID column, then remove its constituent parts
            df['GEOID'] = df[geoid_cols].agg("".join, axis = 1)

            df.drop(geoid_cols, axis = 1, inplace = True)

        if guess_dtypes:
            num_list = []
            # Iterate through the columns in variables and try to guess if they should be converted
            for v in chunk:
                check = pd.to_numeric(df[v], errors = "coerce")
                # If the columns aren't fully null, convert to numeric, taking care of any oddities
                if not pd.isnull(check.unique())[0]:
                    df[v] = check
                    num_list.append(v)

            # If we are guessing numerics, we should convert NAs (negatives below -1 million)
            # to NaN. Users who want to keep the codes should keep as object and handle
            # themselves.
            df[num_list] = df[num_list].where(df[num_list] > -999999)

        data += [df]  # Add output from each chunk to list

    if len(data) < 2:
        return data[0]

    # Merge on shared cols (either GEOID or State/County etc.
    out = data[0]
    for df_b in data[1:]:
        out = out.merge(df_b)

    return out


def get_lodes(state, year, version = "LODES8", lodes_type = "od", part = "main", 
              job_type = "JT00", segment = "S000", agg_level = "block", cache = False,
              return_geometry = False, return_lonlat = False, od_geometry = "home", 
              cb = True):

    """
    Get synthetic block-level data on workplace, residence, and origin-destination flows characteristics from the 
    LEHD Origin-Destination Employment Statistics (LODES) dataset

    Parameters
    --------------
    state : str
        The state postal code of your requested data. Please note that not all states are available 
        in all years.
    year : int
        The year of your requested data. LODES data go back to 2002, but not all datasets are available 
        for all years / for all states.  
    version : str
        The LODES version to use.  Version 8 (the default, use "LODES8") is enumerated at 2020 Census blocks.
        "LODES7" is enumerated at 2010 Census blocks, but ends in 2019; "LODES5" is enumerated at 2000 Census
        blocks, but ends in 2009.  
    lodes_type : str
        One of "od" (the default) for origin-destination flows, "wac" for workplace area characteristics, 
        or "rac" for residence area characteristics.  
    part : str
        Only relevant for the "od" file.  "main" gives information on within-state residence to workplace flows.
        "aux" gives information for residence to workplace flows from outside a given state.
    job_type : str
        The available job type breakdown; defaults to "JT00" for all jobs. Please review the LODES technical
        documentation for a description of other options.
    segment : str
        The workforce segment, relevant when lodes_type is "wac" or "rac". Defaults to "S000" for total jobs;
        review the LODES technical documentation for a description of other options.
    agg_level : str
        The level at which to aggregate the data.  Defaults to the Census block; other options include 
        "county", "tract", and "block group".  
    cache : bool
        If True, downloads the requested LODES data to a cache directory on your computer and reads from
        that directory if the file exists. Defaults to False, which will download the data by default. 
    return_geometry : bool
        If True, get_lodes() will fetch the corresponding polygon geometry for shapes and return a GeoPandas
        GeoDataFrame.  Defaults to False.
    return_lonlat : bool
        If True, columns representing the corresponding polygon centroid will be 
    od_geometry : str
        Whether to attach residential geometries ("home") or workplace geometries ("work").  Only specified
        when lodes_type is "od".  Defaults to "home".  
    cb : bool
        If retrieving geometry, use the Cartographic Boundary shapefile (True) or the TIGER/Line shapefile (False). 
        Defaults to True for LODES8 and LODES7, and False for LODES5.  

    Returns
    ---------------
    A Pandas DataFrame or GeoPandas GeoDataFrame of LODES data.


    Notes
    ---------------
    Please review the LODES technical documentation at https://lehd.ces.census.gov/data/lodes/LODES8/LODESTechDoc8.0.pdf for 
    more information.

    `get_lodes()` is inspired by the lehdr R package (https://github.com/jamgreen/lehdr) by 
    Jamaal Green, Dillon Mahmoudi, and Liming Wang.


    
    """

    if lodes_type not in ['od', 'wac', 'rac']:
        raise ValueError("lodes_type must be one of 'od', 'rac', or 'wac'.")
    
    state = state.lower()

    if lodes_type == "od":
        url = f"https://lehd.ces.census.gov/data/lodes/{version}/{state}/od/{state}_od_{part}_{job_type}_{year}.csv.gz"
    else:
        url = f"https://lehd.ces.census.gov/data/lodes/{version}/{state}/{lodes_type}/{state}_{lodes_type}_{segment}_{job_type}_{year}.csv.gz"
    
    if not cache:
        lodes_data = pd.read_csv(url)
        
    else:
        cache_dir = appdirs.user_cache_dir("pygris")

        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir) 

        basename = os.path.basename(url)

        out_file = os.path.join(cache_dir, basename)
        
        # If the file doesn't exist, you'll need to download it
        # and write it to the cache directory
        if not os.path.isfile(out_file):
            req = requests.get(url = url)

            with open(out_file, 'wb') as fd:
                fd.write(req.content)
        
        # Now, read in the file from the cache directory
        lodes_data = pd.read_csv(out_file)

    # Drop the 'createdate' column
    lodes_data = lodes_data.drop('createdate', axis = 1)

    if lodes_type == "od":
        lodes_data['w_geocode'] = lodes_data['w_geocode'].astype(str).str.zfill(15)
        lodes_data['h_geocode'] = lodes_data['h_geocode'].astype(str).str.zfill(15)
    elif lodes_type == "rac":
        lodes_data['h_geocode'] = lodes_data['h_geocode'].astype(str).str.zfill(15)
    else:
        lodes_data['w_geocode'] = lodes_data['w_geocode'].astype(str).str.zfill(15)

    # Handle aggregation logic
    if agg_level != "block":
        if agg_level == "county":
            end = 5
        elif agg_level == "tract":
            end = 11
        elif agg_level == "block group":
            end = 12
        else: 
            raise ValueError("Invalid agg_level; choose one of 'state', 'county', 'tract', or 'block group'.")
        
        if lodes_type == "wac":
            lodes_data['w_geocode'] = lodes_data['w_geocode'].str.slice(stop = end)

            lodes_data = lodes_data.groupby('w_geocode').agg("sum")
        elif lodes_type == "rac":
            lodes_data['h_geocode'] = lodes_data['h_geocode'].str.slice(stop = end)

            lodes_data = lodes_data.groupby('h_geocode').agg("sum")
        elif lodes_type == "od":
            lodes_data['h_geocode'] = lodes_data['h_geocode'].str.slice(stop = end)
            lodes_data['w_geocode'] = lodes_data['w_geocode'].str.slice(stop = end)

            lodes_data = lodes_data.groupby(['h_geocode', 'w_geocode']).agg("sum")  

    lodes_data = lodes_data.reset_index()
    # Handle geometry requests
    if return_geometry:
        print("Requesting feature geometry.") 

        if not cache:
            ("Use cache = True to speed this up in the future.")

        if return_lonlat: 
            raise ValueError("return_geometry and return_lonlat cannot be used at the same time.")

        if version == "LODES8":
            year = 2020
        elif version == "LODES7": 
            year = 2019
        else:
            year = 2000
            cb = False

        

        if lodes_type == "wac":
            geom = _get_geometry(geography = agg_level, state = state, cb = cb, year = year, cache = cache)

            geom.columns = ['w_geocode', 'geometry']

            geom_merged = geom.merge(lodes_data, on = "w_geocode")

        elif lodes_type == "rac":
            geom = _get_geometry(geography = agg_level, state = state, cb = cb, year = year, cache = cache)

            geom.columns = ['h_geocode', 'geometry']

            geom_merged = geom.merge(lodes_data, on = "h_geocode")     
        
        elif lodes_type == "od":
            if od_geometry == "home":
                if part == "main":
                    geom = _get_geometry(geography = agg_level, state = state, cb = cb, year = year, cache = cache)
                    geom.columns = ['h_geocode', 'geometry']

                    geom_merged = geom.merge(lodes_data, on = "h_geocode") 
                else: 
                    aux_states = lodes_data['h_geocode'].str.slice(stop = 2).unique().tolist()
                    h_geom_list = [_get_geometry(geography = agg_level, state = x, year = year, cb = cb, cache = cache) for x in aux_states]
                    h_geom = pd.concat(h_geom_list)

                    h_geom.columns = ['h_geocode', 'geometry']

                    geom_merged = h_geom.merge(lodes_data, on = "h_geocode") 

            elif od_geometry == "work":
                geom = _get_geometry(geography = agg_level, state = state, cb = cb, year = year, cache = cache)

                geom.columns = ['w_geocode', 'geometry']

                geom_merged = geom.merge(lodes_data, on = "w_geocode")
            else: 
                raise ValueError("od_geometry must be one of 'home' or 'work'.")
        
        return geom_merged
    
    elif return_lonlat:
        warnings.filterwarnings('ignore')
        print("Requesting feature geometry to determine longitude and latitude.") 

        if not cache:
            ("Use cache = True to speed this up in the future.")

        if version == "LODES8":
            year = 2020
        elif version == "LODES7": 
            year = 2019
        else:
            year = 2000
            cb = False

        geom = _get_geometry(geography = agg_level, state = state, cb = cb, year = year, cache = cache)

        if lodes_type == "wac":
            geom.columns = ['w_geocode', 'geometry']

            with warnings.catch_warnings():
                geom['w_lon'] = geom.centroid.x
                geom['w_lat'] = geom.centroid.y

            xy = geom.drop('geometry', axis = 1)

            lodes_merged = lodes_data.merge(xy, on = 'w_geocode')
        
        elif lodes_type == "rac":
            geom.columns = ['h_geocode', 'geometry']

            with warnings.catch_warnings():
                geom['h_lon'] = geom.centroid.x
                geom['h_lat'] = geom.centroid.y

            xy = geom.drop('geometry', axis = 1)

            lodes_merged = lodes_data.merge(xy, on = 'h_geocode')
        
        elif lodes_type == "od":
            w_geom = geom.copy()

            w_geom.columns = ['w_geocode', 'geometry']

            with warnings.catch_warnings():
                w_geom['w_lon'] = w_geom.centroid.x
                w_geom['w_lat'] = w_geom.centroid.y

            w_xy = w_geom.drop('geometry', axis = 1)

            if part == "main":
                h_geom = geom.copy()
            elif part == "aux":
                aux_states = lodes_data['h_geocode'].str.slice(stop = 2).unique().tolist()
                h_geom_list = [_get_geometry(geography = agg_level, state = x, year = year, cb = cb, cache = cache) for x in aux_states]
                h_geom = pd.concat(h_geom_list)

            h_geom.columns = ['h_geocode', 'geometry']

            with warnings.catch_warnings():
                h_geom['h_lon'] = h_geom.centroid.x
                h_geom['h_lat'] = h_geom.centroid.y

            h_xy = h_geom.drop('geometry', axis = 1)

            lodes_merged = (lodes_data
                .merge(h_xy, on = "h_geocode")
                .merge(w_xy, on = "w_geocode")
                )
        
        return lodes_merged
    else:
        return lodes_data 


def get_xwalk(state, version = "LODES8", cache = False):

    """
    Get a Census block-to-parent geography crosswalk file for a given state and a given Census year (represented)
    by a LODES version).  

    Parameters
    --------------
    state : str
        The state postal code of your requested data. 
    version : str
        The LODES version to use.  Version 8 (the default, use "LODES8") is enumerated at 2020 Census blocks. Version 7
        (use "LODES7") is enumerated at 2010 Census blocks.
    cache : bool
        If True, downloads the requested LODES data to a cache directory on your computer and reads from
        that directory if the file exists. Defaults to False, which will download the data by default.     

    Returns
    ---------------
    A Pandas DataFrame representing the correspondence between Census blocks and a variety of parent geograpies
    in a given LODES dataset (and in turn a given Census year).


    Notes
    ---------------
    Please review the LODES technical documentation at https://lehd.ces.census.gov/data/lodes/LODES8/LODESTechDoc8.0.pdf for 
    more information.

    `get_xwalk()` is inspired by the lehdr R package (https://github.com/jamgreen/lehdr) by 
    Jamaal Green, Dillon Mahmoudi, and Liming Wang.


    
    """

    state = state.lower()

    url = f"https://lehd.ces.census.gov/data/lodes/{version}/{state}/{state}_xwalk.csv.gz"

    if not cache:
        xwalk_data = pd.read_csv(url, dtype="object")
        
    else:
        cache_dir = appdirs.user_cache_dir("pygris")

        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir) 

        basename = os.path.basename(url)

        out_file = os.path.join(cache_dir, basename)
        
        # If the file doesn't exist, you'll need to download it
        # and write it to the cache directory
        if not os.path.isfile(out_file):
            req = requests.get(url = url)

            with open(out_file, 'wb') as fd:
                fd.write(req.content)
        
        # Now, read in the file from the cache directory
        xwalk_data = pd.read_csv(out_file, dtype = "object")
    
    xwalk_data = xwalk_data.drop('createdate', axis = 1)

    xwalk_data['blklatdd'] = xwalk_data['blklatdd'].astype(float)
    xwalk_data['blklondd'] = xwalk_data['blklondd'].astype(float)

    return xwalk_data


