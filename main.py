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
    
    for itemWanted in itemsWanted:
        index = 0

        pageNum, page, nextPageCursor = switchPages(itemWanted)
        for user in page["data"]:
            if user["owner"] == "null" or user["owner"] == None: # Check if user has premium
                continue

        tradereq = rbx_request("POST", "https://trades.roblox.com/v1/trades/send", {
                "offers": [
	                {
			            "userId": 368071412,
			            "userAssetIds": [10159911699],
			            "robux": 0,
		            },
		            {
			            "userId": USERID,
			            "userAssetIds": [tradeItems[0]],
			            "robux": 0,
		            },
	            ],
            })
        print(tradereq.text)