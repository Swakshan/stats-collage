import os
from dotenv import load_dotenv
import json

load_dotenv()

def getEnv(key):
    return os.getenv(key)

def printJson(data):
    print(json.dumps(data,indent=4))

def writeJsonFile(data,filename):
    with open(filename, 'w',encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))

def readJsonFile(OUT_PATH):
    f = open(OUT_PATH, 'r',encoding='utf-8')
    data = json.load(f)
    f.close()
    return data
