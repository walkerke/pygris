from pygris.enumeration_units import counties, tracts, block_groups, blocks


# Helper function to get geometry (LODES-only for now)
def _get_geometry(geography, state, year, cb, cache):
    if geography == "county":
        geo = counties(cb = cb, state = state, year = year, cache = cache)
    elif geography == "tract":
        geo = tracts(cb = cb, state = state, year = year, cache = cache)
    elif geography == "block group":
        geo = block_groups(cb = cb, state = state, year = year, cache = cache)
    elif geography == "block":
        geo = blocks(state = state, year = year, cache = cache)
    

    geo_sub = geo.filter(['GEOID', 'geometry'])

    return geo_sub