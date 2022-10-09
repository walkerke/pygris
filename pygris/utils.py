from pygris.enumeration_units import counties, states
from pygris.water import area_water
import warnings
import pandas as pd
import geopandas as gp
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


def shift_geometry(input, geoid_column = None, preserve_area = False, position = "below"):

    minimal_states = states(cb = True, resolution = "20m", year = 2021).to_crs('ESRI:102003')

    ak_bbox = gp.GeoDataFrame(geometry = minimal_states.query("GEOID == '02'").envelope)
    hi_bbox = gp.GeoDataFrame(geometry = minimal_states.query("GEOID == '15'").envelope)
    pr_bbox = gp.GeoDataFrame(geometry = minimal_states.query("GEOID == '72'").envelope)

    boxes = pd.concat([ak_bbox, hi_bbox, pr_bbox])

    boxes['state_fips'] = ['02', '15', '72']

    input_albers = input.to_crs(minimal_states.crs)

    if geoid_column is not None:
        input_albers['state_fips'] = input_albers[geoid_column].str.slice(0, 2)
    else:
        input_albers = input_albers.sjoin(boxes, how = "left")

        input_albers['state_fips'].fillna("00")
    
    # Alaska/Hawaii/PR centroids are necessary to put any dataset in the correct location
    ak_crs = 3338
    hi_crs = 'ESRI:102007'
    pr_crs = 32161

    ak_centroid = minimal_states.query("GEOID == '02'").to_crs(ak_crs).centroid
    hi_centroid = minimal_states.query("GEOID == '15'").to_crs(hi_crs).centroid
    pr_centroid = minimal_states.query("GEOID == '72'").to_crs(pr_crs).centroid

    def place_geometry_wilke(geometry, position, centroid, scale = 1):
        diff = geometry.translate(xoff = -centroid.x, yoff = -centroid.y)
        scaled = diff.scale(xfact = scale, yfact = scale)
        return scaled.translate(xoff = position[0], yoff = position[1])

    bb = minimal_states.query('GEOID not in ["02", "15", "72"]', engine = "python").total_bounds

    us_lower48 = input_albers.query('state_fips not in ["02", "15", "72"]', engine = "python")

    us_alaska = input_albers.query('state_fips == "02"')
    us_hawaii = input_albers.query('state_fips == "15"')
    us_puerto_rico = input_albers.query('state_fips == "72"')

    if pd.concat([us_alaska, us_hawaii, us_puerto_rico]).shape[0] == 0:
        UserWarning("None of your features are in Alaska, Hawaii, or Puerto Rico, so no geometries will be shifted.\nTransforming your object's CRS to 'ESRI:102003'")
        return input_albers.drop('state_fips', axis = 1)
    
    shapes_list = [us_lower48]

    if not preserve_area:
        if us_alaska.shape[0] > 0:
            ak_rescaled = us_alaska.to_crs(ak_crs)

            if position == "below":
                ak_rescaled.geometry = place_geometry_wilke(
                    geometry = ak_rescaled.geometry,
                    position = [bb[0] + 0.10 * (bb[2] - bb[0]), bb[1] + 0.15 * (bb[3] - bb[1])],
                    scale = 0.5,
                    centroid = ak_centroid)

            elif position == "outside":
                ak_rescaled.geometry = place_geometry_wilke(
                    geometry = ak_rescaled.geometry,
                    position = [bb[0] - 0.08 * (bb[2] - bb[0]), bb[1] + 1.2 * (bb[3] - bb[1])],
                    scale = 0.5,
                    centroid = ak_centroid)
            
            ak_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(ak_rescaled)
        
        if us_hawaii.shape[0] > 0:
            
            hi_rescaled = us_hawaii.overlay(hi_bbox).to_crs(hi_crs)

            if position == "below":
                hi_rescaled.geometry = place_geometry_wilke(
                    geometry = hi_rescaled.geometry,
                    position = [bb[0] + 0.35 * (bb[2] - bb[0]), bb[1] + 0.0 * (bb[3] - bb[1])],
                    scale = 1.5,
                    centroid = hi_centroid)
            elif position == "outside":
                hi_rescaled.geometry = place_geometry_wilke(
                    geometry = hi_rescaled.geometry,
                    position = [bb[0] - 0.0 * (bb[2] - bb[0]), bb[1] + 0.2 * (bb[3] - bb[1])],
                    scale = 1.5,
                    centroid = hi_centroid)
            
            hi_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(hi_rescaled)

        if us_puerto_rico.shape[0] > 0:
            pr_rescaled = us_puerto_rico.to_crs(pr_crs)

            if position == "below":
                pr_rescaled.geometry = place_geometry_wilke(
                    geometry = pr_rescaled.geometry,
                    position = [bb[0] + 0.65 * (bb[2] - bb[0]), bb[1] + 0.0 * (bb[3] - bb[1])],
                    scale = 2.5,
                    centroid = pr_centroid)
            elif position == "outside":
                pr_rescaled.geometry = place_geometry_wilke(
                    geometry = pr_rescaled.geometry,
                    position = [bb[0] + 0.95 * (bb[2] - bb[0]), bb[1] - 0.05 * (bb[3] - bb[1])],
                    scale = 2.5,
                    centroid = pr_centroid)
            
            pr_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(pr_rescaled)
        
        output_data = pd.concat(shapes_list).drop('state_fips', axis = 1)

        return output_data

    else:
        if us_alaska.shape[0] > 0:
            ak_rescaled = us_alaska.to_crs(ak_crs)

            if position == "below":
                ak_rescaled.geometry = place_geometry_wilke(
                    geometry = ak_rescaled.geometry,
                    position = [bb[0] + 0.2 * (bb[2] - bb[0]), bb[1] - 0.13 * (bb[3] - bb[1])],
                    scale = 1,
                    centroid = ak_centroid)

            elif position == "outside":
                ak_rescaled.geometry = place_geometry_wilke(
                    geometry = ak_rescaled.geometry,
                    position = [bb[0] - 0.25 * (bb[2] - bb[0]), bb[1] + 1.35 * (bb[3] - bb[1])],
                    scale = 1,
                    centroid = ak_centroid)
            
            ak_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(ak_rescaled)
        
        if us_hawaii.shape[0] > 0:
            hi_rescaled = us_hawaii.overlay(hi_bbox).to_crs(hi_crs)

            if position == "below":
                hi_rescaled.geometry = place_geometry_wilke(
                    geometry = hi_rescaled.geometry,
                    position = [bb[0] + 0.6 * (bb[2] - bb[0]), bb[1] - 0.1 * (bb[3] - bb[1])],
                    scale = 1,
                    centroid = hi_centroid)
            elif position == "outside":
                hi_rescaled.geometry = place_geometry_wilke(
                    geometry = hi_rescaled.geometry,
                    position = [bb[0] - 0.0 * (bb[2] - bb[0]), bb[1] + 0.2 * (bb[3] - bb[1])],
                    scale = 1,
                    centroid = hi_centroid)
            
            hi_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(hi_rescaled)

        if us_puerto_rico.shape[0] > 0:
            pr_rescaled = us_puerto_rico.to_crs(pr_crs)

            if position == "below":
                pr_rescaled.geometry = place_geometry_wilke(
                    geometry = pr_rescaled.geometry,
                    position = [bb[0] + 0.75 * (bb[2] - bb[0]), bb[1] - 0.1 * (bb[3] - bb[1])],
                    scale = 2,
                    centroid = pr_centroid)
            elif position == "outside":
                pr_rescaled.geometry = place_geometry_wilke(
                    geometry = pr_rescaled.geometry,
                    position = [bb[0] + 0.95 * (bb[2] - bb[0]), bb[1] - 0.05 * (bb[3] - bb[1])],
                    scale = 1,
                    centroid = pr_centroid)
            
            pr_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(pr_rescaled)
        
        output_data = pd.concat(shapes_list).drop('state_fips', axis = 1)

        return output_data
