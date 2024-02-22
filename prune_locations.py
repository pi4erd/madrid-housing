"""Check all locations in file and if any are ridiculous, delete them
"""

from math import sqrt
import json
import re

CENTER = {"lat": 40.43058270719132, "lng": -3.696461859683753}
LIMIT_POINT = {"lat": 40.36802875457529, "lng": -4.158458115221}

def calculate_distance(p1: dict[str, float], p2: dict[str, float]) -> float:
    diff = {"lat": p1["lat"] - p2["lat"], "lng": p1["lng"] - p2["lng"]}
    return sqrt(diff['lat'] ** 2 + diff["lng"] ** 2)

MAX_DISTANCE = calculate_distance(CENTER, LIMIT_POINT)

street_locations = {}

with open("street_locations_UT.json", 'r') as f:
    street_locations = json.load(f)

new_street_locations = {}

for street in street_locations:
    if calculate_distance(street_locations[street]['loc'], CENTER) > MAX_DISTANCE:
        print(f"Pruning {street} ({street_locations[street]['loc']})")
        answer = input("Are you sure (yes/no): ")
        
        if re.match(r"y(?:es|)", answer, re.IGNORECASE) is not None :
            print(f"Pruned {street} ({street_locations[street]['loc']})")
            continue
        print(f"Skipped pruning {street} ({street_locations[street]['loc']})")
    new_street_locations[street] = street_locations[street]

print(f"Old size: {len(street_locations)}. New size: {len(new_street_locations)}")
print("Saving street_locations.json...")

with open("street_locations.json", "w") as f:
    f.write(json.dumps(new_street_locations))

print("File saved successfully!")
