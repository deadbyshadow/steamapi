import requests

response = requests.get("https://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v0001/")
print(response.status_code)