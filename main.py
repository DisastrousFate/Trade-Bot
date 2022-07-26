import requests
import json

WebRoblox = requests.get("https://users.roblox.com/v1/users/2046139136")
print(WebRoblox.text)
