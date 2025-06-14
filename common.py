import os
from dotenv import load_dotenv
import json
import matplotlib.pyplot as plt
from datetime import datetime,timedelta,timezone as tz
from pytz import timezone
from sys import exc_info
from traceback import format_exception
from humanfriendly import format_timespan

load_dotenv()

def getEnv(key):
    return os.getenv(key)

def printJson(data):
    print(json.dumps(data,indent=4))

def writeJsonFile(data,filename):
    with open(filename, 'w',encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))
    print("SAVE: "+filename)
    
def readJsonFile(OUT_PATH):
    f = open(OUT_PATH, 'r',encoding='utf-8')
    data = json.load(f)
    f.close()
    print("LOAD: "+OUT_PATH)
    return data


def get_exception():
    etype, value, tb = exc_info()
    info, error = format_exception(etype, value, tb)[-2:]
    rd = f'Exception in: {info}: {error}'
    return rd


def weekLabel(start):
    s = datetime.fromtimestamp(start)
    e = s + timedelta(days=6)
    weekNum = int(s.strftime("%W"))+1

    dayCounter = s.strftime("%b")+" "+s.strftime("%d")+" - "+e.strftime("%b")+" "+e.strftime("%d")
    weekCounter = f"Week #{weekNum:02}" 
    
    return dayCounter, weekCounter

def monthLabel(start,end):
    s = datetime.fromtimestamp(start)
    e = datetime.fromtimestamp(end)
    
    mName = s.strftime("%B")+" "+s.strftime("%Y")
    label = s.strftime("%b")+" "+s.strftime("%d")+" - "+e.strftime("%b")+" "+e.strftime("%d")
    
    return mName,label

def timeSpentLabel(end,timeSpent):
    e = datetime.fromtimestamp(end)
    
    totalTime = int(e.strftime("%d")) * 86400 # end date * seconds in one day
    percentage = (timeSpent / totalTime) * 100
    label = format_timespan(timeSpent)
    return label,f"{percentage:.2f}%"

def getMonthlyTimestamps():
    TZ = timezone('Asia/Kolkata')
    today = datetime.now(tz=TZ)

    endDate = today - timedelta(days=today.day)
    startDate = endDate - timedelta(endDate.day - 1)
    
    startTS = startDate.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    endTS = endDate.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()

    return int(startTS),int(endTS)


def getWeeklyTimestamps():
    TZ = timezone('Asia/Kolkata')
    today = datetime.now(tz=TZ)
    sunTimedelta = today.isoweekday()
    endDate = today - timedelta(days=sunTimedelta)
    startDate = endDate - timedelta(days=6)
    
    startTS = startDate.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    endTS = endDate.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()
    return int(startTS), int(endTS)

def getTraktMonthlyTimestamps():
    s,e = getMonthlyTimestamps()
    start = datetime.fromtimestamp(s, tz=tz.utc).isoformat()
    end = datetime.fromtimestamp(e, tz=tz.utc).isoformat()
    return start,end
    

def buildChart(title,keys,values,xlabel,ylabel,barColor,savePath):
    try:
        fig, CHART = plt.subplots(figsize=(12, 4), facecolor='black')
        bars = CHART.bar(keys, values, color=barColor, edgecolor='white', width=0.5,linewidth=1.5)
        
        #title
        title_font = {'size':25, 'color':'white', 'weight':'bold','pad':20}
        title = CHART.set_title(title,**title_font)
        
        # Labels
        labels_font = {'size':18, 'color':'white', 'weight':'medium'}
        CHART.set_xlabel(xlabel, **labels_font)
        CHART.set_ylabel(ylabel, **labels_font)

        # Customize Ticks
        tick_font = {'labelsize':17, 'colors':'white'}
        CHART.tick_params(axis='x', **tick_font)
        CHART.tick_params(axis='y', **tick_font)

        # Grid & Spines
        CHART.grid(axis='y', linestyle='dashed', color='gray', alpha=0.5)
        CHART.spines['top'].set_visible(False)
        CHART.spines['right'].set_visible(False)
        CHART.spines['left'].set_color('white')
        CHART.spines['bottom'].set_color('white')

        # Background
        CHART.set_facecolor("#222222")

        # Add Data Labels
        for bar in bars:
            height = bar.get_height()
            CHART.text(bar.get_x() + bar.get_width() / 2, height + 0.1, f'{height}', 
                    ha='center', va='bottom', fontsize=17, fontweight='bold', color='white')
        #fig.set_facecolor("black")
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)

        # Save or display the chart
        plt.savefig(savePath, dpi=300, bbox_inches='tight')
        print("IMG: "+savePath)
        #plt.show()
    except Exception as e:
        print(str(e))
        