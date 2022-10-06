import requests
import pandas as pd
import appdirs
import os

def get_census(dataset, year, variables, params = {}):
    endpoint = "https://api.census.gov/data"

    if type(variables) is not list:
        variables = [variables]

    joined_vars = ",".join(variables)

    params.update({'get': joined_vars})

    base = f"{endpoint}/{year}/{dataset}"

    req = requests.get(url = base, params = params)

    out = pd.read_json(req.text)

    out.columns = out.iloc[0]
    out = out[1:]
    
    return out


def get_lodes(state, year, lodes_type = "od", part = "main", 
              job_type = "JT00", segment = "S000", cache = False):

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

