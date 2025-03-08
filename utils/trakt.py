from providers.trakt import getTrackData
from modal import MovieData,SeriesData,MEDIA
from modal import TRAKT_WEEKLY_CHART,TRAKT_DAY_CHART
from common import buildChart

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
    
    
