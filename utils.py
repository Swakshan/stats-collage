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
    rec = {}
    freq = {}
    startFreqDate = datetime.fromtimestamp(start)

    for i in range(7):
        date = (startFreqDate + timedelta(days=i)).strftime("%d-%m")
        freq[date] = 0


    for ts in tracks:
        hr = f"{ts.hour}hrs"
        hr = ts.strftime("%I%p")
        rec[hr] = rec.get(hr,0) + 1
        
        date = ts.strftime("%d-%m")
        freq[date] = freq.get(date,0) + 1

    # # Create Figure
    fig, ax = plt.subplots(1, 2, figsize=(12, 4), facecolor='black')
    BAR_CHART = ax[0]
    PIE_CHART = ax[1]

    # Bar Chart
    bars = BAR_CHART.bar(freq.keys(), freq.values(), color='#1f77b4', edgecolor='white', linewidth=1.5)

    # Labels
    BAR_CHART.set_ylabel('Count', fontsize=12, color='white', fontweight='bold')
    BAR_CHART.set_xlabel('Date', fontsize=12, color='white', fontweight='bold')

    # Customize Ticks
    BAR_CHART.tick_params(axis='x', colors='white',labelsize=10)
    BAR_CHART.tick_params(axis='y', colors='white', labelsize=10)

    # Grid & Spines
    BAR_CHART.grid(axis='y', linestyle='dashed', color='gray', alpha=0.5)
    BAR_CHART.spines['top'].set_visible(False)
    BAR_CHART.spines['right'].set_visible(False)
    BAR_CHART.spines['left'].set_color('white')
    BAR_CHART.spines['bottom'].set_color('white')

    # Background
    BAR_CHART.set_facecolor("#222222")

    # Add Data Labels
    for bar in bars:
        height = bar.get_height()
        BAR_CHART.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{height}', 
                ha='center', va='bottom', fontsize=12, fontweight='bold', color='white')

    # Pie Chart
    wedges, texts, autotexts = PIE_CHART.pie(
        list(rec.values()),
        labels=list(rec.keys()),
        autopct='%1.1f%%',
        textprops={'fontsize': 12, 'color': 'white', 'weight': 'bold'},
        pctdistance=0.75,  # Moves percentage text inside
        wedgeprops={'edgecolor': 'black', 'linewidth': 1},
        radius=1.5,# Add border
    )

    # Title Styling
    # PIE_CHART.set_title("Pattern", **csfont, fontsize=14, pad=30)

    # Improve Text Visibility
    for text in texts:  # Label text
        text.set_color("white")
        text.set_va('center')

    for autotext in autotexts:  # Percentage text
        autotext.set_color("black")  # Inside contrast
        autotext.set_fontsize(10) 

    # Set Background Color
    fig.set_facecolor("black")

    # Adjust Layout & Show
    plt.tight_layout()
    # plt.show()
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    Image.open(img_buf).save(IMG_CHARTS, "PNG")
    img_buf.close()
        