from common import getEnv
from utils import Data
import requests
from ytmusicapi import YTMusic

def getYTImage(name,type):
    YTM = YTMusic()
    search = YTM.search(query=name,filter=type)
    if len(search) == 0: return "https://www.gstatic.com/youtube/media/ytm/images/artist_avatar@1200.png"
    return search[0]['thumbnails'][1]['url'].replace("w120-h120","w720-h720")


def requestAPI(slug):
    API = 'https://ws.audioscrobbler.com/2.0/?api_key='+getEnv('LASTFM_API_KEY')+'&format=json&extended=1&method='+slug
    response = requests.get(API)
    stsCode = response.status_code
    if stsCode !=requests.codes.ok: raise Exception("Error: Lastfm API request failed. Status code: "+stsCode)
    return response.json()

def getTrackChart(username,start,end,limit=5):
    slug = 'user.getweeklytrackchart&user='+username+'&limit='+str(limit)+'&from='+str(start)+'&to='+str(end)
    res = requestAPI(slug)
    tracks = []
    for track in res['weeklytrackchart']['track']:
        artist = track['artist']['#text']
        title = track['name']
        scrobble = track['playcount']
        # artist.split("&")[0].split(",")[0]
        imageUrl = getYTImage(title,"songs")
        
        data = Data(title,artist,imageUrl,scrobble)
        data.generateImage()
        
        tracks.append(data)
    return tracks


def getArtistChart(username,start,end,limit=5):
    slug = 'user.getweeklyartistchart&user='+username+'&limit='+str(limit)+'&from='+str(start)+'&to='+str(end)
    res = requestAPI(slug)
    tracks = []
    for track in res['weeklyartistchart']['artist']:
        title = ""
        artist = track['name']
        scrobble = track['playcount']
        imageUrl = getYTImage(artist,"artists")
        
        data = Data(title,artist,imageUrl,scrobble)
        data.generateImage()
        
        tracks.append(data)
    return tracks

def getAlbumChart(username,start,end,limit=5):
    slug = 'user.getweeklyalbumchart&user='+username+'&limit='+str(limit)+'&from='+str(start)+'&to='+str(end)
    res = requestAPI(slug)
    tracks = []
    for track in res['weeklyalbumchart']['album']:
        artist = track['artist']['#text']
        title = track['name']
        scrobble = track['playcount']
        imageUrl = getYTImage(f"{artist} - {title}","albums")
        data = Data(title,artist,imageUrl,scrobble)
        data.generateImage()
        
        tracks.append(data)
    return tracks

    #     album = track['album']['name']
    #     timestamp = track['date']['uts']

