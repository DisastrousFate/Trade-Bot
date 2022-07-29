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

    def itemsWanted(itemsString): 
        for itemId in itemsString.split():
            rbx_request("GET", "https://catalog.roblox.com/v1/catalog/items/details")
            #print(rbx_request("GET", "https://catalog.roblox.com/v1/catalog/items/details").text)

    print("Checking auth code..")
    req = rbx_request("POST", "https://trades.roblox.com/v1/trades/Inbound?sortOrder=Asc&limit=10") # Check for incorrect auth code
    if req.status_code != 200:
        print(".ROBLOSECURITY Incorrect. Check Settings")
        exit()

    itemsWanted(input("Enter item id's that you want, each id seperated by whitespace: "))
    print("Correct! Starting trade bot..")

    page = None
    pageNum = 0
    nextPageCursor = None

    def switchPages():
        global pageNum, page, GROUPURL, nextPageCursor
        if pageNum == 0:
            page = json.loads(rbx_request("GET", "https://groups.roblox.com/v1/groups/650266/roles/21783158/users?sortOrder=Desc&limit=100").text)
            pageNum =+ 1
            nextPageCursor = page.get("nextPageCursor")
        elif pageNum == 1:
            GROUPURL = GROUPURL + "&cursor="+page.get("nextPageCursor")
            print(GROUPURL)
            page = json.loads(rbx_request("GET", "https://groups.roblox.com/v1/groups/650266/roles/21783158/users?sortOrder=Desc&limit=100").text)
    
    switchPages()
    #for player in page.get("data"):
    #    isPremium = rbx_request("GET", "https://premiumfeatures.roblox.com/v1/users/"+str(player.get("userId"))+"/validate-membership").text
      #  if isPremium == "true":
