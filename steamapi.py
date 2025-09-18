import requests
import json
import mysql.connector
#import multiprocessing

#http://api.steampowered.com/<interface name>/<method name>/v<version>/?key=<api key>&format=<format>

#def proc1():
#  print(idlist[v1], 'proc1')
#  iddone.append(idlist[v1])
#  idlist.pop(v1)
#  
#  
#def proc2():
#  print(idlist[v2], 'proc2')
#  iddone.append(idlist[v2])
#  idlist.pop(v2)


if __name__ == '__main__':
    #Making a connection to the database
    db = mysql.connector.connect(
        host = '127.0.0.1',
        user = 'root',
        password = 'root',
        database = 'steam'
    )
    dbcursor = db.cursor()

    #API key
    key = open('key.txt')
    key = key.read()

    #SteamID to be used
    steamid = 76561198315232228
    idlist = []
    idlist.append(steamid)
    iddone = []
    idcount = 0
    maxcalls = 1000
    calls = 0
    #friendlist = requests.get(f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={key}&steamid={steamid}&relationship=friend')
    #if friendlist.status_code != 200:
    #    print(f'Error: {friendlist.status_code}. Failed to get info from {friendlist.url}')
    #else:
    #    friendData = friendlist.json()
    #    friendData = friendData['friendslist']['friends']
    #    for i in range(len(friendData)):
    #        if int(friendData[i]['steamid']) not in idlist:
    #            idlist.append(int(friendData[i]["steamid"]))
    #
    #    with open('friendlist.json', 'w', encoding='utf-8') as f:
    #        json.dump(friendlist.json(), f, ensure_ascii=False, indent=4)
    #
    #p1 = threading.Thread(target=proc1, daemon=True)
    #p2 = threading.Thread(target=proc2, daemon=True)

    playerNum = 0
    while calls + (playerNum // 100) <= maxcalls:
        friendlist = requests.get(f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={key}&steamid={idlist[calls]}&relationship=friend')
        calls = calls + 1
        if friendlist.status_code == 401:
            print(f'{friendlist.status_code} Friendlist private skipping...')
        elif friendlist.status_code != 200:
            print(f'Error: {friendlist.status_code}. Failed to get info from {friendlist.url}')
        else:
            friendData = friendlist.json()
            friendData = friendData['friendslist']['friends']
            for i in range(len(friendData)):
                if int(friendData[i]['steamid']) not in idlist or iddone:
                    idlist.append(int(friendData[i]["steamid"]))
                    playerNum = playerNum + 1
        


    while len(idlist) > 0:
        playerSummary = requests.get(f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={key}&steamids={idlist[0:99]}')
        calls + 1
        #Checking in case the request failed
        if playerSummary.status_code != 200:
            print(f'Error: {playerSummary.status_code} Failed to get info from {playerSummary.url}')
        else:
            i = 0
            while i <= 99:
                dbinput = [None] * 11
                playerData = playerSummary.json()
                #This is the userdata that will be used in the SQL query
                dbinput =  (int(playerData["response"]["players"][i]["steamid"]), playerData["response"]["players"][i]["personaname"], playerData["response"]["players"][i]["profileurl"], playerData["response"]["players"][i]["avatar"], playerData["response"]["players"][i]["avatarmedium"], playerData["response"]["players"][i]["avatarfull"])

                try:
                    #In case there is a value we input it into the local variable and merge it with dbinput
                    personastate = int(playerData["response"]["players"][i]["personastate"])
                    temp = list(dbinput)
                    temp.append(personastate)
                    dbinput = tuple(temp)
                except:
                    #In case we get an error we assume that the it is false and merge it with dbinput
                    personastate = 0
                    temp = list(dbinput)
                    temp.append(personastate)
                    dbinput = tuple(temp)
                try:
                    #In case there is a value we input it into the local variable and merge it with dbinput
                    comvis = bool(playerData["response"]["players"][i]["communityvisibilitystate"])
                    temp = list(dbinput)
                    temp.append(comvis)
                    dbinput = tuple(temp)
                except:
                    #In case we get an error we assume that the it is false and merge it with dbinput
                    comvis = False
                    temp = list(dbinput)
                    temp.append(comvis)
                    dbinput = tuple(temp)
                try:
                    #In case there is a value we input it into the local variable and merge it with dbinput
                    profilestate = bool(playerData["response"]["players"][i]["profilestate"])
                    temp = list(dbinput)
                    temp.append(profilestate)
                    dbinput = tuple(temp)
                except:
                    #In case we get an error we assume that the it is false and merge it with dbinput
                    profilestate = False
                    temp = list(dbinput)
                    temp.append(profilestate)
                    dbinput = tuple(temp)
                try:
                    #In case there is a value we input it into the local variable and merge it with dbinput
                    lastlogoff = int(playerData["response"]["players"][i]["lastlogoff"])
                    temp = list(dbinput)
                    temp.append(lastlogoff)
                    dbinput = tuple(temp)
                except:
                    #In case we get an error we assume that the it is false and merge it with dbinput
                    lastlogoff = 0
                    temp = list(dbinput)
                    temp.append(lastlogoff)
                    dbinput = tuple(temp)
                #There are cases where the JSON does not contain a "commentpermission" segment and as such we need to handle the cases where dbinput does not get any values
                try:
                    if bool(playerData["response"]["players"][i]["commentpermission"]):
                        #In case there is a value we input it into the local variable and merge it with dbinput
                        commentpermission = bool(playerData["response"]["players"][i]["commentpermission"])
                        temp = list(dbinput)
                        temp.append(commentpermission)
                        dbinput = tuple(temp)
                except:
                    #In case we get an error we assume that the it is false and merge it with dbinput
                    commentpermission = False
                    temp = list(dbinput)
                    temp.append(commentpermission)
                    dbinput = tuple(temp)

                #Checks if the steamID is in the database
                #       >if yes then update record
                #       >if no then create new record
                dbcursor.execute(f'SELECT * FROM publicusers WHERE steamid = {dbinput[0]}')
                if len(dbcursor.fetchall()) > 0:
                    #SQL query that updates the record in case it already exists
                    print(f'SteamID already in database ({dbinput[0]}). Updating record.')

                    #We use local variables to handle special characters in usernames (because the query is sensitive to commas)
                    update = "UPDATE publicusers SET personaname=%s, profileurl=%s, avatar=%s, avatarmedium=%s, avatarfull=%s, personastate=%s, communityvisibilitystate=%s, profilestate=%s, lastlogoff=%s, commentpermission=%s WHERE steamid=%s"
                    tempupd = (str(dbinput[1]), dbinput[2], dbinput[3], dbinput[4], dbinput[5], dbinput[6], dbinput[7], dbinput[8], dbinput[9], dbinput[10], dbinput[0])
                    dbcursor.execute(update, tempupd)
                else:
                    #SQL query that creates the new record in case it isn't in the database
                    print(f'New SteamID detected ({dbinput[0]}). Creating record.')
                    #There is no need to use temporary variables because in the case of the INSERT query the VALUES are already handled in case they contain special characters
                    dbcursor.execute(f'INSERT INTO publicusers (steamid, personaname, profileurl, avatar, avatarmedium, avatarfull, personastate, communityvisibilitystate, profilestate, lastlogoff, commentpermission) VALUES {dbinput}')
                iddone.append(idlist[0])
                idlist.pop(0)
                playerData["response"]["players"].pop(0)
                i = i + 1
                j = 0
            while j <= 99:
                idlist.pop(0)
                j = j + 1
db.commit()
            
            
            
            
            
            
            
            
            
            
            
            

        #Export the request as playerSummary.json
        #DEBUG ONLY
        #with open('playerSummary.json', 'w', encoding='utf-8') as f:
        #    json.dump(playerSummary.json(), f, ensure_ascii=False, indent=4)
        #if p1.is_alive() != True:
        #    v1 = idcount
        #    #time.sleep(0.5)
        #    p1.start()
        #    idcount = idcount + 1
        #    
        #elif p2.is_alive() != False:
        #    v2 = idcount
        #    time.sleep(0.5)
        #    p2.start()
        #    idcount = idcount + 1
        
        
    #p1.join()
    #p2.join()