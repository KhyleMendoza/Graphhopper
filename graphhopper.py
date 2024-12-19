import requests
import urllib.parse
from tabulate import tabulate

geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"
key = "3e362481-1590-4c04-a78c-e46fa8b12184"

def geocoding(location, key):
    while True:
        if location.strip() == "":
            location = input("Location cannot be empty. Please enter the location again: ")
        url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
        replydata = requests.get(url)
        json_data = replydata.json()
        json_status = replydata.status_code
        if json_status == 200 and len(json_data["hits"]) != 0:
            lat = json_data["hits"][0]["point"]["lat"]
            lng = json_data["hits"][0]["point"]["lng"]
            name = json_data["hits"][0]["name"]
            value = json_data["hits"][0].get("osm_value", "")
            country = json_data["hits"][0].get("country", "")
            state = json_data["hits"][0].get("state", "")

            if state and country:
                new_loc = f"{name}, {state}, {country}"
            elif country:
                new_loc = f"{name}, {country}"
            else:
                new_loc = name

            print(f"Geocoding API URL for {new_loc} (Location Type: {value})\n{url}")
            return json_status, lat, lng, new_loc
        else:
            print(f"{location} doesn't exist. Please try again.")
            location = input("Enter the location again: ")

while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    profile = ["car", "bike", "foot"]
    vehicle = input("Enter a vehicle profile from the list above: ").strip().lower()
    if vehicle in ["quit", "q"]:
        break
    elif vehicle not in profile:
        vehicle = "car"
        print("No valid vehicle profile was entered. Using the car profile.")

    loc1 = input("Starting Location: ").strip()
    if loc1 in ["quit", "q"]:
        break
    orig = geocoding(loc1, key)

    loc2 = input("Destination: ").strip()
    if loc2 in ["quit", "q"]:
        break
    dest = geocoding(loc2, key)

    print("=================================================")
    if orig[0] == 200 and dest[0] == 200:
        op = f"&point={orig[1]}%2C{orig[2]}"
        dp = f"&point={dest[1]}%2C{dest[2]}"
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
        paths_response = requests.get(paths_url)
        paths_status = paths_response.status_code
        paths_data = paths_response.json()

        print(f"Routing API Status: {paths_status}\nRouting API URL:\n{paths_url}")
        print("=================================================")
        print(f"Directions from {orig[3]} to {dest[3]} by {vehicle}")
        print("=================================================")

        if paths_status == 200:
            miles = paths_data["paths"][0]["distance"] / 1000 / 1.61
            km = paths_data["paths"][0]["distance"] / 1000
            sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
            mins = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
            hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)

            summary_table = [
                ["Distance (miles)", f"{miles:.1f}"],
                ["Distance (km)", f"{km:.1f}"],
                ["Trip Duration (HH:MM:SS)", f"{hr:02d}:{mins:02d}:{sec:02d}"],
            ]
            print(tabulate(summary_table, headers=["Metric", "Value"], tablefmt="grid"))

            instructions_table = [
                [each["text"], f"{each['distance']/1000:.1f} km", f"{each['distance']/1000/1.61:.1f} miles"]
                for each in paths_data["paths"][0]["instructions"]
            ]
            print(tabulate(instructions_table, headers=["Instruction", "Distance (km)", "Distance (miles)"], tablefmt="grid"))
        else:
            print(f"Error message: {paths_data.get('message', 'Unknown error')}")
            print("*************************************************")
