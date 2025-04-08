from PIL import Image,ImageDraw,ImageFont
import requests,json
from dataclasses import dataclass
from io import BytesIO
from common import getEnv
from enum import Enum
from datetime import datetime


OUT_IMG_W=1080
OUT_IMG_H=1920
CACHE_FOLDER = "./cache"
IMGS_FOLDER = "./images"
FONT_ROBOTO_SEMI_BOLD = CACHE_FOLDER+"/Roboto-SemiBold.ttf"
IMG_TEMP = IMGS_FOLDER+"/template.jpg"
IMG_HEART = IMGS_FOLDER+"/heart.jpg"
IMG_FINAL = IMGS_FOLDER+"/final.png"
IMG_ARTIST = IMGS_FOLDER+"/TopArtist.png"
IMG_ALBUM = IMGS_FOLDER+"/TopAlbum.png"
IMG_TRACK = IMGS_FOLDER+"/TopTrack.png"
LASTM_IMG_DAILY_CHART = IMGS_FOLDER+"/dailyListenPattern.png"
LASTM_IMG_HOURLY_CHART = IMGS_FOLDER+"/hourlyListenPattern.png"
LASTM_IMG_WEEKLY_CHART = IMGS_FOLDER+"/weeklyListenPattern.png"
LASTM_IMG_DAY_CHART = IMGS_FOLDER+"/daysListenPattern.png"

TRAKT_WEEKLY_CHART = IMGS_FOLDER+"/weekly{type}Pattern.png"
TRAKT_DAY_CHART = IMGS_FOLDER+"/days{type}Pattern.png"



class MEDIA(Enum):
    MUSIC = "music"
    ANIME = "anime"
    MOVIE = "movies"
    SERIES = "shows"
    EPISODE = "episodes"


@dataclass
class MusicData:
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
        xAxis = 35
        bytes_decoded = self.__url2Img()
        # bytes_decoded = "./images/unnamed.jpeg"

        img = Image.open(bytes_decoded)
        draw = ImageDraw.Draw(img)
        
        headfont = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 70)
        subfont = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 50)
        
        if len(self.name): #if both title and artist are not empty
            draw.text((xAxis, 520), self.name,font=headfont,stroke_width=8,stroke_fill='#000')
            draw.text((xAxis, 600), self.artist,font=subfont,stroke_width=7,stroke_fill='#000')
        else:
            draw.text((xAxis, 580), self.artist,font=headfont,stroke_width=8,stroke_fill='#000')
        
        draw.text((xAxis, 660), f"{self.scrobble} Scrobbles",font=subfont,stroke_width=7,stroke_fill='#000')
        
        if(self.loved):
            heart = Image.open(IMG_HEART).convert("RGBA").rotate(355)
            img.paste(heart, (570,0),heart)

        return img
    
@dataclass
class MusicItem:
    name:str
    scrobble:int = 0
    loved:bool = False
    
    def __repr__(self):
        return f"{self.name} - {self.scrobble} - {'Loved' if self.loved else 'Not Loved'}"

    def json(self):
        return json.dumps({"name":self.name,"scrobble":self.scrobble,"loved":self.loved})

@dataclass
class MovieData:
    imdb:str
    title:str
    watched_at:datetime
    release_year:int
    
    def __repr__(self):
        return f"{self.imdb} - {self.title} - {self.watched_at} - {self.release_year}"
    
@dataclass
class SeriesData:
    series_imdb:str
    series_name:str
    
    season_number:int
    episode_imdb:str
    episode_name:str
    episode_number:int
    watched_at:datetime
    release_year:int
    
    def __repr__(self):
        return f"{self.series_imdb} - {self.series_name} - {self.season_number}\n{self.episode_imdb} - {self.episode_name} - {self.episode_number}\n{self.watched_at} - {self.release_year}"


class Tele:
    def __init__(self):
        BOT_TOKEN = getEnv("TELE_BOT_TOKEN")
        self.CHANNEL_ID = getEnv("TELE_CHNANNEL_ID")
        self.API = 'https://api.telegram.org/bot'+BOT_TOKEN
    
    def __santizeText(self,txt):
        spl_ch = ['*',  '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!' ]
        for ch in spl_ch:
            txt = txt.replace(ch,f'\\{ch}')
        return txt
    
    def __sendRequest(self,slug,data,file={}):
        api = self.API+slug
        data['chat_id'] = self.CHANNEL_ID
        req = requests.post(api,data=data,files=file)
        pkjson = req.json()
        if req.status_code==200:
            print('TELE: sent')
            return True
        else:
            print("TELE: ERROR ",str(pkjson))
            return False
    
    def sendMessage(self, message):
        msg = self.__santizeText(message)
        print(msg)
        cont = {
            "text":msg,
            "disable_web_page_preview":1,
            "parse_mode" : "MarkdownV2"
        }
        
        return self.__sendRequest('/sendMessage',cont)
        
    def sendImage(self,message,imagePath):
        cont = {'caption':message}
        file = {'photo':open(imagePath,'rb')}
        return self.__sendRequest('/sendPhoto',cont,file)



