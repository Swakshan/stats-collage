from providers.trakt import getTrackData
from modal import MEDIA
from modal import TRAKT_WEEKLY_CHART,TRAKT_DAY_CHART,FONT_ROBOTO_SEMI_BOLD,IMG_FINAL
from common import buildChart,monthLabel,getEnv,getTraktMonthlyTimestamps,getMonthlyTimestamps
from PIL import Image,ImageDraw,ImageFont

def makeChart(tracks,type):
    # Fetch data from Trakt API
    weekly = {}
    days = {}
    days = {"Mon":0,"Tue":0,"Wed":0,"Thu":0,"Fri":0,"Sat":0,"Sun":0}


    for item in tracks:
        ts = item.watched_at
        day = ts.strftime("%a")
        days[day] = days.get(day,0) + 1
        
        week = ts.strftime("%W")
        weekly[week] = weekly.get(week,0) + 1
        
    buildChart(f'Weekly {type.value} watch pattern',weekly.keys(), weekly.values(),'Week','Count','#df2935',TRAKT_WEEKLY_CHART.format(type=type.value))
    buildChart(f'Days {type.value} pattern',days.keys(), days.values(),'Day','Count','#3772ff',TRAKT_DAY_CHART.format(type=type.value))


def buildMoviesNseriesCharts(start,end):
    movieList, showList = getTrackData(start,end,200)
    makeChart(movieList,MEDIA.MOVIE)
    makeChart(showList,MEDIA.SERIES)
    return len(movieList),len(showList)
    

def buildCollage(mName,mDays,movieCount,seriesCount):
    w=1080
    h=1920
    movie = MEDIA.MOVIE.value
    series = MEDIA.SERIES.value
    
    BG = Image.new('RGB', (w,h),'black')
    draw = ImageDraw.Draw(BG)
    x = 65
    
    font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 70)
    draw.text((x, 50), mName,font=font,stroke_width=18,stroke_fill='#000')
    
    font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 50)
    draw.text((x+w-465, 60), mDays,font=font,stroke_width=18,stroke_fill='#000')
    
    font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 40)
    draw.text((x, 160), f"Movie count: {movieCount}",font=font,stroke_width=10,stroke_fill='#000')
    draw.text((x+w-450, 160), f"Series count: {seriesCount}",font=font,stroke_width=10,stroke_fill='#000')
    
    chart_h = 400
    chart_w = w-150
    MOVIE_WEEKLY_CHART = Image.open(TRAKT_WEEKLY_CHART.format(type=movie)).resize((chart_w,chart_h))
    MOVIE_DAY_CHART = Image.open(TRAKT_DAY_CHART.format(type=movie)).resize((chart_w,chart_h))
    SEREIS_WEEKLY_CHART = Image.open(TRAKT_WEEKLY_CHART.format(type=series)).resize((chart_w,chart_h))
    SEREIS_DAY_CHART = Image.open(TRAKT_DAY_CHART.format(type=series)).resize((chart_w,chart_h))
    y = 250
    # x = x+40
    BG.paste(MOVIE_WEEKLY_CHART, (x,y))
    BG.paste(MOVIE_DAY_CHART, (x,y+chart_h))
    BG.paste(SEREIS_WEEKLY_CHART, (x,y+(chart_h*2)))
    BG.paste(SEREIS_DAY_CHART, (x,y+(chart_h*3)))
    
    BG.save(IMG_FINAL, optimize=True)
    print("IMG: Collage saved")
    
    # BG.show()
    

def buildMonthly():
    s,e = getMonthlyTimestamps()
    mName,mDays = monthLabel(s,e)
    print("LOG: Building for "+mName)
    
    s,e = getTraktMonthlyTimestamps()
    movieCount,seriesCount = buildMoviesNseriesCharts(s,e)
    buildCollage(mName,mDays,movieCount,seriesCount)
    msg = f"#Trakt {mName}"   
    return msg,IMG_FINAL
