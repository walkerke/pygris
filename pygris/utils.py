from pygris.enumeration_units import counties
from pygris.water import area_water
import warnings
import pandas as pd
def erase_water(input, area_threshold = 0.75, year = None, cache = False):
    if year is None:
        year = 2021

    # Get a dataset of US counties
    us_counties = counties(cb = True, resolution = "500k", year = year)

    # Find the county GEOIDs that overlap the input object
    with warnings.catch_warnings():
        county_proj = us_counties.to_crs(input.crs)
        county_overlaps = county_proj.overlay(input, keep_geom_type = False)

    county_ids = county_overlaps.GEOID_1.unique().tolist()

    if len(county_ids) == 0:
        raise ValueError("Your dataset does not appear to be in the United States; this function is not appropriate for your data.")

    water_list = []

    for i in county_ids:
        state = i[0:2]
        county = i[2:]

        water = area_water(state = state, county = county, year = year, cache = cache)

        water_proj = water.to_crs(input.crs)

        water_list.append(water)

    all_water = pd.concat(water_list, ignore_index = True)

    all_water['water_rank'] = all_water.AWATER.rank(pct = True)

    water_thresh = all_water.query('water_rank >= @area_threshold')

    # Erase the water area

    erased = input.overlay(water_thresh, how = "difference")

    return erased


