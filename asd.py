import requests
import json
import mysql.connector
import time
import sys
import sched

def GetApplist():
    try:
        apprequest = requests.get(f'https://api.steampowered.com/ISteamApps/GetAppList/v2/')
    except:
        print('Failed to get response from steam')

    appjson = apprequest.json()
    appid = []
    name = []
    for i in range (len(appjson['applist']['apps'])):
        appid.append(appjson['applist']['apps'][i]['appid'])
        name.append(appjson['applist']['apps'][i]['name'])
        
    applist = {
        'appid': appid,
        'name' : name
    }
    
    for i in range(len(applist['appid'])):
        try:
            dbcursor.execute(f'SELECT appid FROM applist WHERE appid = {applist["appid"][i]}')
        except:
            print('sql error in applist')
        try: 
            x = dbcursor.fetchone()[0]
        except:
            dbcursor.execute(f'INSERT INTO applist (appid, name) VALUES {applist["appid"][i], applist["name"][i]}')
    db.commit()
    scheduler.enter(3600, 1, GetApplist)


if __name__ == '__main__':
    #Making a connection to the database
    db = mysql.connector.connect(
        host = '127.0.0.1',
        user = 'root',
        password = 'root',
        database = 'steam'
    )
    dbcursor = db.cursor(buffered = True)
    
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0, 1, GetApplist)
    #API key
    key = open('key.txt')
    key = key.read()

    #SteamIDs and all lists in connection with them
    steamid = 76561198315232228
    
    try:
        req = requests.get(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamid}&format=json')
    except:
        print('gg')
    gamesjson = req.json()['response']
    
    game_count = gamesjson['game_count']
    games = gamesjson['games']
    print(game_count ,'\n')
    for i in range(len(games)):
        print(games[i])
    #gamesjson = gamerequest.json()
    #gamecount = int(gamesjson["response"]["game_count"])
    #games = gamesjson["response"]["games"]
    
    #print(games)
    
    
    scheduler.run()