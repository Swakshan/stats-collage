import sys
import utils.lastfm as lf
import utils.trakt as trk

from modal import Tele

CH = int(sys.argv[1])

tele = Tele()
try:
    msg = ""
    img = ""

    if CH == 1:
        msg,img = lf.buildWeekly()
    elif CH == 2:
        msg, img = lf.buildMonthly()
    elif CH == 3:
        msg, img = trk.buildMonthly()
        
    if len(msg) and len(img):
        tele.sendImage(message=msg,imagePath=img)

    
except Exception as e:
    tele.sendMessage("ERROR: "+str(e))
    

