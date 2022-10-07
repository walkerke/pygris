from .helpers import load_tiger, validate_state, validate_county, fips_codes
import pandas as pd

def roads(state, county, year = None, cache = False):

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    state = validate_state(state)

    if type(county) is list:
        valid_county = [validate_county(state, x) for x in county]

        county_roads = []     
        
        for i in valid_county:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ROADS/tl_{year}_{state}{i}_roads.zip"
            r = load_tiger(url, cache = cache)
            county_roads.append(r)
        
        all_r = pd.concat(county_roads, ignore_index = True)

        return all_r


    else:
        valid_county = validate_county(state, county)
    
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ROADS/tl_{year}_{state}{valid_county}_roads.zip"
        r = load_tiger(url, cache = cache)

        return r


def primary_roads(year = None, cache = False):

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/PRIMARYROADS/tl_{year}_us_primaryroads.zip"
    r = load_tiger(url, cache = cache)

    return r


def primary_secondary_roads(state, year = None, cache = False):

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    state = validate_state(state)
    
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/PRISECROADS/tl_{year}_{state}_prisecroads.zip"

    r = load_tiger(url, cache = cache)

    return r


def rails(year = None, cache = False):

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/RAILS/tl_{year}_us_rails.zip"
    r = load_tiger(url, cache = cache)

    return r


def address_ranges(state, county, year = None, cache = False):

    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    state = validate_state(state)

    if type(county) is list:
        valid_county = [validate_county(state, x) for x in county]

        county_ranges = []     
        
        for i in valid_county:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ADDRFEAT/tl_{year}_{state}{i}_addrfeat.zip"
            r = load_tiger(url, cache = cache)
            county_ranges.append(r)
        
        all_r = pd.concat(county_ranges, ignore_index = True)

        return all_r


    else:
        valid_county = validate_county(state, county)
    
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ADDRFEAT/tl_{year}_{state}{valid_county}_addrfeat.zip"
        r = load_tiger(url, cache = cache)

        return r