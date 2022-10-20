from pygris.helpers import _load_tiger

def native_areas(cb = False, year = None, cache = False):
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_aiannh_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/AIANNH/tl_{year}_us_aiannh.zip"
    
    return _load_tiger(url, cache = cache)


def tribal_subdivisions_national(cb = False, year = None, cache = False):
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

    return _load_tiger(url, cache = cache)


def alaska_native_regional_corporations(cb = False, year = None, cache = False):
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_02_anrc_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ANRC/tl_{year}_02_anrc.zip"
    
    return _load_tiger(url, cache = cache)


def tribal_block_groups(cb = False, year = None, cache = False):
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_tbg_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TBG/tl_{year}_us_tbg.zip"
    
    return _load_tiger(url, cache = cache)



def tribal_tracts(cb = False, year = None, cache = False):
    if year is None:
        print("Using the default year of 2021")
        year = 2021
    
    if cb:
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_ttract_500k.zip"
    else:
        url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TTRACT/tl_{year}_us_ttract.zip"
    
    return _load_tiger(url, cache = cache)