import requests
import pandas as pd
import appdirs
import os

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

    joined_vars = ",".join(variables)

    params.update({'get': joined_vars})

    if year is None:
        base = f"{endpoint}/{dataset}"
    else:
        base = f"{endpoint}/{year}/{dataset}"

    req = requests.get(url = base, params = params)

    if req.status_code != 200:
        raise SyntaxError(f"Request failed. The Census Bureau error message is {req.text}")

    
    out = pd.read_json(req.text)

    out.columns = out.iloc[0]
    out = out[1:]

    if return_geoid:
        # find the columns that are not in variables
        my_cols = list(out.columns)

        # if 'state' is not in the list of columns, don't assemble the GEOID; too much 
        # ambiguity among possible combinations across the various endpoints
        if "state" not in my_cols:
            raise ValueError("`return_geoid` is not supported for this geography hierarchy.")

        # Identify the position of the state column in my_cols, and 
        # extract all the columns that follow it
        state_ix = my_cols.index("state")

        geoid_cols = my_cols[state_ix:]
       
        # Assemble the GEOID column, then remove its constituent parts
        out['GEOID'] = out[geoid_cols].agg("".join, axis = 1)

        out = out.drop(geoid_cols, axis = 1)
    
    if guess_dtypes:
        num_list = []
        # Iterate through the columns in variables and try to guess if they should be converted
        for v in variables:
            check = pd.to_numeric(out[v], errors = "coerce")
            # If the columns aren't fully null, convert to numeric, taking care of any oddities
            if not pd.isnull(check.unique())[0]:
                out[v] = check
                num_list.append(v)

        # If we are guessing numerics, we should convert NAs (negatives below -1 million)
        # to NaN. Users who want to keep the codes should keep as object and handle
        # themselves.
        out[num_list] = out[num_list].where(out[num_list] > -999999)

    return out


def get_lodes(state, year, lodes_type = "od", part = "main", 
              job_type = "JT00", segment = "S000", cache = False):

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
    cache : bool
        If True, downloads the requested LODES data to a cache directory on your computer and reads from
        that directory if the file exists. Defaults to False, which will download the data by default. 

    Returns
    ---------------
    A Pandas DataFrame of LODES data.


    Notes
    ---------------
    Please review the LODES technical documentation at https://lehd.ces.census.gov/data/lodes/LODES7/LODESTechDoc7.5.pdf for 
    more information.

    `get_lodes()` is inspired by the lehdr R package (https://github.com/jamgreen/lehdr) by 
    Jamaal Green, Dillon Mahmoudi, and Liming Wang.


    
    """

    if lodes_type not in ['od', 'wac', 'rac']:
        raise ValueError("lodes_type must be one of 'od', 'rac', or 'wac'.")
    
    state = state.lower()

    if lodes_type == "od":
        url = f"https://lehd.ces.census.gov/data/lodes/LODES7/{state}/od/{state}_od_{part}_{job_type}_{year}.csv.gz"
    else:
        url = f"https://lehd.ces.census.gov/data/lodes/LODES7/{state}/{lodes_type}/{state}_{lodes_type}_{segment}_{job_type}_{year}.csv.gz"
    
    if not cache:
        lodes_data = pd.read_csv(url)
        
        if lodes_type == "od":
            lodes_data['w_geocode'] = lodes_data['w_geocode'].astype(str).str.zfill(15)
            lodes_data['h_geocode'] = lodes_data['h_geocode'].astype(str).str.zfill(15)
        elif lodes_type == "rac":
            lodes_data['h_geocode'] = lodes_data['h_geocode'].astype(str).str.zfill(15)
        else:
            lodes_data['w_geocode'] = lodes_data['w_geocode'].astype(str).str.zfill(15)        

        return lodes_data
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

        if lodes_type == "od":
            lodes_data['w_geocode'] = lodes_data['w_geocode'].astype(str).str.zfill(15)
            lodes_data['h_geocode'] = lodes_data['h_geocode'].astype(str).str.zfill(15)
        elif lodes_type == "rac":
            lodes_data['h_geocode'] = lodes_data['h_geocode'].astype(str).str.zfill(15)
        else:
            lodes_data['w_geocode'] = lodes_data['w_geocode'].astype(str).str.zfill(15)

        return lodes_data          