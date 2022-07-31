import requests
import json

ROBLOSECURITY = ""
USERID = ""

with open("Settings.txt") as f: # Read settings from "Settings.txt"
    for line in f:
        s = line.split("=")
        if s[0].strip() == ".ROBLOSECURITY":
            ROBLOSECURITY = s[1].strip()
        if s[0].strip() == "UserId":
            USERID = s[1].strip()
            print(USERID)

session = requests.session()
session.cookies[".ROBLOSECURITY"] = ROBLOSECURITY
session.headers["Content-Type"] = "application/json"



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

    req2 = session.post(url="https://auth.roblox.com/")
    if "X-CSRF-Token" in req2.headers:  # check if token is in response headers
        print("aa")
        session.headers["X-CSRF-Token"] = req2.headers["X-CSRF-Token"]

    print("Enter item id's of limiteds you want, each seperated by whitespace: ")
    itemsWanted = input().split()

    print("Enter item id's of limiteds to trade, each seperated by whitespace")
    tradeItems = input().split()

    print("Correct! Starting trade bot..")

    def switchPages(itemWanted):
        pageNum, page, nextPageCursor = 0, None, None
        if pageNum == 0:
            page = json.loads(rbx_request("GET", "https://inventory.roblox.com/v2/assets/"+itemWanted+"/owners?sortOrder=Desc&limit=100").text)
            pageNum =+ 1
            nextPageCursor = page.get("nextPageCursor")
        else:
            page = json.loads(rbx_request("GET", "https://inventory.roblox.com/v2/assets/"+itemWanted+"/owners?sortOrder=Desc&limit=100&"+nextPageCursor).text)
            pageNum =+ 1
            nextPageCursor = page.get("nextPageCursor")
        return pageNum, page, nextPageCursor

    def sendTrade(UID, UAID, UID2, UAID2):
        tradereq = session.post(url = "https://trades.roblox.com/v1/trades/send",
            data = json.dumps({
                "offers": [
	                {
			            "userId": UID,
			            "userAssetIds": [UAID],
			            "robux": 0,
		            },
		            {
			            "userId": UID2,
			            "userAssetIds": [UAID2],
			            "robux": 0,
		            },
	            ],
            }),
            headers = session.headers,
            cookies = session.cookies)
    
    for itemWanted in itemsWanted:
        index = 0

        pageNum, page, nextPageCursor = switchPages(itemWanted)
        for user in page["data"]:
            if user["owner"] == "null" or user["owner"] == None: # Check if user has premium
                continue
            