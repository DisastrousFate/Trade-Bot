import requests
import json
import time

def main():

    ROBLOSECURITY = ""
    USERID = 0

    # Read settings from "Settings.txt"
    print("Checking auth code..")
    with open("Settings.txt") as f:
        for line in f:
            s = line.split("=")
            if s[0].strip() == ".ROBLOSECURITY":
                ROBLOSECURITY = s[1].strip()
            if s[0].strip() == "UserId":
                USERID = int(s[1].strip())

    global session
    session = requests.session()
    session.cookies[".ROBLOSECURITY"] = ROBLOSECURITY
    session.headers["Content-Type"] = "application/json"

    # Check for incorrect auth code
    req = rbx_request("GET", "https://trades.roblox.com/v1/trades/Inbound?sortOrder=Asc&limit=10")
    if req.status_code != 200:
        print(".ROBLOSECURITY Incorrect. Check Settings")
        exit()
    print("Auth code correct!")

    req2 = session.post(url="https://auth.roblox.com/")
    if "X-CSRF-Token" in req2.headers:  # check if token is in response headers
        session.headers["X-CSRF-Token"] = req2.headers["X-CSRF-Token"]

    print("Enter asset id's of limiteds to offer, each seperated by whitespace: ")
    assetOffers = input().split()

    print("Enter asset id's of limiteds to request, each seperated by whitespace: ")
    assetRequests = input().split()

    print("Starting trade bot..")

    # Convert client asset id's to UAID
    clientUAIDs = []
    clientInv = json.loads(rbx_request("GET", "https://inventory.roblox.com/v1/users/"+str(USERID)+"/assets/collectibles?sortOrder=Desc&limit=100").text)
    for assetoffer in assetOffers:
        for asset in clientInv["data"]:
            if asset["assetId"] == int(assetoffer):
                clientUAIDs.append(asset["userAssetId"])

    assetOwners, nextPage = assetOwner_request(assetRequests[0]) ## LOOP THROUGH PLAYERS WITH FIRST LIMITED
    for user in assetOwners["data"]:        ## LOOP THROUGH USERS
        # Check if user has premium
        if user["owner"] == "null" or user["owner"] == None: 
            continue
        # Check if you can trade with them
        if json.loads(rbx_request("GET", "https://trades.roblox.com/v1/users/"+ str(user["owner"]["id"]) +"/can-trade-with").text)["canTrade"] == False:
            continue
        
        # Search through user inventory
        userInv = json.loads(rbx_request("GET", "https://inventory.roblox.com/v1/users/"+str(user["owner"]["id"])+"/assets/collectibles?sortOrder=Desc&limit=100").text)
        numOfAssets = 0

        if len(assetRequests) != 1:
            for assetRequest in assetRequests[1:]:
                for userDict in userInv["data"]:
                    if int(assetRequest) == userDict["assetId"]:
                        numOfAssets += 1
                        if numOfAssets == len(assetRequests) - 1:
                            print("trade here!")
                            # initiate trade
        else:
            for userDict in userInv["data"]:
                if int(assetRequests[0]) == userDict["assetId"]:
                    time.sleep(1)
                    print(userDict["userAssetId"])
                    trade_send(USERID, clientUAIDs, user["owner"]["id"], [userDict["userAssetId"]])
                    break


def rbx_request(method, url, **kwargs):

        request = session.request(method, url, **kwargs) 
        method = method.lower()
        if (method == "post") or (method == "put") or (method == "patch") or (method == "delete"):
            if "X-CSRF-Token" in request.headers:
                session.headers["X-CSRF-Token"] = request.headers["x-CSRF-Token"]
                if request.status_code == 403: # request failed, send again
                    request = session.request(method, url, **kwargs)
        return request

def assetOwner_request(assetId, **page):
    req = json.loads(rbx_request("GET", "https://inventory.roblox.com/v2/assets/"+str(assetId)+"/owners?sortOrder=Desc&limit=100").text)
    nextPage = ""
    if "nextPageCursor" in req:
        nextPage = req["nextPageCursor"]
    
    return req, nextPage

def trade_send(clientId, offerUAID, userId, requestUAID):

    print("Target: " + str(userId) + "  Sending trade..")
    tradereq = session.post(
        url="https://trades.roblox.com/v1/trades/send",
        data=json.dumps({
            "offers": [
                {
                    "userId": userId,
                    "userAssetIds": requestUAID,
                    "robux": 0
                },
                {
                    "userId": clientId,
                    "userAssetIds": offerUAID,
                    "robux": 0
                }
            ]
        })
    )
    if tradereq.status_code == 200:
        print("Trade successful.  Trade Id: " + tradereq.text)
    else:
        print("ERROR!!!    " + str(tradereq.text))
if __name__ == "__main__":
    main()
