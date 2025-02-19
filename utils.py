from datetime import datetime,timedelta
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont
from modal import IMG_CHARTS,IMG_TRACK,IMG_ARTIST,IMG_ALBUM,Data
from lastfm import getRecentTracksTimestamp,getTopAlbums,getTopArtists,getTopTracks


def combineImages(items,heading):
    lenItems = len(items)
    pad = 100
    h,w = 720,lenItems*720
    combineImage = Image.new('RGB',(w,h+pad))

    for i in range(lenItems):
        item:Data = items[i]
        img:Image = item.generateImage()
        combineImage.paste(img,(i*h,pad))

    draw = ImageDraw.Draw(combineImage)
    headfont = ImageFont.truetype("arial.ttf",80)
    draw.text((30, 10), heading,font=headfont,stroke_width=2,stroke_fill='white')
    return combineImage


def saveTopItems(start,end):
    combineImages(getTopArtists(start,end),"Top Artists").save(IMG_ARTIST)
    print("Artists saved")
    
    combineImages(getTopAlbums(start,end),"Top Albums").save(IMG_ALBUM)
    print("Albums saved")
    
    combineImages(getTopTracks(start,end),"Top Tracks").save(IMG_TRACK)
    print("Tracks saved")


def saveCharts(start,end):
    def barChart(CHART,title,keys,values,xlabel,ylabel,barColor):
        bars = CHART.bar(keys, values, color=barColor, edgecolor='white', width=0.5,linewidth=1.5)
        
        # title
        title_font = {'size':12, 'color':'white', 'weight':'bold','pad':20}
        CHART.set_title(title,**title_font)
        
        # Labels
        labels_font = {'size':12, 'color':'white', 'weight':'medium'}
        CHART.set_xlabel(xlabel, **labels_font)
        CHART.set_ylabel(ylabel, **labels_font)

        # Customize Ticks
        tick_font = {'labelsize':10, 'colors':'white'}
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
            CHART.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{height}', 
                    ha='center', va='bottom', fontsize=12, fontweight='bold', color='white')
    
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
    
    # # Create Figure
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), facecolor='black')
    weeklyChart = ax[0]
    hourlyChart = ax[1]
    
    barChart(weeklyChart,'Weekly pattern',freq.keys(), freq.values(),'Date','Count','#005582')
    barChart(hourlyChart,'Hourly pattern',hrly.keys(), hrly.values(),'Hour','Count','#00c2c7')
    
     # Set Background Color
    fig.set_facecolor("black")

    # Adjust Layout & Show
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    Image.open(img_buf).save(IMG_CHARTS, "PNG")
    img_buf.close()