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
    print("Google LOC is disabled for the time being (in order to not accidentally put myself in debt)")
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

def get_location(address, api_key) -> dict[str, float] | None:
    global current_requests
    
    if current_requests >= REQUEST_LIMIT:
        print("Cannot do more requests: over the limit")
        return None
    
    URL = "https://geocode.search.hereapi.com/v1/geocode"
    
    current_requests += 1
    
    req_params = {'apikey': api_key, 'q': address + " Madrid, Spain"}
    try:
        response = requests.get(url=URL, params=req_params).json()
    except ConnectionError:
        return None
    
    try:
        if len(response['items']) == 0:
            return None
        position = response['items'][0]['position']
    except KeyError:
        print(response)
        return None
    
    return {'lat': position['lat'], 'lng': position['lng']}

def transform_location_to_format(location) -> dict[str, float]:
    if isinstance(location, list):
        return {'lat': location[0], 'lng': location[1]}
    elif isinstance(location, dict):
        return location
    raise ValueError("Invalid location type")

df_houses = pd.read_csv("houses_Madrid.csv")

df_unique_districts = df_houses['neighborhood_id'].unique()

df_streets = df_houses['street_name'] + ', ' + df_houses['street_number'].astype(str)
# not '.unique', because I want to retain indices
df_streets_unique = df_streets.drop_duplicates()

neighborhood_locations = {}
street_locations = {}

SAVE_FILE = 'street_locations_UT.json'

try:
    with open(SAVE_FILE, 'r') as f:
        street_locations = json.load(f)
except FileNotFoundError:
    pass

# fix location's data
for location_info in street_locations.values():
    location_info['loc'] = transform_location_to_format(location_info['loc'])
    
try:
    answer = input("Are you sure you want to lose money? (yes/no): ")
    
    if answer != 'yes':
        print("Smart choice...")
        exit(0)
    """
    # Code for neighborhoods
    print("Loading neighborhoods")
    for neighborhood in df_unique_districts:
        neighborhood_locations[neighborhood] = get_location(neighborhood, API_KEY)
        print(f"Loaded {neighborhood}")
    """
    for idx, street in df_streets_unique.items():
        if not isinstance(street, str):
            print(f"({idx}) Skipped {street}")
            continue
        
        # remove nan for approximate search
        if street[-5:] == ', nan':
            street = street[:-5]
        
        # if street already loaded, skip
        if street in street_locations.keys():
            print(f"({idx}) Skipped {street}")
            #street_locations[street]['idx'] = idx
            continue
        
        try:
            loc = get_location(street, ENVIRONMENT['API_KEY'])
            if loc is None:
                print(f"({idx}) Failed to get location of {street}. Skipping...")
                continue
            street_locations[street] = {'loc': loc, 'idx': idx}
        except KeyError:
            print(f"({idx}) Failed to get location of {street}. Skipping...")
            continue
        print(f"({idx}) Loaded {street}")
except KeyboardInterrupt:
    # Stop loading after keyboard interrupt and just proceed to saving
    print("Further API queries are cancelled.")
except Exception as e: # I should've done this sooner
    print(f"Error occured: {e}")
finally:
    print("Finished loading")

with open(SAVE_FILE, "w") as f:
    f.write(json.dumps(street_locations))

print(f"File saved successfully as {SAVE_FILE}")
