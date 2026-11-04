try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

def fips_path():
    return files("pygris.internals").joinpath("fips_codes.csv")
