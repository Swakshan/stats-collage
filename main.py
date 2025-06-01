import sys
import utils.lastfm as lf
import utils.trakt as trk
from common import get_exception


from modal import Tele

CH = int(sys.argv[1])

tele = Tele()
try:
    msg = ""
    imgs = []

    if CH == 1:
        msg,img = lf.buildWeekly()
    elif CH == 2:
        msg, img = lf.buildMonthly()
        img2 = lf.buildMonthlyCalendar()
        imgs.append(img2)
    elif CH == 3:
        msg, img = trk.buildMonthly()
        
    imgs.append(img)

    if len(msg) and len(img):
        tele.sendImage(message=msg,imagePath=imgs)

    
except Exception as e:
    err = get_exception()
    print(err)
    tele.sendMessage("ERROR: "+err)
    

