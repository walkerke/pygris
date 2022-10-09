# import requests
# import pandas as pd
# import json

# def geocode(address, benchmark = 2020, output = "locations", 
#             vintage = None):

#     url = f"https://geocoding.geo.census.gov/geocoder/{output}/onelineaddress"

#     req = requests.get(url = url, 
#                        params = {"address": address,
#                         "benchmark": benchmark,
#                         "vintage": vintage,
#                         "format": "json"})

#     if req.status_code != 200:
#         raise SyntaxError(f"Your request failed. The error message is {req.text}")
    
#     r = json.load(req.text)

