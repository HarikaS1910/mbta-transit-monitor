import requests

url = "https://api-v3.mbta.com/vehicles"
params = {"filter[route]": "Red"}   # Red Line only

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()

for vehicle in response.json()["data"]:
    info = vehicle["attributes"]
    print(vehicle["id"], info["current_status"], info["updated_at"])
