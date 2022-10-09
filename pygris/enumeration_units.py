from .helpers import load_tiger, validate_state, validate_county, fips_codes
import pandas as pd

def counties(state = None, cb = False, resolution = '500k', year = None, cache = False):
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if resolution not in ['500k', '5m', '20m']:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")
    
    if cb is True:
        if year in [1990, 2000]:
            yr = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/PREVGENZ/co/co{yr}shp/co99_d{yr}_shp.zip"
        elif year == 2010:
            url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_us_050_00_{resolution}.zip"
        elif year in [2011, 2012]:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_county_{resolution}.zip"            
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_county_{resolution}.zip"
            
    else:
        if year == 1990:
            raise ValueError("Please specify `cb = True` to get 1990 data.")
        elif year in [2000, 2010]:
            yr = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/COUNTY/{year}/tl_2010_us_county{yr}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/COUNTY/tl_{year}_us_county.zip"

    ctys = load_tiger(url, cache = cache)

    if state is not None:
        if type(state) is not list:
            state = [state]
        valid_state = [validate_state(x) for x in state]
        ctys = ctys.query('STATEFP in @valid_state')

    return ctys

def tracts(state = None, county = None, cb = False, year = None, cache = False):
    if year is None:
        print("Using the default year of 2021")
        year = 2021

    if state is None:
        if year > 2018 and cb is True:
            state = 'us'
            print("Retrieving Census tracts for the entire United States")
        else:
            raise ValueError("A state is required for this year/dataset combination.")
    else:
        state = validate_state(state)
    
    if cb is True:
        if year in [1990, 2000]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/PREVGENZ/tr/tr{suf}shp/tr{state}_d{suf}_shp.zip"
        elif year == 2010:
            url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_{state}_140_00_500k.zip"
        elif year > 2013:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state}_tract_500k.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_{state}_tract_500k.zip"
    else:
        if year == 1990:
            raise ValueError("Please specify `cb = True` to get 1990 data.")
        elif year in [2000, 2010]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/TRACT/{year}/tl_2010_{state}_tract{suf}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state}_tract.zip"

    trcts = load_tiger(url, cache = cache)

    if county is not None:
        if type(county) is not list:
            county = [county]
        valid_county = [validate_county(state, x) for x in county]
        trcts = trcts.query('COUNTYFP in @valid_county')

    return trcts


def school_districts(state = None, type = "unified", cb = False, year = None, cache = False):
    if year is None:
        print("Using the default year of 2021")
        year = 2021

    if state is None:
        if year > 2018 and cb is True:
            state = "us"
            print("Retrieving school districts for the entire United States")
        else:
            raise ValueError("A state must be specified for this year/dataset combination.")
    else:
        state = validate_state(state)
    
    if type == "unified":
        type = "unsd"
    elif type == "elementary":
        type = "elsd"
    elif type == "secondary":
        type = "scsd"
    else:
        raise ValueError("Invalid school district type.\nValid types are 'unified', 'elementary', and 'secondary'.")

    if cb is True:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state}_{type}_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/{type.upper()}/tl_{year}_{state}_{type}.zip"

    
    return load_tiger(url, cache = cache)


def states(cb = True, resolution = "500k", year = None, cache = False):

    if resolution not in ["500k", "5m", "20m"]:
        raise ValueError("Invalid value for resolution. Valid values are '500k', '5m', and '20m'.")
    
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        if year in [1990, 2000]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/PREVGENZ/st/st{suf}shp/st99_d{suf}_shp.zip"
        elif year == 2010:
            url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_us_040_00_{resolution}.zip"
        else:
            if year > 2013:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_state_{resolution}.zip"
            else:
                url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_state_{resolution}.zip"
    else:
        if year == 1990:
            raise ValueError("Please specify `cb = True` to get 1990 data.")
        elif year in [2000, 2010]:
            suf = str(year)[2:]
            url = f"https://www2.census.gov/geo/tiger/TIGER2010/STATE/{year}/tl_2010_us_state{suf}.zip"
        else:
            url = f"https://www2.census.gov/geo/tiger/TIGER{year}/STATE/tl_{year}_us_state.zip"
    
    return load_tiger(url, cache = cache)