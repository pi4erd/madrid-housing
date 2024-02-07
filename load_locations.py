import requests
import numpy as np
import dotenv
import pandas as pd
import json
import urllib.parse

# Load environment from .env file to load API_KEY
ENVIRONMENT = dotenv.dotenv_values()

API_KEY = ENVIRONMENT['API_KEY']

REQUEST_LIMIT = 1000
current_requests = 0

def get_location_google(address: str, api_key) -> dict[str, float] | None:
    print("Google LOC is disable for the time being")
    return None
    
    global current_requests
    
    if current_requests >= REQUEST_LIMIT:
        print("Cannot do more requests: over the limit")
        return None
    
    current_requests += 1
    
    URL = "https://maps.googleapis.com/maps/api/geocode/json"
    
    address = address + " Madrid, Spain"
    url_encode_address = urllib.parse.quote(address)
    
    req_params_google = {'key': api_key, 'address': url_encode_address}
    response = requests.get(url=URL, params=req_params_google).json()
    
    try:
        if len(response['results']) == 0:
            return None
        lonlat = response['results'][0]['geometry']['location']
        return lonlat
    except KeyError:
        return None

def get_location(address, api_key) -> tuple[float, float] | None:
    global current_requests
    
    if current_requests >= REQUEST_LIMIT:
        print("Cannot do more requests: over the limit")
        return None
    
    URL = "https://geocode.search.hereapi.com/v1/geocode"
    
    current_requests += 1
    
    req_params = {'apikey': api_key, 'q': address + " Madrid, Spain"}
    response = requests.get(url=URL, params=req_params).json()
    
    try:
        if len(response['items']) == 0:
            return None
    except KeyError:
        print(response)
        return None
    
    position = response['items'][0]['position']
    
    return (position['lat'], position['lng'])

df_houses = pd.read_csv("houses_Madrid.csv")

df_unique_districts = df_houses['neighborhood_id'].unique()

df_streets = df_houses['street_name'] + ', ' + df_houses['street_number'].astype(str)
df_streets_unique = df_streets.unique()

neighborhood_locations = {}
street_locations = {}

SAVE_FILE = 'street_locations_UT.json'

try:
    with open(SAVE_FILE, 'r') as f:
        street_locations = json.load(f)
except FileNotFoundError:
    pass

try:
    answer = input("Are you sure you want to lose money? (yes/no): ")
    
    if answer != 'yes':
        print("Smart choice...")
        exit(0)
    """
    print("Loading neighborhoods")
    for neighborhood in df_unique_districts:
        neighborhood_locations[neighborhood] = get_location(neighborhood, API_KEY)
        print(f"Loaded {neighborhood}")
    """
    for idx, street in enumerate(df_streets_unique, start=1):
        if not isinstance(street, str):
            print(f"({idx}) Skipped {street}")
            continue
        
        # remove nan for approximate search
        if street[-5:] == ', nan':
            street = street[:-5]
        
        # if street already loaded, skip
        if street in street_locations.keys():
            print(f"({idx}) Skipped {street}")
            continue
        
        try:
            loc = get_location(street, ENVIRONMENT['API_KEY'])
            if loc is None:
                print(f"({idx}) Failed to get location of {street}. Skipping...")
                continue
            street_locations[street] = loc
        except KeyError:
            print(f"({idx}) Failed to get location of {street}. Skipping...")
            continue
        print(f"({idx}) Loaded {street}")
except KeyboardInterrupt:
    # Stop loading after keyboard interrupt and just proceed to saving
    print("Further API queries are cancelled")

print("Finished loading")

with open(SAVE_FILE, "w") as f:
    f.write(json.dumps(street_locations))

print(f"File saved successfully as {SAVE_FILE}")
