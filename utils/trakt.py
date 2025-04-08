from providers.trakt import getTrackData
from modal import MEDIA
from modal import TRAKT_WEEKLY_CHART,TRAKT_DAY_CHART,FONT_ROBOTO_SEMI_BOLD,IMG_FINAL,OUT_IMG_W,OUT_IMG_H
from common import buildChart,monthLabel,getEnv,getTraktMonthlyTimestamps,getMonthlyTimestamps
from PIL import Image,ImageDraw,ImageFont

def makeChart(tracks,type):
    weekly = {}
    days = {}
    days = {"Mon":0,"Tue":0,"Wed":0,"Thu":0,"Fri":0,"Sat":0,"Sun":0}


    for item in tracks:
        ts = item.watched_at
        day = ts.strftime("%a")
        days[day] = days.get(day,0) + 1
        
        week = int(ts.strftime("%W")) + 1
        weekly[week] = weekly.get(week,0) + 1
        
    buildChart(f'Weekly {type.value} watch pattern',weekly.keys(), weekly.values(),'Week','Count','#df2935',TRAKT_WEEKLY_CHART.format(type=type.value))
    buildChart(f'Days {type.value} pattern',days.keys(), days.values(),'Day','Count','#3772ff',TRAKT_DAY_CHART.format(type=type.value))


def buildMoviesNseriesCharts(start,end):
    movieList, showList,episodeList = getTrackData(start,end,200)
    makeChart(movieList,MEDIA.MOVIE)
    makeChart(episodeList,MEDIA.EPISODE)
    return len(movieList),len(showList),len(episodeList)
    

def buildCollage(mName,mDays,movieCount,showCount,episodeCount):
    w=OUT_IMG_W
    h=OUT_IMG_H
    movie = MEDIA.MOVIE.value
    episode = MEDIA.EPISODE.value
    
    BG = Image.new('RGB', (w,h),'black')
    draw = ImageDraw.Draw(BG)
    x = 65
    
    font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 70)
    draw.text((x, 50), mName,font=font,stroke_width=18,stroke_fill='#000')
    
    font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 50)
    draw.text((x+w-465, 60), mDays,font=font,stroke_width=18,stroke_fill='#000')
    
    font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 40)
    draw.text((x, 160), f"Movies count: {movieCount}",font=font,stroke_width=10,stroke_fill='#000')
    draw.text((x+w-450, 140), f"Shows count: {showCount}",font=font,stroke_width=10,stroke_fill='#000')
    draw.text((x+w-450, 180), f"Episodes count: {episodeCount}",font=font,stroke_width=10,stroke_fill='#000')
    
    chart_h = 400
    chart_w = w-150
    MOVIE_WEEKLY_CHART = Image.open(TRAKT_WEEKLY_CHART.format(type=movie)).resize((chart_w,chart_h))
    MOVIE_DAY_CHART = Image.open(TRAKT_DAY_CHART.format(type=movie)).resize((chart_w,chart_h))
    EPISODE_WEEKLY_CHART = Image.open(TRAKT_WEEKLY_CHART.format(type=episode)).resize((chart_w,chart_h))
    EPISODE_DAY_CHART = Image.open(TRAKT_DAY_CHART.format(type=episode)).resize((chart_w,chart_h))
    y = 250
    # x = x+40
    BG.paste(MOVIE_WEEKLY_CHART, (x,y))
    BG.paste(MOVIE_DAY_CHART, (x,y+chart_h))
    BG.paste(EPISODE_WEEKLY_CHART, (x,y+(chart_h*2)))
    BG.paste(EPISODE_DAY_CHART, (x,y+(chart_h*3)))
    
    BG.save(IMG_FINAL, optimize=True)
    print("IMG: Collage saved")
    
    # BG.show()
    

def buildMonthly():
    s,e = getMonthlyTimestamps()
    mName,mDays = monthLabel(s,e)
    print("LOG: Building for "+mName)
    
    s,e = getTraktMonthlyTimestamps()
    movieCount,showCount,episodeCount = buildMoviesNseriesCharts(s,e)

    buildCollage(mName,mDays,movieCount,showCount,episodeCount)
    msg = f"#Trakt {mName}"   
    return msg,IMG_FINAL
