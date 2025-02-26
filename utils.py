from datetime import datetime,timedelta

from PIL import Image,ImageDraw,ImageFont
from modal import IMG_TRACK,IMG_ARTIST,IMG_ALBUM,Data,LASTM_IMG_DAILY_CHART,LASTM_IMG_HOURLY_CHART
from providers.lastfm import getRecentTracksTimestamp,getTopAlbums,getTopArtists,getTopTracks,findTopRatings
from common import buildChart

#----------------------------------
# LASTFM
def combineImages(items):
    lenItems = len(items)
    h,w = 720,lenItems*720
    combineImage = Image.new('RGB',(w,h))

    for i in range(lenItems):
        item:Data = items[i]
        img:Image = item.generateImage()
        combineImage.paste(img,(i*h,0))
    return combineImage


def saveTopItems(start,end):
    topTracks,topArtists,topAlbums = findTopRatings(start,end)
    
    combineImages(getTopArtists(topArtists)).save(IMG_ARTIST)
    print("IMG: Artists saved")
    
    combineImages(getTopAlbums(topAlbums)).save(IMG_ALBUM)
    print("IMG: Albums saved")
    
    combineImages(getTopTracks(topTracks)).save(IMG_TRACK)
    print("IMG: Tracks saved")
        
def saveWeeklyCharts(start,end):       
    tracks = getRecentTracksTimestamp(start,end)        
    hrly = {}
    freq = {}
    startFreqDate = datetime.fromtimestamp(start)

    for i in range(7):
        date = (startFreqDate + timedelta(days=i)).strftime("%d-%m")
        freq[date] = 0


    for ts in tracks:
        hr = ts.strftime("%I%p")
        hrly[hr] = hrly.get(hr,0) + 1
        
        date = ts.strftime("%d-%m")
        freq[date] = freq.get(date,0) + 1
    
    buildChart('Daily listen pattern',freq.keys(), freq.values(),'Date','Count','#005582',LASTM_IMG_DAILY_CHART)
    buildChart('Hourly listen pattern',hrly.keys(), hrly.values(),'Hour','Count','#00c2c7',LASTM_IMG_HOURLY_CHART)
    

#----------------------------------