from re import I
from tokenize import generate_tokens
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from threading import Thread
import json
import os
import requests
import hashlib
import datetime
import random
import time

from werkzeug.datastructures import Headers

titleider = "8D608"

SecretKey = "N7XPOQJB8CPZB8U6Q7A1ZNGR1QQE41CAUXJGKC6Q4PIISC69EJ"

#😀
app_credentials_1 = 'OC|1296841200171257|afac58dab345e294f3339925c9d11277'

# 😝
app_credentials_2 = 'OC|1296841200171257|afac58dab345e294f3339925c9d11277'

# 😁
app_credentials_3 = 'OC|1296841200171257|afac58dab345e294f3339925c9d11277'

app = Flask(__name__, template_folder='template')
muteCache = dict = {}

request_count = 0
report_count = 0
last_request_time = time.time()

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000000 per day", "1000000 per hour"]
)

class UploadData:

    def __init__(self):
        self.version = ""
        self.upload_chance = 0.0
        self.map = ""
        self.mode = ""
        self.queue = ""
        self.player_count = 0
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.vel_z = 0.0
        self.cosmetics_owned = ""
        self.cosmetics_worn = ""


upload_data_instance = UploadData()

def bad_request(message):
    return jsonify({
    'ResultCode': 3,
    'Error': 'Bad Request',
    'Message': f'Bad-Request: {message}'
    })

def loadTitleDataFromFile():
    try:
        with open('titleData.json', 'r') as file:
            data = json.load(file)
            print(f"Successfully loaded title data: {data}")  # Additional log
            return data
    except FileNotFoundError:
        print("Error: titleData.json file not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from titleData.json: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error reading titleData.json: {e}")
        return {}


def saveTitleDataToFile(data):
    with open('titleData.json', 'w') as file:
        json.dump(data, file, indent=2)


def md5(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def returnmyfunction(data, funcname, funcparam={}):
    rjson = data["FunctionParameter"]

    userId: str = rjson.get("CallerEntityProfile").get("Lineage").get(
        "TitlePlayerAccountId")

    req = requests.post(
        url=f"https://{titleider}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": userId,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers={
            "Content-Type": "application/json",
            "X-SecretKey": SecretKey
        })

    if req.status_code == 200:
        return jsonify(
            req.json().get("data").get("FunctionResult")), req.status_code
    else:
        return jsonify({}), req.status_code


def send_to_discord(message):
    webhook_url = ''
    headers = {'Content-Type': 'application/json'}
    data = {
        'content': message,
    }
    requests.post(webhook_url, headers=headers, json=data)


@app.route('/')
def index():
        return ("YOUR HAWKTUAHEND IS RUNNING 😀")


@app.route('/api/TitleData', methods=['GET', 'POST'])
@limiter.limit("50 per minute")
def title_data():
    if request.method == 'GET':
        data = loadTitleDataFromFile()
        print('Title data fetched: ', data)
        return jsonify(data)
    elif request.method == 'POST':
        global titleData
        print(request.json)
        titleData = loadTitleDataFromFile()
        return jsonify(titleData)


# covid's nonce validation, prevents the usage of unauthorized apps
# unused as it always fails for some reason and i cant figure out why
def validate_nonce(user_id: str, nonce: str):
    url1 = f"https://graph.oculus.com/user_nonce_validate?nonce={nonce}&user_id={user_id}&access_token={app_credentials_1}"
    url2 = f"https://graph.oculus.com/user_nonce_validate?nonce={nonce}&user_id={user_id}&access_token={app_credentials_2}"
    url3 = f"https://graph.oculus.com/user_nonce_validate?nonce={nonce}&user_id={user_id}&access_token={app_credentials_3}"
    headers = {'Content-Type': 'application/json'}

    def get_valid(url1, url2, url3) -> bool:
        try:
            result1 = requests.post(url=url1, headers=headers)
            result2 = requests.post(url=url2, headers=headers)
            result3 = requests.post(url=url3, headers=headers)
            if result1.json().get['is_valid']:
                return (result1.json().get['is_valid'])
            elif result2.json().get['is_valid']:
                return (result2.json().get['is_valid'])
            elif result3.json().get['is_valid']:
                return (result3.json().get['is_valid'])
            else:
                print('Warning: is_valid not in data')
                return False
        except Exception as e:
            print(f'Error checking nonce validity: {e}')
            return False

    valid = get_valid(url1, url2, url3)

    if valid:
        return True
    else:
        print('Warning: Nonce validation failed')
        return False

@app.route("/api/leftpocketdogshit/londonparisamsterdamyeahimoverseas", methods=['POST'])
def photon_api():
    # ticket, nonce, platform, appid, token, appversion, extract userid from ticket

    if request.get_json().get("Ticket") is None:
        return jsonify({
            "Message":"Missing CustomId parameter",
            "Error":"BadRequest-NoCustomId"
            }),400
    if request.get_json().get("Nonce") is None:
        return jsonify({
            "Message":"Missing Nonce parameter",
            "Error":"BadRequest-NoNonce"
            }),400
    if request.get_json().get("Platform") is None:
        return jsonify({
            "Message":"Missing Platform parameter",
            "Error":"BadRequest-NoPlatform"
            }),400
    if request.get_json().get("AppId") is None:
        return jsonify({
            "Message":"Missing AppId parameter",
            "Error":"BadRequest-NoAppId"
            }),400
    if request.get_json().get("AppVersion") is None:
        return jsonify({
            "Message":"Missing AppVersion parameter",
            "Error":"BadRequest-NoAppVersion"
            }),400


    if request.get_json().get("AppId") != titleider:
        return jsonify({
            "Message":"Request sent for the wrong App ID",
            "Error":"BadRequest-AppIdMismatch"
            }),400
    if request.get_json().get("Platform") != 'Quest':
        return jsonify({
            "Message":"Bad request",
            "Error":"BadRequest-WrongPlatform"
            }),400


    return jsonify({
        'Ticket': request.get_json().get("Ticket"),
        'Nonce': request.get_json().get("Nonce"),
        'Platform': request.get_json().get("Platform"),
        'AppId': request.get_json().get("AppId"),
        'AppVersion': request.get_json().get("AppVersion"),
        'UserId': request.get_json().get("Ticket").split("-")[0],
        'ResultCode': 1
        }), 200


@app.route("/api/photon/authenticate", methods=["POST", "GET"])
def photonauthenticate():
    if request.method.upper() == "GET":
        userId = request.args.get("username")
        token = request.args.get("token")

        response = requests.post(
            url=f"https://8D608.playfabapi.com/Server/GetUserData",
            json={"PlayFabId": userId},
            headers={
                "X-SecretKey":
                "N7XPOQJB8CPZB8U6Q7A1ZNGR1QQE41CAUXJGKC6Q4PIISC69EJ",
                "Content-Type": "application/json"
            })

        accountinfo = requests.post(
            url=f"https://8D608.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": userId},
            headers={
                "X-SecretKey":
                "N7XPOQJB8CPZB8U6Q7A1ZNGR1QQE41CAUXJGKC6Q4PIISC69EJ",
                "Content-Type": "application/json"
            })

        print(f"userId: {userId}, token: {token}")

        if response.status_code == 200:
            response_data = response.json().get("data", {}).get("Data", {})

            accinfo = accountinfo.json().get("data", {}).get("UserInfo", {})

            CustomId = accinfo.get("CustomIdInfo", {}).get("CustomId")
            print(CustomId)

            scoped = CustomId.split("OCULUS")[1]
            print(scoped)

            oculusauth = f"https://graph.oculus.com/{scoped}?access_token=N7XPOQJB8CPZB8U6Q7A1ZNGR1QQE41CAUXJGKC6Q4PIISC69EJ"
            headers = {"Content-Type": "application/json"}

            responseoculus = requests.get(oculusauth, headers=headers)

            print(responseoculus.json())

            if "ISPC" in response_data:
                send_to_discord(f"{userId} is on PC")
                return jsonify({
                    'resultCode': 3,
                    'message': 'Failed to parse token from request',
                    'userId': None,
                    'nickname': None
                })

            if "error" in responseoculus.json():
                send_to_discord(f"{userId} has invalid oculusid")
                return jsonify({
                    'resultCode': 3,
                    'message': 'Failed to parse token from request',
                    'userId': None,
                    'nickname': None
                })

            if "Device" not in response_data:
                send_to_discord(f"{userId} has no device info")
                return jsonify({
                    'resultCode': 3,
                    'message': 'Failed to parse token from request',
                    'userId': None,
                    'nickname': None
                })

            print(f"Authed {userId}")

            return jsonify({
                'resultCode': 1,
                'message': f'Authenticated user {userId.lower()} title 8D608',
                'userId': userId.upper(),
            })
        else:
            if userId is None or len(userId) != 16:
                print("incorrect userid")
                return jsonify({
                    'resultCode': 2,
                    'message': 'Invalid token',
                    'userId': None,
                    'nickname': None
                })
            elif token is None:
                print("incorrect token")
                return jsonify({
                    'resultCode': 3,
                    'message': 'Failed to parse token from request',
                    'userId': None,
                    'nickname': None
                })
            else:
                print("unknown error")
                return jsonify({
                    'resultCode': 0,
                    'message': "Something went wrong",
                    'userId': None,
                    'nickname': None
                })
    else:
        print("invalid method")


@app.route('/api/PlayFabAuthentication', methods=['POST'])
@limiter.limit("30 per minute")
def playfabauth():
    # customid, appid, nonce, oculusid, platform
    print("Received data at /api/playfabauthenticate:", data)

    if request.get_json().get("CustomId") is None:
        return jsonify({
            "Message":"Missing CustomId parameter",
            "Error":"BadRequest-NoCustomId"
            }),400
    if request.get_json().get("AppId") is None:
        return jsonify({
            "Message":"Missing AppId parameter",
            "Error":"BadRequest-NoAppId"
            }),400
    if request.get_json().get("Nonce") is None:
        return jsonify({
            "Message":"Missing Nonce parameter",
            "Error":"BadRequest-NoNonce"
            }),400
    if request.get_json().get("OculusId") is None:
        return jsonify({
            "Message":"Missing OculusId parameter",
            "Error":"BadRequest-NoOculusId"
            }),400
    if request.get_json().get("Platform") is None:
        return jsonify({
            "Message":"Missing Platform parameter",
            "Error":"BadRequest-NoPlatform"
            }),400


    if request.get_json().get("AppId") != titleider:
        return jsonify({
            "Message": "Bad Request",
            "Error": "BadRequest-AppIdMismatch"
            })
    if request.get_json().get("Platform") != 'Quest':
        return jsonify({
            "Message": "Bad Request",
            "Error": "BadRequest-Wrong Platform"
            })
    if not request.get_json().get("CustomId").startsWith("OC"):
        return jsonify({
            "Message": "Bad Request",
            "Error": "BadRequest-No OC Prefix"
            })
    if not validate_nonce(request.get_json().get("OculusId"), request.get_json().get("Nonce")):
        return jsonify({
            "Message": "Bad Request",
            "Error": "BadRequest-Invalid Nonce"
            })

    headers = {'Content-Type': 'application/json', 'X-SecretKey': SecretKey}

    login_endpoint = f"https://{titleider}.playfabapi.com/Server/LoginWithServerCustomId"
    login_payload = {
        'ServerCustomId': custom_id,
       'CreateAccount': True
       }
    login_response = requests.post(login_endpoint, headers=headers, json=login_payload)

    if login_response.status_code == 200:
        response_data = login_response.json()["data"]
        playfab_id = response_data['PlayFabId']
        session_ticket = response_data['SessionTicket']

        user_auth_headers = {
            'Content-Type': 'application/json',
            'X-Authorization': session_ticket
        }
        link_endpoint = f"https://{titleider}.playfabapi.com/Client/LinkCustomID"
        link_payload = {
            'CustomId': custom_id,
            'ForceLink': True
           }
        link_response = requests.post(link_endpoint, headers=user_auth_headers, json=link_payload)

        if link_response.status_code == 200:
            print("CustomID successfully linked to the PlayFab account.")
        else:
            print(
                f"Failed to link CustomID: {link_response.status_code} - {link_response.text}"
            )

        entityId = response_data['EntityToken']['Entity']['Id']
        entityType = response_data['EntityToken']['Entity']['Type']
        entityToken = response_data['EntityToken']['EntityToken']

        return jsonify({
            'SessionTicket': session_ticket,
            'PlayFabId': playfab_id,
            'EntityId': entityId,
            'EntityType': entityType,
            'EntityToken': entityToken
        }), 200

    elif login_response.status_code == 403:
        ban_info = login_response.json()
        if ban_info.get('errorCode') == 1002:
            ban_details = ban_info.get('errorDetails', {})
            ban_expiration_key = next(iter(ban_details.keys()), None)
            ban_expiration_list = ban_details.get(ban_expiration_key, [])
            ban_expiration = ban_expiration_list[0] if len(
                ban_expiration_list) > 0 else "No expiration date provided."
            print(ban_info)
            return jsonify({
                'BanMessage': ban_expiration_key,
                'BanExpirationTime': ban_expiration
            }), 403
        else:
            error_message = ban_info.get('errorMessage',
                                         'Forbidden without ban information.')
            return jsonify({
                'Error': 'PlayFab Error',
                'Message': error_message
            }), 403

    else:
        playfab_error = login_response.json().get("error", {})
        error_message = playfab_error.get("errorMessage", "Login failed")
        return jsonify({
            'Error': 'PlayFab Error',
            'Message': error_message,
            'PlayFabError': playfab_error
        }), login_response.status_code


@app.route('/api/CachePlayFabId', methods=['POST'])
@limiter.limit("30 per minute")
def cache_playfab_id():
    data = request.json
    send_to_discord(data)
    required_fields = ['Platform', 'SessionTicket', 'PlayFabId']
    if all([field in data for field in required_fields]):
        return jsonify({"Message": "PlayFabId Cached Successfully"}), 200
    else:
        missing_fields = [
            field for field in required_fields if field not in data
        ]
        return jsonify({
            "Error": "Missing Data",
            "MissingFields": missing_fields
        }), 400


if os.path.exists('data.json'):
    with open('data.json', 'r') as f:
        info = f.read()
        print(info)
        config = json.loads(info)
else:
    config = {}


def log_bad_name(name, id):

    if os.path.exists(f'Users/{id}.json'):
        with open(f'Users/{id}.json', 'r') as f:
            info = f.read()
            print(info)
            logs = json.loads(info)
    else:
        logs = {}

    if id in logs:
        if name in logs[id]:
            logs[id][name] += 1
        else:
            logs[id] = {name: 1}
    else:
        logs[id] = {name: 1}

    with open(f'Users/{id}.json', 'w') as temp_file:
        json.dump(logs, temp_file)
        temp_file.close()


@app.route('/api/send', methods=['POST', 'GET'])
@limiter.limit("30 per minute")
def checkforbadname():
    if request.method == 'POST':
        data = request.json

        name = data['FunctionArgument']['name']

        forRoom = data['FunctionArgument']['forRoom']

        with open('BanningWords.txt', 'r') as f:
            bad_words = f.read().splitlines()

        if any(word in name for word in bad_words):
            print("Data: ", data['CallerEntityProfile']['Entity']['Id'])

            if forRoom or not forRoom:
                return jsonify({
                    'ErrorCode': 3,
                    'Message': 'Bad Request',
                    'error': 'BadRequest-Name or Room is Bad',
                    'result': 2
                })
        else:
            return jsonify({'StatusCode': 200, 'Message': '', 'result': 0})

    else:
        return


def save_accepted_agreements(data):
    with open('accepted_agreements.json', 'w') as file:
        json.dump(data, file)


@app.route('/api/save', methods=['POST'])
@limiter.limit("30 per minute")
def save_legal_agreements():
    data = request.json
    function_argument = data['FunctionArgument']

    print(f'Recived argument: {function_argument}')

    return jsonify({"PrivacyPolicy": "2024.03.07", "TOS": "11.05.22.2"})


@app.route('/api/load', methods=['POST'])
@limiter.limit("30 per minute")
def load_legal_agreements():
    data = request.json
    function_argument = data['FunctionArgument']

    print(f'Recived argument: {data}')

    return jsonify({"PrivacyPolicy": "2024.03.07", "TOS": "11.05.22.2"})


@app.route('/api/get_data', methods=['GET'])
@limiter.limit("30 per minute")
def get_data():
    return jsonify(config)


def Send_PlayFab_Request(url: str, body, head):
    actual_url = f'https://{titleider}.playfabapi.com/{url}'
    response = requests.post(actual_url, json=body, headers=head)
    return response.json()


@app.route('/api/analytics', methods=['POST'])
@limiter.limit("30 per minute")
def temp():
    try:
        data = request.get_json()['FunctionArgument']

        upload_data_instance.version = data.get('version', "")
        upload_data_instance.upload_chance = data.get('upload_chance', 0.0)
        upload_data_instance.map = data.get('map', "")
        upload_data_instance.mode = data.get('mode', "")
        upload_data_instance.queue = data.get('queue', "")
        upload_data_instance.player_count = data.get('player_count', 0)
        upload_data_instance.pos_x = data.get('pos_x', 0.0)
        upload_data_instance.pos_y = data.get('pos_y', 0.0)
        upload_data_instance.pos_z = data.get('pos_z', 0.0)
        upload_data_instance.vel_x = data.get('vel_x', 0.0)
        upload_data_instance.vel_y = data.get('vel_y', 0.0)
        upload_data_instance.vel_z = data.get('vel_z', 0.0)
        upload_data_instance.cosmetics_owned = data.get('cosmetics_owned', "")
        upload_data_instance.cosmetics_worn = data.get('cosmetics_worn', "")

        print("Received data:", upload_data_instance.__dict__)

        send_to_discord(upload_data_instance.__dict__)

        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Error handling upload data: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/dlcownership', methods=['POST'])
@limiter.limit("30 per minute")
def aordlcownership():
    return jsonify({"result": True}), 200


@app.route('/api/getrandname', methods=["POST"])
@limiter.limit("30 per minute")
def GetRandomName():
    defaultname = "gorilla" + str(random.randint(1000, 9999))
    return jsonify({"result": defaultname})


@app.route('/api/ConsumeOculusIAP', methods=["POST"])
@limiter.limit("30 per minute")
def consumeoculusiap():
    data = request.json

    userId = data.get("userID")
    nonce = data.get("nonce")
    sku = data.get("sku")

    request1 = requests.post(
        url=
        f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={userId}&sku={sku}&access_token={app_credentials_1}",
        headers={"content-type": "application/json"})
    request2 = requests.post(
        url=
        f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={userId}&sku={sku}&access_token={app_credentials_2}",
        headers={"content-type": "application/json"})
    request3 = requests.post(
        url=
        f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={userId}&sku={sku}&access_token={app_credentials_3}",
        headers={"content-type": "application/json"})
    success1 = bool(request1.json().get("success"))
    success2 = bool(request2.json().get("success"))
    success3 = bool(request3.json().get("success"))

    if success1 or success2 or success3:
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})


@app.route('/api/returnmyoculushash', methods=["POST"])
@limiter.limit("30 per minute")
def returnmyoculushashv2():
    return returnmyfunction(request.get_json(), "ReturnMyOculusHash")


@app.route('/api/returncurrentversion', methods=["POST"])
@limiter.limit("30 per minute")
def returncurrentversionv2():
    return returnmyfunction(request.get_json(), "ReturnCurrentVersion")


@app.route('/api/trydistributecurrency', methods=["POST"])
@limiter.limit("30 per minute")
def trydistributecurrencyv2():
    return returnmyfunction(request.get_json(), "TryDistributeCurrency")


@app.route('/api/broadcastmyroom', methods=["POST"])
@limiter.limit("30 per minute")
def broadcastmyroomv2():
    return returnmyfunction(request.get_json(), "BroadcastMyRoom",
                            request.get_json()["FunctionParameter"])


@app.route('/api/ShouldUserAutomutePlayer', methods=["POST"])
@limiter.limit("50 per minute")
def shoulduserautomuteplayer():
    data = request.json()
    muteCache = data.get('muteCache')
    return jsonify(muteCache)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)