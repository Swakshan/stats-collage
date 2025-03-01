import sys
from utils import buildWeekly,buildMonthly
from modal import Tele

CH = int(sys.argv[1])

tele = Tele()
try:
    msg = ""
    img = ""

    if CH == 1:
        msg,img = buildWeekly()
    elif CH == 2:
        msg, img = buildMonthly()
    
    if len(msg) and len(img):
        pass
        # tele.sendImage(message=msg,imagePath=img)

    
except Exception as e:
    tele.sendMessage("ERROR: "+str(e))
    

