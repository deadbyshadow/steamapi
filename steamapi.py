import requests
import json

#http://api.steampowered.com/<interface name>/<method name>/v<version>/?key=<api key>&format=<format>

#List of API methods
apilist = requests.get("https://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v0001/")
if apilist.status_code == 200:
    apilist = apilist.json()
else:
    print(f'Error: {apilist.status_code}')
    apilist = None
        
with open('list.json', 'w', encoding='utf-8') as f:
    json.dump(apilist, f, ensure_ascii=False, indent=4)


#API key
key = "0D42AB8DF7C4200A9F811E08E4D5FF41"

response = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + key + "&steamids=76561198315232228")
url = response.url

if response.status_code == 200:
    data = response.json()
    #print(data)
else:
    #error handling
    print(f'Error: {response.status_code}')
    data = None
    
    
    
#File operations
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)