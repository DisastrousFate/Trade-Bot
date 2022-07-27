from math import fabs
from urllib.robotparser import RobotFileParser
import requests
import json

ROBLOSECURITY = ""
SCRIPT_ID = ""

with open("Settings.txt") as f: # Read settings from "Settings.txt"
    for line in f:
        s = line.split("=")
        if s[0].strip() == ".ROBLOSECURITY":
            ROBLOSECURITY = s[1].strip()
        elif s[0].strip() == "Script_Id":
            SCRIPT_ID = s[1].strip()

