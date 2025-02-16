import os
from dotenv import load_dotenv
load_dotenv()

def getEnv(key):
    return os.getenv(key)
