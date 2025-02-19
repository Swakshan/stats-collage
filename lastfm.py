from common import getEnv,readJsonFile,writeJsonFile
from modal import Data
import requests
from ytmusicapi import YTMusic
from datetime import datetime,timedelta
from pytz import timezone


def getTimestamps():
    TZ = timezone('Asia/Kolkata')
    today = datetime.now(tz=TZ)
    sunTimedelta = today.isoweekday()
    endDate = today - timedelta(days=sunTimedelta)
    startDate = endDate - timedelta(days=6)
    
    startTS = startDate.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    endTS = endDate.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()
    return int(startTS), int(endTS)


def getYTImage(name,type):
    YTM = YTMusic()
    search = YTM.search(query=name,filter=type)
    if len(search) == 0: return "https://www.gstatic.com/youtube/media/ytm/images/artist_avatar@1200.png"
    return search[0]['thumbnails'][1]['url'].replace("w120-h120","w720-h720")


def requestAPI(slug,start,end,limit=200):
    API = 'https://ws.audioscrobbler.com/2.0/?api_key='+getEnv('LASTFM_API_KEY')+'&format=json&extended=1&method='+slug+'&user='+getEnv('LASTFM_USERNAME')+'&limit='+str(limit)+'&from='+str(start)+'&to='+str(end)
    response = requests.get(API)
    stsCode = response.status_code
    if stsCode !=requests.codes.ok: raise Exception("Error: Lastfm API request failed. Status code: "+stsCode)
    return response.json()

def getTopTracks(start,end,limit=5):
    slug = 'user.getweeklytrackchart'
    res = requestAPI(slug,start,end,limit)
    tracks = []
    for track in res['weeklytrackchart']['track']:
        artist = track['artist']['#text']
        title = track['name']
        scrobble = track['playcount']
        imageUrl = getYTImage(title,"songs")
        
        data = Data(title,artist,imageUrl,scrobble)
        tracks.append(data)
    return tracks


def getTopArtists(start,end,limit=5):
    slug = 'user.getweeklyartistchart'
    res = requestAPI(slug,start,end,limit)
    tracks = []
    for track in res['weeklyartistchart']['artist']:
        title = ""
        artist = track['name'].split("&")[0].split(",")[0]
        scrobble = track['playcount']
        imageUrl = getYTImage(artist,"artists")
        
        data = Data(title,artist,imageUrl,scrobble)
        tracks.append(data)
    return tracks

def getTopAlbums(start,end,limit=5):
    slug = 'user.getweeklyalbumchart'
    res = requestAPI(slug,start,end,limit)
    tracks = []
    for track in res['weeklyalbumchart']['album']:
        artist = track['artist']['#text']
        title = track['name']
        scrobble = track['playcount']
        imageUrl = getYTImage(f"{artist} - {title}","albums")
        
        data = Data(title,artist,imageUrl,scrobble)
        tracks.append(data)
    return tracks

def getRecentTracks(start,end,limit=200):
    totalPages = 999
    page = 1
    slug = 'user.getRecentTracks'
    tracks = []
    while page <= totalPages:
        res = requestAPI(f'{slug}&page={page}',start,end,limit)
        
        track = res['recenttracks']['track']
        tracks.extend(track)
        
        attr = res['recenttracks']['@attr']
        totalPages = int(attr['totalPages'])
        page = int(attr['page']) + 1
    return tracks

def getRecentTracksTimestamp(start,end,limit=200):
    tracks = getRecentTracks(start,end,limit)
    TZ = timezone('Asia/Kolkata')
    dt = []
    for track in tracks:
        if 'date' not in track:
            continue
        date_str = track['date']['uts']
        
        dt.append(datetime.fromtimestamp(int(date_str),tz=TZ))
    return dt

