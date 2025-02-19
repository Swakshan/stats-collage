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