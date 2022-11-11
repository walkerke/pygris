import requests
import geopandas as gp
import os
import appdirs
import pandas as pd
import re
from pygris.internal_data import fips_path
from pygris.geocode import geocode

def _load_tiger(url, cache = False, subset_by = None):

    # Parse the subset_by argument to figure out what it should represent
    # If subset_by is a tuple, it becomes bbox
    if subset_by is not None:
        if type(subset_by) is tuple:
            sub = {"bbox": subset_by}
        # If subset_by is an integer or slice, it becomes rows
        elif type(subset_by) is int or type(subset_by) is slice:
            sub = {"rows": subset_by}
        # If subset_by is a GeoDataFrame or GeoSeries, use mask
        # CRS conflicts should be resolved internally by geopandas
        elif type(subset_by) is gp.GeoDataFrame or type(subset_by) is gp.GeoSeries:
            sub = {"mask": subset_by}
        # If subset_by is a dict, it should be of format address: buffer, with the 
        # buffer specified in meters
        elif type(subset_by) is dict:
            # We need to iterate through the key/value pairs, geocoding 
            # each one
            buffers = []
            for i, j in subset_by.items():
                g = geocode(address = i, as_gdf = True, limit = 1)
                g_buffer = g.to_crs('ESRI:102010').buffer(distance = j)
                buffers.append(g_buffer)
            
            buffer_gdf = pd.concat(buffers)

            sub = {"mask": buffer_gdf}


    if not cache:
        if subset_by is not None:
            tiger_data = gp.read_file(url, **sub)
        else:
            tiger_data = gp.read_file(url)

        return tiger_data
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
        if subset_by is not None:
            tiger_data = gp.read_file(out_file, **sub)
        else:
            tiger_data = gp.read_file(out_file)

        return tiger_data         

def fips_codes():
    path = fips_path()

    return pd.read_csv(path, dtype = 'object')

def validate_state(state, quiet = False):
    # Standardize as lowercase
    original_input = state
    state = state.lower()
    # Get rid of whitespace
    state = state.strip()

    # If the FIPS code is supplied
    if state.isdigit():
        # Left-pad if necessary
        state = state.zfill(2)

        # Return the result
        return state
    else:
        # Get the FIPS codes dataset
        fips = fips_codes()
        # If a state abbreviation, use the state postal code
        if len(state) == 2:
            fips['postal_lower'] = fips.state.str.lower()
            state_sub = fips.query('postal_lower == @state')

            if state_sub.shape[0] == 0:
                raise ValueError("You have likely entered an invalid state code, please revise.")
            else:
                state_fips = state_sub.state_code.unique()[0]
                
                if not quiet:
                    print(f"Using FIPS code '{state_fips}' for input '{original_input}'")

                return state_fips
        else:
            # If a state name, grab the appropriate info from fips_codes
            fips['name_lower'] = fips.state_name.str.lower()
            state_sub = fips.query('name_lower == @state')

            if state_sub.shape[0] == 0:
                raise ValueError("You have likely entered an invalid state code, please revise.")
            else:
                state_fips = state_sub.state_code.unique()[0]

                if not quiet:
                    print(f"Using FIPS code '{state_fips}' for input '{original_input}'")
                
                return state_fips
            

def validate_county(state, county, quiet = False):
    state = validate_state(state)

    fips = fips_codes()

    county_table = fips.query('state_code == @state')

    # If they used numbers for the county:
    if county.isdigit():
        # Left-pad with zeroes
        county.zfill(3)
        
        return county
    
    # Otherwise, if they pass a name:
    else:
        # Find counties in the table that could match
        county_sub = county_table.query('county.str.contains(@county, flags = @re.IGNORECASE, regex = True)',
                                        engine = 'python')

        possible_counties = county_sub.county.unique()

        if len(possible_counties) == 0:
            raise ValueError("No county names match your input country string.")
        elif len(possible_counties) == 1:

            cty_code = (county_sub
                .query('county == @possible_counties[0]')
                .county_code
                .unique()[0]
            )            

            if not quiet:
                print(f"Using FIPS code '{cty_code}' for input '{county}'")

            return cty_code
        else:
            msg = f"Your string matches {' and '.join(possible_counties)}. Please refine your selection."

            raise ValueError(msg)