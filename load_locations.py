import requests
import numpy as np
import dotenv
import pandas as pd
import json

# Load environment from .env file to load API_KEY
ENVIRONMENT = dotenv.dotenv_values()

API_KEY = ENVIRONMENT['API_KEY']

def get_location(address, api_key) -> tuple[float, float] | None:
    URL = "https://geocode.search.hereapi.com/v1/geocode"
    
    req_params = {'apikey': api_key, 'q': address + " Madrid, Spain"}
    response = requests.get(url=URL, params=req_params).json()
    
    if len(response['items']) == 0:
        return None
    
    position = response['items'][0]['position']
    
    return (position['lat'], position['lng'])

df_houses = pd.read_csv("houses_Madrid.csv")

df_unique_districts = df_houses['neighborhood_id'].unique()

neighborhood_locations = {}

try:
    for neighborhood in df_unique_districts:
        neighborhood_locations[neighborhood] = get_location(neighborhood, API_KEY)
        print(f"Loaded {neighborhood}")
except KeyboardInterrupt:
    # Stop loading after keyboard interrupt and just proceed to saving
    print("Further API queries are cancelled")

print("Finished loading")

SAVE_FILE = 'saved_locations_UT.json'

with open(SAVE_FILE, "w") as f:
    f.write(json.dumps(neighborhood_locations))

print(f"File saved successfully as {SAVE_FILE}")
