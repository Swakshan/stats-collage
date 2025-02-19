from PIL import Image,ImageDraw,ImageFont
import requests
from dataclasses import dataclass
from io import BytesIO
from datetime import datetime,timedelta
import matplotlib.pyplot as plt

IMG_ARTIST = "./images/TopArtist.png"
IMG_ALBUM = "./images/TopAlbum.png"
IMG_TRACK = "./images/TopTrack.png"
IMG_CHARTS = "./images/Charts.png"


@dataclass
class Data:
    name: str
    artist: str
    imageUrl: str
    scrobble: int = 0
    
    def __repr__(self):
        return f"Data(name={self.name}, artist={self.artist}, imageUrl={self.imageUrl}, scrobble={self.scrobble})"
    
    def __url2Img(self):
        content = requests.get(self.imageUrl).content
        return BytesIO(content)
    
    def generateImage(self):
        fontName = "arial.ttf"
        xAxis = 35
        bytes_decoded = self.__url2Img()
        img = Image.open(bytes_decoded)
        draw = ImageDraw.Draw(img)
        
        headfont = ImageFont.truetype(fontName, 50)
        subfont = ImageFont.truetype(fontName, 30)
        
        if len(self.name):
            draw.text((xAxis, 530), self.name,font=headfont,stroke_width=10,stroke_fill='#000')
            draw.text((xAxis, 610), self.artist,font=subfont,stroke_width=9,stroke_fill='#000')
        else:
            draw.text((xAxis, 590), self.artist,font=headfont,stroke_width=10,stroke_fill='#000')
        
        draw.text((xAxis, 670), f"{self.scrobble} Scrobbles",font=subfont,stroke_width=9,stroke_fill='#000')
        return img


def formCharts(tracks,start):
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