from importlib import resources

def fips_path():
    with resources.path("pygris.data", "fips_codes.csv") as path:
        data_file_path = path
        return data_file_path