import requests
import pandas as pd
import json
import geopandas as gp

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

