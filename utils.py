from datetime import datetime,timedelta

from PIL import Image,ImageFont,ImageDraw
from modal import IMG_TRACK,IMG_ARTIST,IMG_ALBUM,LASTM_IMG_DAILY_CHART,LASTM_IMG_HOURLY_CHART,IMG_TEMP,IMG_FINAL
from modal import Data,Tele
from providers.lastfm import getRecentTracksTimestamp,getTopAlbums,getTopArtists,getTopTracks,findTopRatings,weekCalculator,getTimestamps
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
        
    combineImage = combineImage.resize([1440, 288]) #[int(combineImage.width*0.4),int(combineImage.height*0.4)]
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


def makeWeeklyCollage(start):
    BG = Image.open(IMG_TEMP)
    x = 25
    
    dayCounter, weekCounter = weekCalculator(start)
    
    draw = ImageDraw.Draw(BG)
    font = ImageFont.truetype("arial.ttf", 80)
    draw.text((x, 15), weekCounter,font=font,stroke_width=18,stroke_fill='#000')
    font = ImageFont.truetype("arial.ttf", 60)
    draw.text((x+1000, 30), dayCounter,font=font,stroke_width=18,stroke_fill='#000')

    
    
    ALBUM = Image.open(IMG_ALBUM) #.resize([1440, 288]) #[int(ALBUM.width*0.4),int(ALBUM.height*0.4)]
    ARTIST = Image.open(IMG_ARTIST) #.resize([1440, 288])
    TRACK = Image.open(IMG_TRACK) #.resize([1440, 288])
    
    y = 215
    offset = 385
    BG.paste(ARTIST, (x,y)) 
    BG.paste(ALBUM, (x,y+offset))
    BG.paste(TRACK, (x,y+(offset*2)))
    
    DAILYCHART = Image.open(LASTM_IMG_DAILY_CHART).resize([1425, 550])
    HOURLYCHART = Image.open(LASTM_IMG_HOURLY_CHART).resize([1425, 550])

    y = 1300
    offset = 540
    BG.paste(DAILYCHART, (x,y))
    BG.paste(HOURLYCHART, (x,y+offset))
  
    # # Displaying the image 
    BG.save(IMG_FINAL, optimize=True)
    print("IMG: Weekly Collage saved")
    # BG.show()

def buildWeekly():
    start,end = getTimestamps()
    
    saveTopItems(start,end)
    saveWeeklyCharts(start,end)
    
    makeWeeklyCollage(start)
    
    dayCounter, weekCounter = weekCalculator(start)
    msg = weekCounter+"\n"+dayCounter
    return msg,IMG_FINAL

#----------------------------------