from .helpers import load_tiger, validate_state, validate_county, fips_codes
import pandas as pd
def area_water(state, county, year = None, cache = False):
    if year is None:
        print("Using the default year of 2021")
        year = 2021

    state = validate_state(state)

    if type(county) is list:
        valid_county = [validate_county(state, x) for x in county]

        county_water = []     
        
        for i in valid_county:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/AREAWATER/tl_{year}_{state}{i}_areawater.zip"
            w = load_tiger(url, cache = cache)
            county_water.append(w)
        
        all_w = pd.concat(county_water, ignore_index = True)

        return all_w


    else:
        valid_county = validate_county(state, county)
    
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/AREAWATER/tl_{year}_{state}{valid_county}_areawater.zip"
        w = load_tiger(url, cache = cache)

        return w

    

def linear_water(state, county, year = None, cache = False):
    if year is None:
        print("Using the default year of 2021")
        year = 2021

    state = validate_state(state)

    if type(county) is list:
        valid_county = [validate_county(state, x) for x in county]

        county_water = []     
        
        for i in valid_county:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/LINEARWATER/tl_{year}_{state}{i}_linearwater.zip"
            w = load_tiger(url, cache = cache)
            county_water.append(w)
        
        all_w = pd.concat(county_water, ignore_index = True)

        return all_w


    else:
        valid_county = validate_county(state, county)
    
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/LINEARWATER/tl_{year}_{state}{valid_county}_linearwater.zip"
        w = load_tiger(url, cache = cache)

        return w

def coastline(year = None, cache = False):
    if year is None:
        year = 2021
        print(f"Using the default year of {year}")

    if year > 2016:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/COASTLINE/tl_{year}_us_coastline.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/COAST/tl_{year}_us_coastline.zip"
    
    return load_tiger(url, cache = cache)