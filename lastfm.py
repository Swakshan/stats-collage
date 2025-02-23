from common import getEnv,readJsonFile,writeJsonFile
from modal import Data,Item
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

def getYT(name,type):
    YTM = YTMusic()
    return YTM.search(query=name,filter=type)

def getYTImage(name,type):
    search = getYT(name,type)
    if len(search) == 0: return "https://www.gstatic.com/youtube/media/ytm/images/artist_avatar@1200.png"
    return search[0]['thumbnails'][1]['url'].replace("w120-h120","w720-h720")

def getYTImageNArtist(name,type):
    search = getYT(name,type)
    img = "https://www.gstatic.com/youtube/media/ytm/images/artist_avatar@1200.png"
    artist = "unknown"
    if len(search) != 0: 
        item = search[0]
        img =  item['thumbnails'][1]['url'].replace("w120-h120","w720-h720")
        artist = item['artists'][0]['name']
    return img, artist



def requestAPI(slug,start,end,limit=200):
    API = 'https://ws.audioscrobbler.com/2.0/?api_key='+getEnv('LASTFM_API_KEY')+'&format=json&extended=1&method='+slug+'&user='+getEnv('LASTFM_USERNAME')+'&limit='+str(limit)+'&from='+str(start)+'&to='+str(end)
    response = requests.get(API)
    stsCode = response.status_code
    if stsCode !=requests.codes.ok: raise Exception("Error: Lastfm API request failed. Status code: "+stsCode)
    print("API: fetched "+slug)
    return response.json()

def getTopTracks(start,end,limit=5):
    slug = 'user.getweeklytrackchart'
    res = requestAPI(slug,start,end,limit)
    # res = readJsonFile("./dummy/getweeklytrackchart.json")
    
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
    # res = readJsonFile("./dummy/getweeklyartistchart.json")
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
    # res = readJsonFile("./dummy/getweeklyalbumchart.json")
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
        # res = readJsonFile(f"./dummy/getrecenttracks_{page}.json")
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

def findTopRatings(start,end,limit=200):
    tracks = getRecentTracks(start,end,limit)
    songs  = {}
    artists = {}
    albums = {}
    for track in tracks:
        if "@attr" in track: continue

        songName = track['name']
        artistName = track['artist']['name']
        albumName = track['album']['#text']
        albumName = songName if albumName == "" else albumName
        isLoved = True if int(track['loved']) else False
        
        songKey  = f"{songName}||{artistName}||{albumName}"
        
        songData:Item = songs[songKey] if songKey in songs else Item(name=songKey,scrobble=0,loved=isLoved)
        songData.scrobble += 1
        songData.loved = isLoved if isLoved else songData.loved
        songs[songKey] = songData
        
        artistData:Item = artists[artistName] if artistName in artists else Item(name=artistName,scrobble=0,loved=isLoved)
        artistData.scrobble += 1
        artistData.loved = isLoved if isLoved else artistData.loved
        artists[artistName] = artistData

        albumData:Item = albums[albumName] if albumName in albums else Item(name=albumName+"||"+artistName,scrobble=0,loved=isLoved)
        albumData.scrobble += 1
        albumData.loved = isLoved if isLoved else albumData.loved
        albums[albumName] = albumData
    
    topSongs = sorted(list(songs.values()), key=lambda x: x.scrobble,reverse=True)[:5]
    topArtists = sorted(list(artists.values()), key=lambda x: x.scrobble,reverse=True)[:5]
    topAlbums = sorted(list(albums.values()), key=lambda x: x.scrobble,reverse=True)[:5]
    
    return topSongs,topArtists,topAlbums

def getTopTracks(tracks):
    whole = []
    for item in tracks:
        splits = item.name.split("||")
        title = splits[0]
        artist = splits[1]

        scrobble = item.scrobble
        loved = item.loved    

        imageUrl = getYTImage(f"{title} - {artist}","songs")
        
        data:Data = Data(title,artist,imageUrl,scrobble,loved)
        whole.append(data)
    return whole

def getTopArtists(artists):
    whole = []
    for item in artists:
        artist = item.name
        scrobble = item.scrobble
        title = ""
        loved = item.loved    

        imageUrl = getYTImage(artist,"artists")
        
        data:Data = Data(title,artist,imageUrl,scrobble,loved)
        whole.append(data)
    return whole

def getTopAlbums(albums):
    whole = []
    for item in albums:
        splits = item.name.split("||")
        title = splits[0]
        artist = splits[1]
        scrobble = item.scrobble
        loved = item.loved    

        imageUrl,artist = getYTImageNArtist(f"{title} - {artist}","albums")
        
        data:Data = Data(title,artist,imageUrl,scrobble,loved)
        whole.append(data)
    return whole
