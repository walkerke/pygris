"""Utility functions for working with Census datasets"""

__author__ = "Kyle Walker <kyle@walker-data.com>"

from pygris.enumeration_units import counties, states
from pygris.water import area_water
import warnings
import pandas as pd
import geopandas as gp
def erase_water(input, area_threshold = 0.75, year = None, cache = False):
    """
    Automate the process of removing water area from an input dataset

    Parameters
    -------------
    input : geopandas.GeoDataFrame
        An input dataset from which you would like to remove water area.  The input dataset 
        should be in the United States, ideally retrieved with the pygris package
        for best performance.  
    
    area_threshold : float
        A proportion between 0 and 1 that references the water area threshold
        to be used in the erase operation.  A value of 0 will use all water area;
        a value of 1 will use none of the water area.  Typically, a user will specify 
        a higher value to erase only the largest water areas, as erasing small areas 
        will slow performance of the function. Defaults to 0.75.  

    year : int
        The year of the TIGER/Line water dataset to use.  Defaults to 2021. 
        To minimize sliver polygons, choose the same year as your input 
        pygris dataset.  

    cache : bool
        If True, area water files in the vicinity of input will be downloaded 
        to a cache directory on the user's computer, or read from that cache directory.
        This option is recommended for best performance.  

    Returns
    --------------
    An object of type geopandas.GeoDataFrame with water area removed.

    Notes
    --------------
    For a given input polygon spatial dataset in the United States, this function fetches water for 
    nearby counties and removes those water areas from the input polygons.  Performance 
    will likely be best when polygons are retrieved with the argument `cb = True` and 
    the `year` argument aligns with that of the input polygons.  Sliver polygons due to 
    misalignment are always possible; it is recommended to inspect your data after running 
    this function.  
    """
    if year is None:
        year = 2021

    # Get a dataset of US counties
    us_counties = counties(cb = True, resolution = "500k", year = year)

    # Find the county GEOIDs that overlap the input object
    with warnings.catch_warnings():
        county_proj = us_counties.to_crs(input.crs)
        county_proj['county_id'] = county_proj['GEOID']
        county_overlaps = county_proj.overlay(input, keep_geom_type = False)

    county_ids = county_overlaps['county_id'].unique().tolist()

    if len(county_ids) == 0:
        raise ValueError("Your dataset does not appear to be in the United States; this function is not appropriate for your data.")

    water_list = []

    for i in county_ids:
        state = i[0:2]
        county = i[2:]

        water = area_water(state = state, county = county, year = year, cache = cache)

        water_proj = water.to_crs(input.crs)

        water_list.append(water_proj)

    all_water = pd.concat(water_list, ignore_index = True)

    all_water['water_rank'] = all_water.AWATER.rank(pct = True)

    water_thresh = all_water.query('water_rank >= @area_threshold')

    # Erase the water area

    erased = input.overlay(water_thresh, how = "difference")

    return erased


def shift_geometry(input, geoid_column = None, preserve_area = False, position = "below"):
    """
    Shift and optionally rescale Alaska, Hawaii, and Puerto Rico for better cartographic display

    Parameters
    ---------------
    input : geopandas.GeoDataFrame
        A dataset of features in the United States to shift / rescale. 

    geoid_column : str, optional
        An optional column in the dataset that provides a state FIPS code. If used, avoids spatial 
        overlay to identify features and can speed processing.  

     preserve_area : bool
        Whether or not to preserve the area of Alaska, Hawaii, and Puerto Rico when re-arranging 
        features.  If False, Alaska will be shrunk to about half its size; Hawaii will be 
        rescaled to 1.5x its size, and Puerto Rico will be rescaled to 2.5x its size. 
        If True, sizes of Alaska, Hawaii, and Puerto Rico relative to the continental United 
        States will be preserved.  Defaults to False. 

    position : str
        One of "below" (the default), which moves features in Alaska, Hawaii, and Puerto Rico below the 
        continental United States; or "outside", which places features outside the 
        continental US in locations that correspond roughly to their actual geographic 
        positions.  

    Returns
    -----------
    The original input dataset with shifted / rescaled geometry.

    Notes
    -----------
    `shift_geometry()`, while designed for use with objects from the pygris package, will work with any US
    dataset. If aligning datasets from multiple sources, you must take care to ensure that your options
    specified in `preserve_area` and `position` are identical across layers.  Otherwise your layers
    will not align correctly.

    The function is also designed to work exclusively with features in the continental United States,
    Alaska, Hawaii, and Puerto Rico.  If your dataset includes features outside these areas (e.g. other
    US territories or other countries), you may get unworkable results.  It is advisable to filter out
    those features before using ``shift_geometry()`.

    Work on this function is inspired by and adapts some code from Claus Wilke's book Fundamentals of
    Data Visualization (https://clauswilke.com/dataviz/geospatial-data.html); Bob Rudis's
    albersusa R package (https://github.com/hrbrmstr/albersusa); and the ggcart R package
    (https://uncoast-unconf.github.io/ggcart/).
    
    """

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

        input_albers['state_fips'] = input_albers['state_fips'].fillna("00")
    
    # Alaska/Hawaii/PR centroids are necessary to put any dataset in the correct location
    ak_crs = 3338
    hi_crs = 'ESRI:102007'
    pr_crs = 32161

    ak_centroid = minimal_states.query("GEOID == '02'").to_crs(ak_crs).centroid
    hi_centroid = minimal_states.query("GEOID == '15'").to_crs(hi_crs).centroid
    pr_centroid = minimal_states.query("GEOID == '72'").to_crs(pr_crs).centroid

    def place_geometry_wilke(geometry, position, centroid, scale = 1):
        centroid_x = centroid.x.values[0]
        centroid_y = centroid.y.values[0]
        diff = geometry.translate(xoff = -centroid_x, yoff = -centroid_y)
        scaled = diff.scale(xfact = scale, yfact = scale, origin = (centroid_x, centroid_y))
        return scaled.translate(xoff = position[0], yoff = position[1])

    bb = minimal_states.query('GEOID not in ["02", "15", "72"]', engine = "python").total_bounds

    us_lower48 = input_albers.query('state_fips not in ["02", "15", "72"]', engine = "python")

    us_alaska = input_albers.query('state_fips == "02"')
    us_hawaii = input_albers.query('state_fips == "15"')
    us_puerto_rico = input_albers.query('state_fips == "72"')

    if pd.concat([us_alaska, us_hawaii, us_puerto_rico]).shape[0] == 0:
        UserWarning("None of your features are in Alaska, Hawaii, or Puerto Rico, so no geometries will be shifted.\nTransforming your object's CRS to 'ESRI:102003'")
        return input_albers.drop(['state_fips', 'index_right'], axis = 1)
    
    shapes_list = [us_lower48]

    if not preserve_area:
        if us_alaska.shape[0] > 0:
            ak_rescaled = us_alaska.to_crs(ak_crs)

            if position == "below":
                ak_rescaled.geometry = place_geometry_wilke(
                    geometry = ak_rescaled.geometry,
                    position = [bb[0] + 0.06 * (bb[2] - bb[0]), bb[1] - 0.14 * (bb[3] - bb[1])],
                    scale = 0.5,
                    centroid = ak_centroid)

            elif position == "outside":
                ak_rescaled.geometry = place_geometry_wilke(
                    geometry = ak_rescaled.geometry,
                    position = [bb[0] - 0.08 * (bb[2] - bb[0]), bb[1] + 0.92 * (bb[3] - bb[1])],
                    scale = 0.5,
                    centroid = ak_centroid)
            
            ak_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(ak_rescaled)
        
        if us_hawaii.shape[0] > 0:
            
            hi_rescaled = us_hawaii.overlay(hi_bbox).to_crs(hi_crs)

            if position == "below":
                hi_rescaled.geometry = place_geometry_wilke(
                    geometry = hi_rescaled.geometry,
                    position = [bb[0] + 0.32 * (bb[2] - bb[0]), bb[1] + 0.2 * (bb[3] - bb[1])],
                    scale = 1.5,
                    centroid = hi_centroid)
            elif position == "outside":
                hi_rescaled.geometry = place_geometry_wilke(
                    geometry = hi_rescaled.geometry,
                    position = [bb[0] + 0.05 * (bb[2] - bb[0]), bb[1] + 0.35 * (bb[3] - bb[1])],
                    scale = 1.5,
                    centroid = hi_centroid)
            
            hi_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(hi_rescaled)

        if us_puerto_rico.shape[0] > 0:
            pr_rescaled = us_puerto_rico.to_crs(pr_crs)

            if position == "below":
                pr_rescaled.geometry = place_geometry_wilke(
                    geometry = pr_rescaled.geometry,
                    position = [bb[0] + 0.75 * (bb[2] - bb[0]), bb[1] + 0.15 * (bb[3] - bb[1])],
                    scale = 2.5,
                    centroid = pr_centroid)
            elif position == "outside":
                pr_rescaled.geometry = place_geometry_wilke(
                    geometry = pr_rescaled.geometry,
                    position = [bb[0] + 1.0 * (bb[2] - bb[0]), bb[1] + 0.05 * (bb[3] - bb[1])],
                    scale = 2.5,
                    centroid = pr_centroid)
            
            pr_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(pr_rescaled)
        
        output_data = pd.concat(shapes_list).drop(['state_fips', 'index_right'], axis = 1)

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
                    scale = 1,
                    centroid = pr_centroid)
            elif position == "outside":
                pr_rescaled.geometry = place_geometry_wilke(
                    geometry = pr_rescaled.geometry,
                    position = [bb[0] + 0.95 * (bb[2] - bb[0]), bb[1] - 0.05 * (bb[3] - bb[1])],
                    scale = 1,
                    centroid = pr_centroid)
            
            pr_rescaled.set_crs('ESRI:102003', inplace = True, allow_override = True)

            shapes_list.append(pr_rescaled)
        
        output_data = pd.concat(shapes_list).drop(['state_fips', 'index_right'], axis = 1)

        return output_data
