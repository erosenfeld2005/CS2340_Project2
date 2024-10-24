#from django.shortcuts import render
import base64
from requests import post, get
import json


# Create your views here.
client_id = 'defb4c242b7247529ae6409bc5ab3a7f'
client_secret = 'f32301833f4a4f85b2cf4caed8bd4f7d'

def get_token():
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token):
    return {'Authorization': 'Bearer ' + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    return json_result[0]

token = get_token()

result = search_for_artist(token, "Taylor")
print(result["name"])



