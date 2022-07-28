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

session = requests.session()
session.cookies[".ROBLOSECURITY"] = ROBLOSECURITY
req = session.post(
    url="https://chat.roblox.com/v2/send-message",
    data={
        "message": "string",
        "conversationId": 9873047824,
        "decorators": [
          "string"
        ]
    }
)

if "X-CSRF-Token" in req.headers:
    session.headers["X-CSRF-Token"] = req.headers["X-CSRF-Token"]

req = session.post(
    url="https://chat.roblox.com/v2/send-message",
    data={
        "message": "Hello World!",
        "conversationId": 9873047824,
        "decorators": [
          "string"
        ]
    }
)

print(json.loads(req.text))