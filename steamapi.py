import requests
import json
import mysql.connector

#http://api.steampowered.com/<interface name>/<method name>/v<version>/?key=<api key>&format=<format>

#List of API methods
apilist = requests.get(f'https://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v0001/')


#Making a connection to the database
db = mysql.connector.connect(
    host = '127.0.0.1',
    user = 'root',
    password = 'root',
    database = 'steam'
)
dbcursor = db.cursor()

#Checks if the request is valid and writes to apilist.json
if apilist.status_code != 200:
    print(f'Error: {apilist.status_code}. Failed to get info from {apilist.url}')
else:
    with open('list.json', 'w', encoding='utf-8') as f:
        json.dump(apilist.json(), f, ensure_ascii=False, indent=4)

#API key
key = open('key.txt')
key = key.read()

#SteamID to be used
steamid = 76561198315232228

playerSummary = requests.get(f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={key}&steamids={steamid}')

#Checking in case the request failed
if playerSummary.status_code != 200:
    print(f'Error: {playerSummary.status_code} Failed to get info from {playerSummary.url}')
else:
    playerData = playerSummary.json()
    #This is the userdata that will be used in the SQL query
    dbinput = (int(playerData["response"]["players"][0]["steamid"]), int(playerData["response"]["players"][0]["communityvisibilitystate"]), int(playerData["response"]["players"][0]["profilestate"]), str(playerData["response"]["players"][0]["personaname"]), int(playerData["response"]["players"][0]["commentpermission"]), str(playerData["response"]["players"][0]["profileurl"]), str(playerData["response"]["players"][0]["avatar"]), str(playerData["response"]["players"][0]["avatarmedium"]), str(playerData["response"]["players"][0]["avatarfull"]), int(playerData["response"]["players"][0]["lastlogoff"]), int(playerData["response"]["players"][0]["personastate"]))

    #Checks if the steamID is in the database
    #       >if yes then update record
    #       >if no then create new record
    dbcursor.execute(f'SELECT * FROM publicuser WHERE steamid = {dbinput[0]}')
    if len(dbcursor.fetchall()) > 0:
        print(f'SteamID already in database ({dbinput[0]}). Updating record.')
        #SQL query that updates the record
        dbcursor.execute(f"UPDATE publicuser SET communityvisibilitystate={dbinput[1]}, profilestate={dbinput[2]}, personaname='{dbinput[3]}', commentpermission={dbinput[4]}, profileurl='{dbinput[5]}', avatar='{dbinput[6]}', avatarmedium='{dbinput[7]}', avatarfull='{dbinput[8]}', lastlogoff={dbinput[9]}, personastate={dbinput[10]} WHERE steamid={dbinput[0]}")
    else:
        print(f'New SteamID detected ({dbinput[0]}). Creating record.')
        #SQL query that creates the new record
        dbcursor.execute(f'INSERT INTO publicuser (steamid, communityvisibilitystate, profilestate, personaname, commentpermission, profileurl, avatar, avatarmedium, avatarfull, lastlogoff, personastate) VALUES {dbinput}')
    db.commit()
    
    #Export the request as playerSummary.json
    #DEBUG ONLY
    with open('playerSummary.json', 'w', encoding='utf-8') as f:
        json.dump(playerSummary.json(), f, ensure_ascii=False, indent=4)
        

#clientver = requests.get('http://api.steampowered.com/IGCVersion_1046930/GetClientVersion/v0001/')
#
#if clientver.status_code != 200:
#    print(f'Error: {clientver.status_code}. Failed to get info from {clientver.url}')
#else:
#    with open('clientver.json', 'w', encoding='utf-8') as f:
#        json.dump(clientver.json(), f, ensure_ascii=False, indent=4)
#        clientData = clientver.json()
#        clientDict = clientData["result"]
#        clientArray = [clientDict["success"], clientDict["min_allowed_version"], clientDict["active_version"]]
        
        
