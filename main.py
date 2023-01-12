import requests
import json
import time
import ratelimit

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
    asset_offers = input().split()

    print("Enter asset id's of limiteds to request, each seperated by whitespace: ")
    asset_requests = input().split()

    print("Starting trade bot..")
    timeTaken(True)

    # Convert client asset id's to UAID
    client_UAIDs = []
    client_inv = json.loads(rbx_request("GET", "https://inventory.roblox.com/v1/users/"+str(USERID)+"/assets/collectibles?sortOrder=Desc&limit=100").text)
    for asset_offer in asset_offers:
        for asset in client_inv["data"]:
            if asset["assetId"] == int(asset_offer):
                client_UAIDs.append(asset["userAssetId"])
    
    counter = 0 
    while True:        
        if counter == 0:
            asset_owners, next_page = asset_owner_request(asset_requests[0], "")  # LOOP THROUGH PLAYERS WITH FIRST LIMITED
        if counter == 1:
            asset_owners, next_page = asset_owner_request(asset_requests[0], next_page)

        for user in asset_owners["data"]:  # LOOP THROUGH USERS
            # Check if user has premium
            if user["owner"] == "null" or user["owner"] == None: 
                continue

            # Check if you can trade with them
            req123 = json.loads(rbx_request("GET", "https://trades.roblox.com/v1/users/"+ str(user["owner"]["id"]) +"/can-trade-with").text)
            if not req123.get("canTrade", True):
                continue

            # Search through user inventory
            user_inv = json.loads(rbx_request("GET", "https://inventory.roblox.com/v1/users/"+str(user["owner"]["id"])+"/assets/collectibles?sortOrder=Desc&limit=100").text)

            item_counts = {}
            allItems = {}
            hasAllItems = False
            # Loop through user's inventory and count each item
            print(user_inv["data"])
            for item in user_inv["data"]:
                
                # Check if user has all requested items
                if str(item["assetId"]) in asset_requests: # Check id match
                    if item["userAssetId"] in list(item_counts.keys()): # if 1 or more
                        item_counts[item["assetId"]] += 1
                    else:
                        item_counts[item["assetId"]] = 1

            # Check item amount
            for item, amount in item_counts.items():
                if amount >= asset_requests.count(str(item)):
                    allItems[item] = True
                else:
                    allItems[item] = False
            if not any(value == False for value in list(allItems.values())):
                hasAllItems = True

            # Convert requested asset id's to UAID
            request_UAIDs = []
            for request_item in asset_requests:
                for asset in user_inv["data"]:
                    if asset["assetId"] == int(request_item):
                        request_UAIDs.append(asset["userAssetId"])

            if (hasAllItems) and (len(asset_requests) == len(item_counts)):
                trade_send(USERID, client_UAIDs, user["owner"]["id"], request_UAIDs)
                time.sleep(10)

        counter = 1
        
#//////////////////////////////////////////////////////////////////////////////////////////////////////////#
@ratelimit.rate_limited(30, 10)  # allow the function to be called 30 times
def rbx_request(method, url, **kwargs):
    request = session.request(method, url, **kwargs) 
    method = method.lower()
    if (method == "post") or (method == "put") or (method == "patch") or (method == "delete"):
        if "X-CSRF-Token" in request.headers:
            session.headers["X-CSRF-Token"] = request.headers["x-CSRF-Token"]
            if request.status_code == 403: # request failed, send again
                request = session.request(method, url, **kwargs)

    return request

def asset_owner_request(asset_ids, next_page):
    """Get a list of users who own a specific asset.

    Parameters:
    asset_id (int): The ID of the asset.

    Returns:
    dict: A dictionary containing information about the asset owners.
    """
    if next_page == "":
        asset_owners = json.loads(rbx_request("GET", f"https://inventory.roblox.com/v2/assets/{asset_ids}/owners?sortOrder=Desc&limit=100").text)
    else:
        asset_owners = json.loads(rbx_request("GET", f"https://inventory.roblox.com/v2/assets/{asset_ids}/owners?sortOrder=Desc&limit=100&cursor={next_page}").text)

    # Check for same userid's and remove
    asset_owners_done = {}
    for user in asset_owners["data"]:
        if user.get("owner"): 
            if asset_owners_done.get(user["owner"]["id"]):
                asset_owners_done[user["owner"]["id"]] = asset_owners_done[user["owner"]["id"]] + 1
            else:
                asset_owners_done[user["owner"]["id"]] =  1

    for userId, amount in asset_owners_done.items():
            
        if user.get("owner"):
            if amount > 1:
                print("Over 1")
                for i, user in enumerate(asset_owners["data"]):
                    if user.get("owner"):
                        if user["owner"]["id"] == userId:
                            for x in range(amount - 1):
                                asset_owners["data"].pop(i)

    if "nextPageCursor" in asset_owners:
        next_page = asset_owners["nextPageCursor"]
    else:
        next_page = ""

    return asset_owners, next_page

def timeTaken(start):
    timeList = []
    if start == True:
        start_time = time.perf_counter()
    else:
        end_time = time.perf_counter()
        timeList.append(f"{(end_time - start_time):.2f}s")
        print(timeList)



def trade_send(user_id, offerUAID, user_trade_id, requestUAID):
    """Send a trade offer to another user.

    Parameters:
    userId (int): The ID of the first user.
    userAssetIds (list): A list of UAIDs of assets that the first user is offering.
    userId (int): The ID of the second user.
    userAssetIds (list): A list of UAIDs of assets that the second user is offering.
    """

    print("Target: " + str(user_trade_id) + "  Sending trade..")
    tradereq = session.post(
        url="https://trades.roblox.com/v1/trades/send",
        data=json.dumps({
            "offers": [
                {
                    "userId": user_trade_id,
                    "userAssetIds": requestUAID,
                    "robux": 0
                },
                {
                    "userId": user_id,
                    "userAssetIds": offerUAID,
                    "robux": 0
                }
            ]
        })
    )
    if tradereq.status_code == 200:
        print("Trade successful.  Trade Id: " + tradereq.text)

        timeTaken(False)
        timeTaken(True)
    else:
        print("ERROR!!!    " + str(tradereq.text))
    time.sleep(6)

if __name__ == "__main__":
    main()