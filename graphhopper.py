import requests
import urllib.parse
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"
key = "3e362481-1590-4c04-a78c-e46fa8b12184"

def geocoding(location, key):
    while True:
        if location.strip() == "":
            location = input(Fore.RED + "Location cannot be empty. Please enter the location again: ")
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

            print(Fore.BLUE + f"Geocoding API URL for {new_loc} (Location Type: {value}): {url}")
            return json_status, lat, lng, new_loc
        else:
            print(Fore.RED + f"{location} doesn't exist. Please try again.")
            location = input("Enter the location again: ")

while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("🚗 car, 🚴 bike, 🚶 foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    profile = ["car", "bike", "foot"]
    vehicle = input("Enter a vehicle profile from the list above: ").strip().lower()
    if vehicle in ["quit", "q"]:
        print("Goodbye!")
        break
    elif vehicle not in profile:
        vehicle = "car"
        print(Fore.YELLOW + "No valid vehicle profile was entered. Defaulting to 'car' profile.")

    loc1 = input("📍 Starting Location: ").strip()
    if loc1 in ["quit", "q"]:
        print("Goodbye!")
        break
    orig = geocoding(loc1, key)

    loc2 = input("📍 Destination: ").strip()
    if loc2 in ["quit", "q"]:
        print("Goodbye!")
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

        print(f"Routing API Status: {paths_status}")
        print("Routing API URL:")
        print(Fore.CYAN + f"{paths_url}")
        print("=================================================")
        print(Fore.GREEN + f"Directions from {orig[3]} to {dest[3]} by {vehicle}")
        print("=================================================")

        if paths_status == 200:
            miles = paths_data["paths"][0]["distance"] / 1000 / 1.61
            km = paths_data["paths"][0]["distance"] / 1000
            sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
            mins = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
            hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)

            summary_table = [
                [Fore.WHITE + "Distance (miles)" + Fore.YELLOW, Fore.WHITE + f"{miles:.1f}" + Fore.YELLOW],
                [Fore.WHITE + "Distance (km)" + Fore.YELLOW, Fore.WHITE + f"{km:.1f}" + Fore.YELLOW],
                [Fore.WHITE + "Trip Duration (HH:MM:SS)" + Fore.YELLOW, Fore.WHITE + f"{hr:02d}:{mins:02d}:{sec:02d}" + Fore.YELLOW],
            ]
            print(Fore.YELLOW + tabulate(summary_table, headers=[Fore.WHITE + "Metric" + Fore.YELLOW, Fore.WHITE + "Value" + Fore.YELLOW], tablefmt="grid"))

            instructions_table = [
                [Fore.WHITE + each["text"] + Fore.CYAN, Fore.WHITE + f"{each['distance']/1000:.1f} km" + Fore.CYAN, Fore.WHITE + f"{each['distance']/1000/1.61:.1f} miles" + Fore.CYAN]
                for each in paths_data["paths"][0]["instructions"]
            ]
            print(Fore.CYAN + tabulate(instructions_table, headers=[Fore.WHITE +"Instruction" + Fore.CYAN, Fore.WHITE + "Distance (km)" + Fore.CYAN, Fore.WHITE + "Distance (miles)" + Fore.CYAN], tablefmt="grid"))
        else:
            print(Fore.RED + f"Error: {paths_data.get('message', 'Unknown error')}")
            print("*************************************************")
