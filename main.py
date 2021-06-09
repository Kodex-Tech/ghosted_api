from flask import Flask,request,Response
import os
import pycountry
import logging
import requests
import json
from rich.logging import RichHandler
from datetime import datetime
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
app = Flask(__name__)
languages = {
    'da'    : 'Danish, Denmark',
    'de'    : 'German, Germany',
    'en-GB' : 'English, United Kingdom',
    'en-US' : 'English, United States',
    'es-ES' : 'Spanish, Spain',
    'fr'    : 'French, France',
    'hr'    : 'Croatian, Croatia',
    'lt'    : 'Lithuanian, Lithuania',
    'hu'    : 'Hungarian, Hungary',
    'nl'    : 'Dutch, Netherlands',
    'no'    : 'Norwegian, Norway',
    'pl'    : 'Polish, Poland',
    'pt-BR' : 'Portuguese, Brazilian, Brazil',
    'ro'    : 'Romanian, Romania',
    'fi'    : 'Finnish, Finland',
    'sv-SE' : 'Swedish, Sweden',
    'vi'    : 'Vietnamese, Vietnam',
    'tr'    : 'Turkish, Turkey',
    'cs'    : 'Czech, Czechia, Czech Republic',
    'el'    : 'Greek, Greece',
    'bg'    : 'Bulgarian, Bulgaria',
    'ru'    : 'Russian, Russia',
    'uk'    : 'Ukranian, Ukraine',
    'th'    : 'Thai, Thailand',
    'zh-CN' : 'Chinese, China',
    'ja'    : 'Japanese',
    'zh-TW' : 'Chinese, Taiwan',
    'ko'    : 'Korean, Korea'
}
cc_digits = {
    'american express': '3',
    'visa': '4',
    'mastercard': '5'
}
relation_types = {
    "1": "Friend",
    "2": "Blocked",
    "3": "Incoming Friend Request",
    "4": "Outgoing Friend Request"
}

@app.route("/", methods=['GET'])
def hello():
    return "GHOST API"

@app.route('/api/token',methods=['GET'])
def token():
    token = request.args.get('token')
    if token is None:
        response = Response()
        response.status_code = 401
        response.headers["Access-Control-Allow-Origin"]="*"
        return response
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    res = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers)
    if (res.status_code == 401):
        response = Response()
        response.status_code = 401
        response.headers["Access-Control-Allow-Origin"]="*"
        return response
    res_json = res.json()
    username = f'{res_json["username"]}#{res_json["discriminator"]}'
    id = res_json['id']
    avatar = f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.gif"
    phone = res_json['phone']
    email = res_json['email']
    mfa = res_json['mfa_enabled']
    created = datetime.utcfromtimestamp(
                ((int(res_json['id']) >> 22) + 1420070400000) / 1000).strftime(
                '%d-%m-%Y %H:%M:%S UTC')
    language = languages.get(res_json['locale'])

    res = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=headers)
    nitro_data = res.json()
    hasNitro = bool(len(nitro_data) > 0)
    if hasNitro:
        d1 = datetime.strptime(nitro_data[0]["current_period_end"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
        d2 = datetime.strptime(nitro_data[0]["current_period_start"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
        days_left = abs((d2 - d1).days)
    billing_info = []
    for x in requests.get('https://discordapp.com/api/v6/users/@me/billing/payment-sources',headers=headers).json():
        y = x['billing_address']
        name = y['name']
        address_1 = y['line_1']
        address_2 = y['line_2']
        city = y['city']
        postal_code = y['postal_code']
        state = y['state']
        country = y['country']
        if x['type'] == 1:
            cc_brand = x['brand']
            cc_first = cc_digits.get(cc_brand)
            cc_last = x['last_4']
            cc_month = str(x['expires_month'])
            cc_year = str(x['expires_year'])
            
            data = {
                        'Payment Type': 'Credit Card',
                        'Valid': not x['invalid'],
                        'CC Holder Name': name,
                        'CC Brand': cc_brand.title(),
                        'CC Number': ''.join(z if (i + 1) % 2 else z + ' ' for i, z in
                                             enumerate((cc_first if cc_first else '*') + ('*' * 11) + cc_last)),
                        'CC Exp. Date': ('0' + cc_month if len(cc_month) < 2 else cc_month) + '/' + cc_year[2:4],
                        'Address 1': address_1,
                        'Address 2': address_2 if address_2 else '',
                        'City': city,
                        'Postal Code': postal_code,
                        'State': state if state else '',
                        'Country': pycountry.countries.get(alpha_2=country).name,
                        'Default Payment Method': x['default']
                    }
            billing_info.append(data)
        elif x['type'] == 2:
            data = {
                'Payment Type': 'PayPal',
                'Valid': not x['invalid'],
                'PayPal Name': name,
                'PayPal Email': x['email'],
                'Address 1': address_1,
                'Address 2': address_2 if address_2 else '',
                'City': city,
                'Postal Code': postal_code,
                'State': state if state else '',
                'Country': pycountry.countries.get(alpha_2=country).name,
                'Default Payment Method': x['default']
                }
            billing_info.append(data)
    connections = []
    for z in requests.get('https://discordapp.com/api/v6/users/@me/connections',headers=headers).json():
        data = {
            "type": z['type'].lower(),
            "id": z['id'],
            "username": z['name'],
            "revoked": z['revoked'],
            "visible": z['visibility'],
            "friend_sync": z['friend_sync'],
            "show_activity": z['show_activity'],
            "verified": z['verified']
        }
        try:
            data['access_token'] = z['access_token']
        except:
            pass
        connections.append(data)
    boosted_servers = []
    boosts = {}
    userID = ''
    for a in requests.get('https://discordapp.com/api/v6/users/@me/guilds/premium/subscription-slots',
                                 headers=headers).json():
        if(a['premium_guild_subscription'] is not None):
            guild_id = a['premium_guild_subscription']['guild_id']
            userID = a['premium_guild_subscription']['user_id']
            try:
                boosts[guild_id] += 1
            except KeyError:
                boosts[guild_id] = 1
    
    for gID in boosts.keys():
        guild = requests.get("https://discordapp.com/api/v6/guilds/"+gID, headers=headers).json()
        name = guild['name']
        isOwner = False
        if(guild['owner_id'] == str(userID)):
            isOwner = True
        owner = requests.get(f"https://discordapp.com/api/v6/users/{guild['owner_id']}",headers=headers).json()
        data = {
            "guild_name": name,
            "boosts": boosts[gID],
            "guild_id": gID,
            "owner": f"{owner['username']}#{owner['discriminator']}",
            "owner_id": owner['id'],
            "is_owner": isOwner
        }
        boosted_servers.append(data)
    friends = []
    for b in requests.get('https://discord.com/api/v9/users/@me/relationships',headers=headers).json():
        data = {
            "id": b['id'],
            "type": b['type'],
            "status": relation_types[str(b['type'])],
            "nickname": b['nickname'],
            "username": b['user']['username']+"#"+b['user']['discriminator'],
            'avatar': f"https://cdn.discordapp.com/avatars/{b['id']}/{b['user']['avatar']}.gif",
        }
        friends.append(data)
    final_data = {
        "username": username,
        "id": id,
        "email": email,
        "phone": phone,
        "avatar": avatar,
        "mfa_authentication": mfa,
        "account_created": created,
        "language": language,
        "has_nitro": hasNitro,
        "days_left": days_left if hasNitro else 0,
        "billing_info": billing_info,
        "connections": connections,
        "premium_guilds": boosted_servers,
        "relationships": friends

    }
    response = Response()
    response.status_code = 200
    response.headers["Access-Control-Allow-Origin"]="*"
    response.set_data(json.dumps(final_data))
    return response
        

port = os.environ.get('PORT')
if port is None:
    port = 2500
app.run(port=port,host='0.0.0.0')