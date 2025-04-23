import requests
import geopandas as gp
import os
import tempfile
import appdirs
import pandas as pd
import re
import ftplib
import zipfile
from urllib.parse import urlparse
from pygris.internal_data import fips_path
from pygris.geocode import geocode

def _load_tiger(url, cache=False, subset_by=None, protocol="http", timeout=1800):
    """
    Helper function to load census TIGER/Line shapefiles.
    
    Parameters
    ----------
    url : str
        URL for zipped shapefile in TIGER database.
    cache : bool
        Whether to cache the shapefile locally. Defaults to False.
    subset_by : tuple, int, slice, dict, geopandas.GeoDataFrame, or geopandas.GeoSeries
        Optional directive for subsetting the data.
    protocol : str
        Protocol to use for downloading files. Options are "http" (default) or "ftp".
    timeout : int
        Timeout in seconds for download operations. Defaults to 300 (5 minutes).
    
    Returns
    -------
    geopandas.GeoDataFrame
        A GeoDataFrame containing the TIGER/Line data.
    """
    # Store original URL before protocol modification
    original_url = url
    
    # Modify URL for FTP if requested
    if protocol == "ftp" and url.startswith("https://www2"):
        url = url.replace("https://www2", "ftp://ftp2")
    
    # Parse the subset_by argument to figure out what it should represent
    if subset_by is not None:
        if type(subset_by) is tuple:
            sub = {"bbox": subset_by}
        elif type(subset_by) is int or type(subset_by) is slice:
            sub = {"rows": subset_by}
        elif type(subset_by) is gp.GeoDataFrame or type(subset_by) is gp.GeoSeries:
            sub = {"mask": subset_by}
        elif type(subset_by) is dict:
            buffers = []
            for i, j in subset_by.items():
                g = geocode(address=i, as_gdf=True, limit=1)
                g_buffer = g.to_crs('ESRI:102010').buffer(distance=j)
                buffers.append(g_buffer)
            
            buffer_gdf = pd.concat(buffers)
            sub = {"mask": buffer_gdf}
    
    # Determine where to save the file
    if cache:
        cache_dir = appdirs.user_cache_dir("pygris")
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)
        basename = os.path.basename(url)
        file_path = os.path.join(cache_dir, basename)
    else:
        # Use a temporary directory if not caching
        tmp_dir = tempfile.gettempdir()
        basename = os.path.basename(url)
        file_path = os.path.join(tmp_dir, basename)
    
    # Download the file if it doesn't exist (or if not using cache)
    download_needed = not os.path.isfile(file_path) if cache else True
    
    if download_needed:
        download_success = False
        
        # Parse the URL to determine protocol and path
        parsed_url = urlparse(url)
        is_ftp = parsed_url.scheme == 'ftp'
        
        # Try with the primary protocol
        try:
            if is_ftp:
                # Handle FTP download with ftplib
                ftp_host = parsed_url.netloc
                ftp_path = os.path.dirname(parsed_url.path)
                filename = os.path.basename(parsed_url.path)
                
                print(f"Downloading {filename} from Census FTP...")
                ftp = ftplib.FTP(ftp_host)
                ftp.login()  # anonymous login
                ftp.cwd(ftp_path)
                
                with open(file_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {filename}', f.write)
                
                ftp.quit()
                download_success = True
            else:
                # Handle HTTP download with requests
                req = requests.get(url=url, timeout=timeout)
                req.raise_for_status()  # Raise an exception for HTTP errors
                
                with open(file_path, 'wb') as fd:
                    fd.write(req.content)
                download_success = True
                
        except Exception as e:
            # If HTTP fails and we're using HTTP, try FTP as fallback
            if protocol == "http" and not is_ftp:
                print("HTTP download failed, trying FTP as fallback...")
                ftp_url = original_url.replace("https://www2", "ftp://ftp2")
                
                try:
                    # Parse the FTP URL
                    parsed_ftp = urlparse(ftp_url)
                    ftp_host = parsed_ftp.netloc
                    ftp_path = os.path.dirname(parsed_ftp.path)
                    filename = os.path.basename(parsed_ftp.path)
                    
                    # Connect to FTP and download
                    print(f"Downloading {filename} from Census FTP...")
                    ftp = ftplib.FTP(ftp_host)
                    ftp.login()  # anonymous login
                    ftp.cwd(ftp_path)
                    
                    with open(file_path, 'wb') as f:
                        ftp.retrbinary(f'RETR {filename}', f.write)
                    
                    ftp.quit()
                    download_success = True
                    
                except Exception as e2:
                    download_success = False
        
        # If both HTTP and FTP failed, raise an error
        if not download_success:
            raise ValueError(
                "Download failed with both HTTP and FTP; check your internet connection or the status of the Census Bureau website "
                "at https://www2.census.gov/geo/tiger/ or ftp://ftp2.census.gov/geo/tiger/."
            )
    
    # Read the file from the local filesystem
    try:
        if subset_by is not None:
            tiger_data = gp.read_file(file_path, **sub)
        else:
            tiger_data = gp.read_file(file_path)
        
        # Clean up temporary file if not caching
        if not cache and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore errors in cleanup
                
        return tiger_data
    
    except Exception as e:
        # If the file is corrupted, remove it and try downloading again
        if cache and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print("Cached file may be corrupted. Downloading again...")
                return _load_tiger(original_url, cache=cache, subset_by=subset_by, protocol=protocol, timeout=timeout)
            except:
                pass
        raise e

def fips_codes():
    path = fips_path()

    return pd.read_csv(path, dtype = 'object')

def validate_state(state, quiet = False):
    # Standardize as lowercase
    original_input = state
    if isinstance(state, str):
        state = str(state).lower()
        # Get rid of whitespace
        state = state.strip()
        if state.isdigit():
            # Left-pad if necessary
            state = state.zfill(2)
            # Return the result
            return state

    # If the FIPS code is supplied as an int
    elif isinstance(state, int):
        #convert to string
        state=str(state)
        # Left-pad if necessary
        state = state.zfill(2)
        # Return the result
        return state

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



