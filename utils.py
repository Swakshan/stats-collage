from PIL import Image,ImageDraw,ImageFont
import requests
from dataclasses import dataclass
from io import BytesIO

@dataclass
class Data:
    name: str
    artist: str
    imageUrl: str
    scrobble: int = 0
    image:Image = None
    
    def __repr__(self):
        return f"Data(name={self.name}, artist={self.artist}, imageUrl={self.imageUrl}, scrobble={self.scrobble})"
    
    def url2Img(self):
        content = requests.get(self.imageUrl).content
        return BytesIO(content)
    
    def generateImage(self):
        fontName = "arial.ttf"
        xAxis = 35
        bytes_decoded = self.url2Img()
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
        self.image = img
        # img.show()

    