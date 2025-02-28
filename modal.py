from PIL import Image,ImageDraw,ImageFont
import requests,json
from dataclasses import dataclass
from io import BytesIO
from datetime import datetime,timedelta
import matplotlib.pyplot as plt

IMG_TEMP = "./images/template.jpg"
IMG_FINAL = "./images/final.png"
IMG_ARTIST = "./images/TopArtist.png"
IMG_ALBUM = "./images/TopAlbum.png"
IMG_TRACK = "./images/TopTrack.png"
LASTM_IMG_DAILY_CHART = "./images/dailyListenPattern.png"
LASTM_IMG_HOURLY_CHART = "./images/hourlyListenPattern.png"


@dataclass
class Data:
    name: str
    artist: str
    imageUrl: str
    scrobble: int = 0
    loved:bool = False
    
    def __repr__(self):
        return f"Data(name={self.name}, artist={self.artist}, imageUrl={self.imageUrl}, scrobble={self.scrobble})"
    
    def __url2Img(self):
        content = requests.get(self.imageUrl).content
        return BytesIO(content)
    
    def generateImage(self):
        fontName = "arial.ttf"
        xAxis = 35
        bytes_decoded = self.__url2Img()
        # bytes_decoded = "./images/unnamed.jpeg"

        img = Image.open(bytes_decoded)
        draw = ImageDraw.Draw(img)
        
        headfont = ImageFont.truetype(fontName, 70)
        subfont = ImageFont.truetype(fontName, 50)
        
        if len(self.name): #if both title and artist are not empty
            draw.text((xAxis, 520), self.name,font=headfont,stroke_width=8,stroke_fill='#000')
            draw.text((xAxis, 600), self.artist,font=subfont,stroke_width=7,stroke_fill='#000')
        else:
            draw.text((xAxis, 580), self.artist,font=headfont,stroke_width=8,stroke_fill='#000')
        
        draw.text((xAxis, 660), f"{self.scrobble} Scrobbles",font=subfont,stroke_width=7,stroke_fill='#000')
        return img
    
@dataclass
class Item:
    name:str
    scrobble:int = 0
    loved:bool = False
    
    def __str__(self):
        return f"{self.name} - {self.scrobble} - {'Loved' if self.loved else 'Not Loved'}"

    def json(self):
        return json.dumps({"name":self.name,"scrobble":self.scrobble,"loved":self.loved})

