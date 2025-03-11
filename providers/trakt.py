from common import getEnv,readJsonFile,writeJsonFile
import requests,os
from modal import MEDIA,CACHE_FOLDER,MovieData,SeriesData
from datetime import datetime, timedelta


def formatWatchedAt(watchedAt):
    return datetime.fromisoformat(watchedAt) + timedelta(hours=5,minutes=30) # UTC to IST


def requestAPI(slug,start,end,limit):
    API = f"https://api.trakt.tv/users/{getEnv('TRAKT_USERNAME')}/{slug}?limit={limit}&start_at={start}&end_at={end}"
    HDR = {
        "Content-Type":"application/json",
        "trakt-api-version":"2",
        "trakt-api-key": getEnv('TRAKT_CLIENT_ID')
    }
    
    response = requests.get(API,headers=HDR)
    stsCode = response.status_code
    if stsCode !=requests.codes.ok: raise Exception("Error: Trakt API request failed. Status code: "+stsCode)
    print("API: fetched "+slug)
    rd = {}
    rd['data'] = response.json()
    rHeaders = response.headers
    if "x-pagination-page-count" in rHeaders:
        rd['page'] = rHeaders['x-pagination-page']
        rd['totalPages'] = rHeaders['x-pagination-page-count']
    return rd

def getTraktHistory(type:MEDIA,start:str,end:str,limit:int):
    typ = type.value
    cache_file = f"{CACHE_FOLDER}/trakt_{typ}_history.json"
    if os.path.exists(cache_file):
        return readJsonFile(cache_file)
    
    totalPages = 999
    page = 1
    slug = f"history/{typ}"

    items = []
    while page <= totalPages:
        res = requestAPI(slug,start,end,limit)
        items.extend(res['data'])
        totalPages = int(res['totalPages']) if "totalPages" in res else page
        page+=1
    writeJsonFile(items,cache_file)
    return items

def getTrackData(start:str,end:str,limit=25):
    movies = getTraktHistory(MEDIA.MOVIE,start,end,limit)
    movies = reversed(movies)
    movieList = []
    for movie in movies:
        watchedAt = formatWatchedAt(movie['watched_at'])
        movieData = movie['movie']
        title = movieData['title']
        imdb = movieData['ids']['imdb']
        year = movieData['year']
        
        md = MovieData(imdb,title,watchedAt,year)
        movieList.append(md)

    shows = getTraktHistory(MEDIA.SERIES,start,end,limit)
    shows = reversed(shows)
    showList = []
    for show in shows:
        showData = show['show']
        series_imdb = showData['ids']['imdb']
        series_name = showData['title']
        year = showData['year']

        episodeData = show['episode']
        season_number = episodeData['season']
        episode_imdb = episodeData['ids']['imdb']
        episode_name = episodeData['title']
        episode_number = episodeData['number']
        watched_at = formatWatchedAt(show['watched_at'])
        
        sd = SeriesData(series_imdb,series_name,season_number,episode_imdb,episode_name,episode_number,watched_at,year)
        showList.append(sd)
    return movieList,showList






