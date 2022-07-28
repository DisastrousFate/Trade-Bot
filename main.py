import requests
import json

ROBLOSECURITY = ""
GROUPURL = "https://groups.roblox.com/v1/groups/650266/roles/21783158/users?sortOrder=Desc&limit=100"

with open("Settings.txt") as f: # Read settings from "Settings.txt"
    for line in f:
        s = line.split("=")
        if s[0].strip() == ".ROBLOSECURITY":
            ROBLOSECURITY = s[1].strip()

session = requests.session()
session.cookies[".ROBLOSECURITY"] = ROBLOSECURITY

def rbx_request(method, url, **kwargs):
    request = session.request(method, url, **kwargs)
    method = method.lower()
    if (method == "post") or (method == "put") or (method == "patch") or (method == "delete"):
        if "X-CSRF-Token" in request.headers:
            session.headers["X-CSRF-Token"] = request.headers["x-CSRF-Token"]
            if request.status_code == 403: # request failed, send again
                request = session.request(method, url, **kwargs)
    return request

if __name__ == "__main__":

    print("Checking auth code..")
    req = rbx_request("GET", "https://trades.roblox.com/v1/trades/Inbound?sortOrder=Asc&limit=10") # Check for incorrect auth code
    if req.status_code != 200:
        print(".ROBLOSECURITY Incorrect. Check Settings")
        exit()
    print("Correct! Starting trade bot..")

    page = None
    pageNum = 0

    def switchPages():
        if pageNum == 0:
            page = json.loads(rbx_request("GET", "https://groups.roblox.com/v1/groups/650266/roles/21783158/users?sortOrder=Desc&limit=100").text)
            pageNum =+ 1
        elif pageNum == 1:
            GROUPURL =+ "&cursor="+page.get("previousPageCursor")
            print(GROUPURL)
            page = json.loads(rbx_request("GET", "https://groups.roblox.com/v1/groups/650266/roles/21783158/users?sortOrder=Desc&limit=100").text)
    
    switchPages()
    print(page)