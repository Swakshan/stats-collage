from common import getEnv,readJsonFile,writeJsonFile
from modal import MusicData,MusicItem,CACHE_FOLDER
import requests,os
from ytmusicapi import YTMusic
from datetime import datetime,timedelta
from pytz import timezone

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

def getYTSongDuration(title):
    search = getYT(title,"songs")
    if len(search) == 0: return 0
    return search[0]['duration_seconds']

def requestAPI(slug,start,end,limit=200):
    API = 'https://ws.audioscrobbler.com/2.0/?api_key='+getEnv('LASTFM_API_KEY')+'&format=json&extended=1&method='+slug+'&user='+getEnv('LASTFM_USERNAME')+'&limit='+str(limit)+'&from='+str(start)+'&to='+str(end)
    response = requests.get(API)
    stsCode = response.status_code
    if stsCode !=requests.codes.ok: raise Exception(f"Error: Lastfm API request failed. Status code: {stsCode}")
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
        
        data = MusicData(title,artist,imageUrl,scrobble)
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
        
        data = MusicData(title,artist,imageUrl,scrobble)
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
        
        data = MusicData(title,artist,imageUrl,scrobble)
        tracks.append(data)
    return tracks

def getRecentTracks(start,end,limit=200):
    cache_file = CACHE_FOLDER+"/getrecenttracks.json"
    if os.path.exists(cache_file):
        return readJsonFile(cache_file)
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
    writeJsonFile(tracks,cache_file)
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
    
    return reversed(dt)


def getDurationSpent(start,end,limit=200):
    global cache
    cache = {}
    totalDuration = 0
    def getDuration(track):
        songName = track['name']
        artistName = track['artist']['name']
        albumName = track['album']['#text']
        title = f"{songName} - {artistName} - {albumName}"
        dur = cache.get(title,0)
        if not dur:
            dur = getYTSongDuration(title)
            cache[title] = dur
        return dur
        
    tracks = getRecentTracks(start,end,limit)
    TZ = timezone('Asia/Kolkata')
    for i in range(1,len(tracks)):
        prevTrack = tracks[i-1]
        if 'date' not in prevTrack:
            continue
        
        curTrack = tracks[i]
        prev_ts = prevTrack['date']['uts']
        cur_ts = curTrack['date']['uts']
        dur = int(prev_ts) - int(cur_ts)
        if dur > 300: #5 minutes
            dur = getDuration(prevTrack)
        totalDuration+= dur
    totalDuration+= getDuration(tracks[-1])
    return totalDuration

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
        
        songData:MusicItem = songs[songKey] if songKey in songs else MusicItem(name=songKey,scrobble=0,loved=isLoved)
        songData.scrobble += 1
        songData.loved = isLoved if isLoved else songData.loved
        songs[songKey] = songData
        
        artistData:MusicItem = artists[artistName] if artistName in artists else MusicItem(name=artistName,scrobble=0)
        artistData.scrobble += 1
        artists[artistName] = artistData

        albumData:MusicItem = albums[albumName] if albumName in albums else MusicItem(name=albumName+"||"+artistName,scrobble=0)
        albumData.scrobble += 1
        albums[albumName] = albumData
    
    topSongs = sorted(list(songs.values()), key=lambda x: x.scrobble,reverse=True)[:5]
    topArtists = sorted(list(artists.values()), key=lambda x: x.scrobble,reverse=True)[:5]
    topAlbums = sorted(list(albums.values()), key=lambda x: x.scrobble,reverse=True)[:5]
    
    tops = [topArtists,topAlbums,topSongs]
    counts = [f"({len(artists)})",f"({len(albums)})",f"({len(songs)})"]
    
    return tops,counts

def getTopTracks(tracks):
    whole = []
    for item in tracks:
        splits = item.name.split("||")
        title = splits[0]
        artist = splits[1]

        scrobble = item.scrobble
        loved = item.loved    

        imageUrl = getYTImage(f"{title} - {artist}","songs")
        
        data:MusicData = MusicData(title,artist,imageUrl,scrobble,loved)
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
        
        data:MusicData = MusicData(title,artist,imageUrl,scrobble,loved)
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
        
        data:MusicData = MusicData(title,artist,imageUrl,scrobble,loved)
        whole.append(data)
    return whole
