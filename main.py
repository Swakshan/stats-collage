import sys
from utils import buildWeekly
from modal import Tele

CH = int(sys.argv[1])

tele = Tele()
try:
    if CH == 1:
        msg,img = buildWeekly()
        tele.sendImage(message=msg,imagePath=img)
    
except Exception as e:
    tele.sendMessage("ERROR: "+str(e))
    

