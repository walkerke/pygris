from importlib import resources

def fips_path():
    return resources.files("pygris.internals").joinpath("fips_codes.csv")
