import requests
import pandas as pd
import json
import geopandas as gp
import numpy as np
from io import StringIO
import csv


def _parse_geographies(response_obj, geography, keep_geo_cols, type):
    # Walk through the response object 
    # first, grab appropriate geography data
    if type == "geocode":
        geo_data = pd.json_normalize(response_obj['result'], ['addressMatches', 'geographies', geography])

        if not keep_geo_cols:
            geo_data = geo_data.filter(['GEOID'])

        # Next, get the coordinates
        coords = pd.json_normalize(response_obj['result'], 'addressMatches').filter(['coordinates.x', 'coordinates.y'])

        coords.columns = ['longitude', 'latitude']

        # Combine the two frames
        out = coords.join(geo_data)

        return out

    else:
        geo_data = pd.json_normalize(response_obj['result'], ['geographies', geography])

        if not keep_geo_cols:
            geo_data = geo_data.filter(['GEOID'])
        
        return geo_data
    

def geocode(address = None, street = None, city = None, state = None, zip = None,
            benchmark = "Public_AR_Current",  
            vintage = "Census2020_Current", as_gdf = False,
            geography = "Census Blocks", limit = 1, 
            keep_geo_cols = False, return_dict = False):
    """
    Use the Census geocoder to return XY coordinates and Census geography for an input address in the
    United States.

    Parameters
    ---------------
    address : str
        A single-line address to be geocoded, e.g. "1600 Pennsylvania Ave, Washington DC 20500"
    street : str
        The street address component, e.g. "1600 Pennsylvania Ave", if breaking out the address into 
        multiple arguments.
    city : str
        The city address component, e.g. "Washington"
    state : str
        The state address component, e.g. "DC"
    zip : str
        The zip code address component, e.g. "20500"
    benchmark : str
        The geocoding benchmark to use. Defaults to "Public_AR_Current"; other options are 
        outlined at https://geocoding.geo.census.gov/geocoder/benchmarks. 
    vintage : str
        The geocoding vintage to use. Defaults to "Census2020_Current" to return 2020 Census
        geographies. Vintages available for a given benchmark can be looked up at 
        https://geocoding.geo.census.gov/geocoder/vintages?benchmark={benchmark_id}, 
        where benchmark_id is replaced with the benchmark ID.  
    as_gdf : bool
        If False (the default), returns a regular Pandas DataFrame of results. 
        If True, converts the DataFrame into a GeoDataFrame of points.
    geography : str
        The Census geography to return; defaults to 'Census Blocks'. 
    limit : int
        How many records to return (as the geocoder can sometimes return multiple
        matches). Defaults to 1.
    keep_geo_cols : bool
        The Census geocoder can return a wide range of contextual information about
        a location with its response. If True, return all of these columns 
        (default False)
    return_dict : bool
        Advanced users may want to keep the general structure of the Census 
        geocoder response as a dict without having pygris parse the response. 
        If so, use True (default False).
    
    Returns
    ---------------
    A DataFrame (or GeoDataFrame) representing the geocoded address.


    Notes
    ---------------
    See https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html for more information.

    """

    if address is not None:
        url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
    elif street is not None:
        url = "https://geocoding.geo.census.gov/geocoder/geographies/address"
    else:
        raise ValueError("Either a single-line address or street must be specified.")

    req = requests.get(url = url, 
                       params = {"address": address,
                        "street": street,
                        "city": city,
                        "state": state,
                        "zip": zip,
                        "benchmark": benchmark,
                        "vintage": vintage,
                        "format": "json"})

    if req.status_code != 200:
        raise SyntaxError(f"Your request failed. The error message is {req.text}")
    
    r = json.loads(req.text)

    if return_dict:
        return r
    else:
        output = _parse_geographies(response_obj = r, geography = geography, keep_geo_cols = keep_geo_cols,
                                    type = "geocode")

        if address is not None:
            output['address'] = address
        elif street is not None:
            output['street'] = street
            output['city'] = city
            output['state'] = state
            output['zip'] = zip

        output = output.iloc[0:limit]

    if as_gdf:
        output = gp.GeoDataFrame(data = output, crs = 4326, geometry = gp.points_from_xy(x = output.longitude, y = output.latitude))
    
    return output


def geolookup(longitude, latitude,
            benchmark = "Public_AR_Current",  
            vintage = "Census2020_Current",
            geography = "Census Blocks", limit = 1, 
            keep_geo_cols = False, return_dict = False): 

    """
    Use the Census GeoLookup service to return Census geography for an XY coordinate
    pair in the United States.

    Parameters
    ---------------
    longitude : float
        The X (longitude) coordinate of your requested location.
    latitude : float
        The Y (latitude) coordinate of your requested location.
    benchmark : str
        The geocoding benchmark to use. Defaults to "Public_AR_Current"; other options are 
        outlined at https://geocoding.geo.census.gov/geocoder/benchmarks. 
    vintage : str
        The geocoding vintage to use. Defaults to "Census2020_Current" to return 2020 Census
        geographies. Vintages available for a given benchmark can be looked up at 
        https://geocoding.geo.census.gov/geocoder/vintages?benchmark={benchmark_id}, 
        where benchmark_id is replaced with the benchmark ID.  
    geography : str
        The Census geography to return; defaults to 'Census Blocks'. 
    limit : int
        How many records to return (as the geocoder can sometimes return multiple
        matches). Defaults to 1.
    keep_geo_cols : bool
        The Census geocoder can return a wide range of contextual information about
        a location with its response. If True, return all of these columns 
        (default False)
    return_dict : bool
        Advanced users may want to keep the general structure of the Census 
        geocoder response as a dict without having pygris parse the response. 
        If so, use True (default False).
    
    Returns
    ---------------
    A DataFrame representing the location with contextual information from the Census Bureau.


    Notes
    ---------------
    See https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html for more information.

    """

    url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"

    req = requests.get(url = url, 
                       params = {"x": longitude,
                        "y": latitude,
                        "benchmark": benchmark,
                        "vintage": vintage,
                        "format": "json"})
    
    if req.status_code != 200:
        raise SyntaxError(f"Your request failed. The error message is {req.text}")
    
    r = json.loads(req.text)

    if return_dict:
        return r
    else:
        output = _parse_geographies(response_obj = r, geography = geography, keep_geo_cols = keep_geo_cols,
                                    type = "geolookup")

        output['longitude'] = longitude
        output['latitude'] = latitude

        output = output.iloc[0:limit]

        return output

def batch_geocode(df, address, city = None, state = None, zip = None,
                  id_column = None, benchmark = "Public_AR_Current",
                  vintage = "Census2020_Current", as_gdf = False):

    """
    Use the Census batch geocoder to geocode a DataFrame of addresses in the Unied States.

    Parameters
    ---------------
    df : pandas.DataFrame
        A Pandas DataFrame containing addresses to be geocoded.  Address components should be 
        split across columns, meaning that separate columns are required for street address,
        city, state, and zip code.  
    street : str
        The name of the street address column, e.g. "address"
    city : str
        The name of the city column, e.g. "city"
    state : str
        The name of the state column, e.g. "state"
    zip : str
        The name of the zip code column, e.g. "zip"
    benchmark : str
        The geocoding benchmark to use. Defaults to "Public_AR_Current"; other options are 
        outlined at https://geocoding.geo.census.gov/geocoder/benchmarks. 
    vintage : str
        The geocoding vintage to use. Defaults to "Census2020_Current" to return 2020 Census
        geographies. Vintages available for a given benchmark can be looked up at 
        https://geocoding.geo.census.gov/geocoder/vintages?benchmark={benchmark_id}, 
        where benchmark_id is replaced with the benchmark ID.  
    as_gdf : bool
        If False (the default), returns a regular Pandas DataFrame of results. 
        If True, converts the DataFrame into a GeoDataFrame of points.
    
    Returns
    ---------------
    A DataFrame (or GeoDataFrame) representing the geocoded addresses.


    Notes
    ---------------
    See https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html for more information.

    """

    # Check to make sure the dataset doesn't exceed 10k rows
    if df.shape[0] > 10000:
        raise ValueError("The row limit for the Census batch geocoder is 10,000. Consider splitting your request into multiple requests and retry.")
    
    # Prep the df object for sending to the geocoder
    if id_column is None:
        request_df = pd.DataFrame(
            {"Unique ID": range(0, df.shape[0]),
             "Street address": df[address]}
        )
    else:
        request_df = pd.DataFrame(
            {"Unique ID": df[id_column],
             "Street address": df[address]}
        )    

    if city is None:
        request_df["City"] = np.nan
    else:
        request_df["City"] = df[city]
    
    if state is None:
        request_df["State"] = np.nan
    else:
        request_df["State"] = df[state]
    
    if zip is None:
        request_df["ZIP"] = np.nan
    else:
        request_df["ZIP"] = df[zip]

    # Store the df as a CSV
    request_csv = request_df.to_csv(index = False, header = False)

    # Formulate the request
    req = requests.post(
        url = "https://geocoding.geo.census.gov/geocoder/geographies/addressbatch",
        files = {"addressFile": ('request.csv', request_csv)},
        data = {
            "benchmark": benchmark,
            "vintage": vintage
        }
    )

    if req.status_code != 200:
        raise SyntaxError(f"Your request failed. The error message is {req.text}")

    output = pd.read_csv(StringIO(req.text), sep = ",", header = None, quoting = csv.QUOTE_ALL)

    # name the columns appropriately
    output.columns = ['id', 'address', 'status', 'match_quality', 'matched_address', 'coordinates', 'tiger_line_id', 'tiger_side', 
                      'state', 'county', 'tract', 'block']

    # split longitude/latitude
    output = output.join(output['coordinates'].str.split(',', expand = True).rename(columns = {0: 'longitude', 1: 'latitude'})).drop('coordinates', axis = 1)

    if as_gdf:
        output = gp.GeoDataFrame(data = output, crs = 4326, geometry = gp.points_from_xy(x = output.longitude, y = output.latitude))

    return output


    

