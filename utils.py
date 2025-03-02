from datetime import datetime,timedelta

from PIL import Image,ImageFont,ImageDraw
from modal import IMG_TRACK,IMG_ARTIST,IMG_ALBUM,LASTM_IMG_DAILY_CHART,LASTM_IMG_HOURLY_CHART,IMG_TEMP,IMG_FINAL,LASTM_IMG_DAY_CHART,LASTM_IMG_WEEKLY_CHART,FONT_ROBOTO_SEMI_BOLD
from modal import Data,Tele
from providers.lastfm import getRecentTracksTimestamp,getTopAlbums,getTopArtists,getTopTracks,findTopRatings
from common import buildChart,getMonthlyTimestamps,getWeeklyTimestamps,weekLabel,monthLabel


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

def saveMothlyCharts(start,end):       
    tracks = getRecentTracksTimestamp(start,end)
    weekly = {}
    days = {}
    days = {"Mon":0,"Tue":0,"Wed":0,"Thu":0,"Fri":0,"Sat":0,"Sun":0}


    for ts in tracks:
        day = ts.strftime("%a")
        days[day] = days.get(day,0) + 1
        
        week = ts.strftime("%W")
        weekly[week] = weekly.get(week,0) + 1
        
    buildChart('Weekly listen pattern',weekly.keys(), weekly.values(),'Week','Count','#EEDE54',LASTM_IMG_WEEKLY_CHART)
    buildChart('Days pattern',days.keys(), days.values(),'Day','Count','#48A54C',LASTM_IMG_DAY_CHART)


def saveCollage(lHeader,rHeader,chart1,chart2):
    BG = Image.open(IMG_TEMP)
    x = 25
    
    
    draw = ImageDraw.Draw(BG)
    if(len(lHeader)):
        font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 80)
        draw.text((x, 15), lHeader,font=font,stroke_width=18,stroke_fill='#000')
    if(len(rHeader)):
        font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 60)
        draw.text((x+1000, 30), rHeader,font=font,stroke_width=18,stroke_fill='#000')

    
    
    ALBUM = Image.open(IMG_ALBUM) #.resize([1440, 288]) #[int(ALBUM.width*0.4),int(ALBUM.height*0.4)]
    ARTIST = Image.open(IMG_ARTIST) #.resize([1440, 288])
    TRACK = Image.open(IMG_TRACK) #.resize([1440, 288])
    
    y = 215
    offset = 385
    BG.paste(ARTIST, (x,y)) 
    BG.paste(ALBUM, (x,y+offset))
    BG.paste(TRACK, (x,y+(offset*2)))
    
    CHART1 = Image.open(chart1).resize([1465, 550])
    CHART2 = Image.open(chart2).resize([1465, 550])

    y = 1300
    offset = 540
    BG.paste(CHART1, (x-30,y))
    BG.paste(CHART2, (x-30,y+offset))
  
    # # Displaying the image 
    BG.save(IMG_FINAL, optimize=True)
    print("IMG: Collage saved")
    # BG.show()


def buildWeekly():
    start,end = getWeeklyTimestamps()
    dayCounter, weekCounter = weekLabel(start)
    msg = f"#Music {weekCounter}\n{dayCounter}"
    print("LOG: Building for "+dayCounter)
    
    saveTopItems(start,end)
    saveWeeklyCharts(start,end)
    
    saveCollage(weekCounter,dayCounter,LASTM_IMG_DAILY_CHART,LASTM_IMG_HOURLY_CHART)
    
    return msg,IMG_FINAL

def buildMonthly():
    start,end = getMonthlyTimestamps()
    mName,mDays = monthLabel(start,end)
    
    print("LOG: Building for "+mName)
    
    saveTopItems(start,end)
    saveMothlyCharts(start,end)
    
    saveCollage(mName,mDays,LASTM_IMG_DAY_CHART,LASTM_IMG_WEEKLY_CHART)
    
    msg = f"#Music {mName}"
    return msg,IMG_FINAL


#----------------------------------