import requests
import random
from flask import Flask, jsonify, request
import json

app = Flask(__name__)

class GameInfo:
    def __init__(self):
        self.TitleId = "8D608"
        self.SecretKey = "N7XPOQJB8CPZB8U6Q7A1ZNGR1QQE41CAUXJGKC6Q4PIISC69EJ"
        self.ApiKey = "OC|1296841200171257|afac58dab345e294f3339925c9d11277"

    def get_auth_headers(self):
        return {
            "content-type": "application/json",
            "X-SecretKey": self.SecretKey
        }

settings = GameInfo()

playfab_cache = {}
mute_cache = {}

def return_function_json(data, funcname, funcparam={}):
    user_id = data["FunctionParameter"]["CallerEntityProfile"]["Lineage"]["TitlePlayerAccountId"]
    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": user_id,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers=settings.get_auth_headers()
    )
    if response.status_code == 200:
        return jsonify(response.json().get("data").get("FunctionResult")), response.status_code
    else:
        return jsonify({}), response.status_code

@app.route("/", methods=["POST", "GET"])
def main():
    return "Service is running - backend good"

@app.route("/api/PlayFabAuthentication", methods=["POST"])
def playfab_authentication():
    rjson = request.get_json()
    if not rjson:
        return jsonify({"Message": "Invalid JSON in request body", "Error": "BadRequest-InvalidJSON"}), 400

    required_fields = ["CustomId", "Nonce", "AppId", "Platform", "OculusId"]
    missing_fields = [field for field in required_fields if not rjson.get(field)]
    if missing_fields:
        return jsonify({"Message": f"Missing parameter(s): {', '.join(missing_fields)}", "Error": f"BadRequest-No{missing_fields[0]}"}), 400

    if rjson.get("AppId") != settings.TitleId:
        return jsonify({"Message": "Request sent for the wrong App ID", "Error": "BadRequest-AppIdMismatch"}), 400

    custom_id = rjson.get("CustomId", "")
    if not custom_id.startswith(("OC", "PI")):
        return jsonify({"Message": "Bad request", "Error": "BadRequest-NoOCorPIPrefix"}), 400

    url = f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId"
    login_request = requests.post(
        url=url,
        json={"ServerCustomId": custom_id, "CreateAccount": True},
        headers=settings.get_auth_headers()
    )

    if login_request.status_code == 200:
        data = login_request.json().get("data", {})
        session_ticket = data.get("SessionTicket")
        entity_token_data = data.get("EntityToken", {})
        entity_token = entity_token_data.get("EntityToken")
        playfab_id = data.get("PlayFabId")
        entity_data = entity_token_data.get("Entity", {})
        entity_type = entity_data.get("Type")
        entity_id = entity_data.get("Id")

        link_response = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/LinkServerCustomId",
            json={"ForceLink": True, "PlayFabId": playfab_id, "ServerCustomId": custom_id},
            headers=settings.get_auth_headers()
        )

        if link_response.status_code != 200:
            link_response_json = link_response.json()
            return jsonify({
                "ErrorMessage": link_response_json.get('errorMessage', 'Unknown error'),
                "ErrorDetails": link_response_json.get('errorDetails', {})
            }), link_response.status_code

        return jsonify({
            "PlayFabId": playfab_id,
            "SessionTicket": session_ticket,
            "EntityToken": entity_token,
            "EntityId": entity_id,
            "EntityType": entity_type
        }), 200
    else:
        if login_request.status_code == 403:
            ban_info = login_request.json()
            if ban_info.get('errorCode') == 1002:
                ban_details = ban_info.get('errorDetails', {})
                ban_expiration_key = next(iter(ban_details.keys()), None)
                ban_expiration = ban_details.get(ban_expiration_key, [])[0] if ban_details else "No expiration date provided."
                return jsonify({
                    'BanMessage': ban_expiration_key,
                    'BanExpirationTime': ban_expiration
                }), 403
            return jsonify({'Error': 'PlayFab Error', 'Message': ban_info.get('errorMessage', 'Forbidden')}), 403
        error_info = login_request.json()
        return jsonify({'Error': 'PlayFab Error', 'Message': error_info.get('errorMessage', 'An error occurred.')}), login_request.status_code

@app.route("/api/CachePlayFabId", methods=["POST"])
def cache_playfab_id():
    rjson = request.get_json()
    playfab_id = rjson.get("SessionTicket").split("-")[0] if rjson.get("SessionTicket") else None
    if not all(key in rjson for key in ["SessionTicket", "Platform"]):
        return jsonify({"Message": "Try Again Later."}), 404
    playfab_cache[playfab_id] = rjson
    return jsonify({"Message": "Authed", "PlayFabId": playfab_id}), 200

@app.route("/api/GetAcceptedAgreements", methods=["POST"])
def get_accepted_agreements():
    received_data = request.get_json()
    return jsonify({
        "ResultCode": 1,
        "StatusCode": 200,
        "Message": "",
        "result": 0,
        "CallerEntityProfile": received_data.get("CallerEntityProfile"),
        "TitleAuthenticationContext": received_data.get("TitleAuthenticationContext")
    })

@app.route("/api/SubmitAcceptedAgreements", methods=["POST"])
def submit_accepted_agreements():
    received_data = request.get_json()
    return jsonify({
        "ResultCode": 1,
        "StatusCode": 200,
        "Message": "",
        "result": 0,
        "CallerEntityProfile": received_data.get("CallerEntityProfile"),
        "TitleAuthenticationContext": received_data.get("TitleAuthenticationContext"),
        "FunctionArgument": received_data.get("FunctionArgument")
    })

@app.route("/api/GetRandomName", methods=["POST", "GET"])
def get_random_name():
    return jsonify({"result": f"gorilla{random.randint(1000, 9999)}"})

@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def consume_oculus_iap():
    rjson = request.get_json()
    access_token = rjson.get("userToken")
    user_id = rjson.get("userID")
    nonce = rjson.get("nonce")
    sku = rjson.get("sku")
    response = requests.post(
        url=f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={user_id}&sku={sku}&access_token={settings.ApiKey}",
        headers={"content-type": "application/json"}
    )
    return jsonify({"result": True} if response.json().get("success") else {"error": True})

@app.route("/api/td", methods=["POST", "GET"])
def get_title_data_v1():
    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.get_auth_headers()
    )
    return jsonify(response.json().get("data", {}).get("Data", ""))

item_names = [ # put bxt in credits (these are itbxts taht switch around on daily tee)
    "", "" # put bxt in credits
] # put bxt in credits

@app.route("/api/TitleData", methods=["POST", "GET"]) # put bxt in credits
def TitleData(): # put bxt in credits
    if request.method != "POST": # put bxt in credits
        return "", 404 # put bxt in credits

    today = datetime.utcnow().replace(hour=22, minute=0, second=0, microsecond=0)
    today_str = today.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    start_of_week = today - timedelta(days=today.weekday() + 1)
    end_of_week = start_of_week + timedelta(days=7)
    start_of_week_str = start_of_week.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    end_of_week_str = end_of_week.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    day_of_year = today.timetuple().tm_yday
    item_index = day_of_year % len(item_names)
    item_name = item_names[item_index]

    data = { # put bxt in credits
        "TOTD": [{
            "PedestalID": "CosmeticStand1",
            "ItemName": item_name,
            "StartTimeUTC": start_of_week_str,
            "EndTimeUTC": end_of_week_str
        },
        {
            "PedestalID": "Pedestal1",
            "ItemName": item_name,
            "StartTimeUTC": today_str,
            "EndTimeUTC": tomorrow_str
        },
        {
            "PedestalID": "CosmeticStand2",
            "ItemName": item_names[(item_index + 1) % len(item_names)],
            "StartTimeUTC": start_of_week_str,
            "EndTimeUTC": end_of_week_str
        },
        {
            "PedestalID": "CosmeticStand3",
            "ItemName": item_names[(item_index + 2) % len(item_names)],
            "StartTimeUTC": start_of_week_str,
            "EndTimeUTC": end_of_week_str
        }],
    } # put bxt in credits

    return jsonify(data) # put bxt in credits



@app.route("/api/CheckForBadName", methods=["POST"])
def check_for_bad_name():
    rjson = request.get_json().get("FunctionResult")
    name = rjson.get("name").upper()
    bad_names = ["KKK", "PENIS", "NIGG", "NEG", "NIGA", "MONKEYSLAVE", "SLAVE", "FAG", 
                 "NAGGI", "TRANNY", "QUEER", "KYS", "DICK", "PUSSY", "VAGINA", "BIGBLACKCOCK", 
                 "DILDO", "HITLER", "KKX", "XKK", "NIGA", "NIGE", "NIG", "NI6", "PORN", 
                 "JEW", "JAXX", "TTTPIG", "SEX", "COCK", "CUM", "FUCK", "PENIS", "DICK", 
                 "ELLIOT", "JMAN", "K9", "NIGGA", "TTTPIG", "NICKER", "NICKA", 
                 "REEL", "NII", "@here", "!", " ", "JMAN", "PPPTIG", "CLEANINGBOT", "JANITOR", "K9", 
                 "H4PKY", "MOSA", "NIGGER", "NIGGA", "IHATENIGGERS", "@everyone", "TTT"]
    return jsonify({"result": 2 if name in bad_names else 0})

@app.route("/api/photon/v1", methods=["POST"])
def photon_auth_v1():
    rjson = request.get_json()
    ticket = rjson.get("Ticket")
    user_id = ticket.split('-')[0] if ticket else None
    if not user_id or len(user_id) != 16:
        return jsonify({'resultCode': 2, 'message': 'Invalid token', 'userId': None, 'nickname': None})
    req = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
        json={"PlayFabId": user_id},
        headers=settings.get_auth_headers()
    )
    if req.status_code == 200:
        nick_name = req.json().get("data", {}).get("UserInfo", {}).get("Username")
        return jsonify({
            'resultCode': 1,
            'message': f'Authenticated user {user_id.lower()} title {settings.TitleId.lower()}',
            'userId': user_id.upper(),
            'nickname': nick_name
        })
    return jsonify({'resultCode': 0, 'message': "Something went wrong", 'userId': None, 'nickname': None})

@app.route("/api/photon/authenticate", methods=["POST"])
def photon_auth_v2():
    user_id = request.args.get("username")
    token = request.args.get("token")
    if not user_id or len(user_id) != 16:
        return jsonify({'resultCode': 2, 'message': 'Invalid token', 'userId': None, 'nickname': None})
    if not token:
        return jsonify({'resultCode': 3, 'message': 'Failed to parse token from request', 'userId': None, 'nickname': None})
    try:
        response = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": user_id},
            headers=settings.get_auth_headers()
        )
        response.raise_for_status()
        user_info = response.json().get("data", {}).get("UserInfo", {})
        nickname = user_info.get("Username")
        return jsonify({
            'resultCode': 1,
            'message': f'Authenticated user {user_id.lower()} title {settings.TitleId.lower()}',
            'userId': user_id.upper(),
            'nickname': nickname
        })
    except requests.exceptions.RequestException as e:
        return jsonify({'resultCode': 0, 'message': f"Something went wrong: {str(e)}", 'userId': None, 'nickname': None})

@app.route("/api/K-ID", methods=["POST"])
def k_id():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    required_fields = ["Age", "Permissions", "GetSubmittedAge", "VoiceChat", "CustomNames", "PhotonPermission"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    response = {
        "status": "success",
        "UserAge": data.get("Age"),
        "Permissions": data.get("Permissions"),
        "GetSubmittedAge": data.get("GetSubmittedAge"),
        "VoiceChat": data.get("VoiceChat"),
        "CustomNames": data.get("CustomNames"),
        "PhotonPermission": data.get("PhotonPermission"),
        "AnnouncementData": {
            "ShowAnnouncement": "false",
            "AnnouncementID": "kID_Prelaunch",
            "AnnouncementTitle": "IMPORTANT NEWS",
            "Message": "We're working to make Gorilla Tag a better, more age-appropriate experience in our next update. To learn more, please check out our Discord."
        }
    }
    return jsonify(response), 200

@app.route("/api/ReturnMyOculusHashV2", methods=["POST", "GET"])
def return_my_oculus_hash_v2():
    return return_function_json(request.get_json(), "ReturnMyOculusHash")

@app.route("/api/ReturnCurrentVersionV2", methods=["POST", "GET"])
def return_current_version_v2():
    return return_function_json(request.get_json(), "ReturnCurrentVersion")

@app.route("/api/TryDistributeCurrencyV2", methods=["POST", "GET"])
def try_distribute_currency_v2():
    return return_function_json(request.get_json(), "TryDistributeCurrency")

@app.route("/api/BroadCastMyRoomV2", methods=["POST", "GET"])
def broadcast_my_room_v2():
    return return_function_json(request.get_json(), "BroadCastMyRoom", request.get_json()["FunctionParameter"])

@app.route("/api/ShouldUserAutomutePlayer", methods=["POST", "GET"])
def should_user_automute_player():
    return jsonify(mute_cache)

@app.route("/api/AddOrRemoveDLCOwnershipV2", methods=["POST", "GET"])
def add_or_remove_dlc_ownership_v2():
    return return_function_json(request.get_json(), "AddOrRemoveDLCOwnership")

@app.route("/api/UpdatePersonalCosmeticsList", methods=["POST", "GET"])
def update_personal_cosmetics_list():
    return return_function_json(request.get_json(), "UpdatePersonalCosmeticsList")

@app.route("/api/UpdateUserCosmetics", methods=["POST", "GET"])
def update_user_cosmetics():
    return return_function_json(request.get_json(), "UpdateUserCosmetics")

@app.route("/api/UploadGorillanalytics", methods=["POST", "GET"])
def upload_gorilla_analytics():
    return return_function_json(request.get_json(), "UploadGorillanalytics")

@app.route("/api/Gorillanalytics", methods=["POST", "GET"])
def gorilla_analytics():
    return return_function_json(request.get_json(), "Gorillanalytics")

@app.route("/api/UpdatePersonalCosmetics", methods=["POST", "GET"])
def update_personal_cosmetics():
    return return_function_json(request.get_json(), "UpdatePersonalCosmetics")

@app.route("/api/ConsumeItem", methods=["POST", "GET"])
def consume_item():
    return return_function_json(request.get_json(), "ConsumeItem")

@app.route("/api/NewCosmeticsPath", methods=["POST", "GET"])
def new_cosmetics_path():
    return return_function_json(request.get_json(), "NewCosmeticsPath")

@app.route("/api/ReturnQueueStats", methods=["POST", "GET"])
def return_queue_stats():
    return return_function_json(request.get_json(), "ReturnQueueStats")

@app.route("/api/ConsumeCodeItem", methods=["POST", "GET"])
def consume_code_item():
    return return_function_json(request.get_json(), "ConsumeCodeItem")

@app.route("/api/CosmeticsAuthenticationV2", methods=["POST", "GET"])
def cosmetic_auth():
    return return_function_json(request.get_json(), "CosmeticsAuthentication")

@app.route("/api/KIDIntegrationV1", methods=["POST", "GET"])
def kid_integration():
    return return_function_json(request.get_json(), "KIDIntegration")

@app.route('/api/v2/GetName', methods=['POST', 'GET'])
def GetNameIg():
    return jsonify({"result": f"GORILLA{random.randint(1000,9999)}"})
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)