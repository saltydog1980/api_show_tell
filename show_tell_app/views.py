from django.shortcuts import render
import requests as HTTP_Client
import requests, json
from dotenv import load_dotenv 
import sys, logging, time
import os 
import pprint

pp = pprint.PrettyPrinter(indent=2, depth=3)
# Create your views here.
load_dotenv()

#function to obtain new OAuth 2.0 token from the authentication server
def get_new_token():
    
    auth_server_url = "https://api.gfycat.com/v1/oauth/token"
    client_id = os.environ['apikey']
    
    client_secret = os.environ['secretkey']

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    token_req_payload = f"{{'client_id': \"{client_id}\", 'client_secret': \"{client_secret}\", 'grant_type': 'client_credentials'}}"

    token_response = requests.post(auth_server_url, headers=headers, data=token_req_payload)

    if token_response.status_code !=200:
        print("failed to obtain token from OAuth 2.0 server", file=sys.stderr)
        sys.exit(1)
    print("successfuly obtained a new token")

    mytoken = token_response.json()

    token = mytoken['access_token']

    return token

def call_api(endpoint):
    #obtain a new token before calling the API for the first time
    token = get_new_token()
    while True:
        api_call_headers = {'Authorization': 'Bearer ' + token}
        api_call_response = requests.get(endpoint, headers=api_call_headers)

        if api_call_response.status_code == 401:
            token = get_new_token()
        else:
            json_response = api_call_response.json()
        return json_response

def index(request):
    
    giphy_tags = []

    test_api_url = "https://api.gfycat.com/v1/reactions/populated"

    json_response = call_api(test_api_url)

    giphy_types = json_response['tags']
            
    for type in giphy_types:
        giphy_tags.append(type['tag'])
            
    data = {'giphy_types': giphy_types, 'tags': giphy_tags}

    return render(request, 'pages/index.html', data)

def get_type(request, tag):
    type_list = []
    giphy_tags = []

    test_api_url = f"https://api.gfycat.com/v1/gfycats/trending?tagName={tag}"
    type_url = "https://api.gfycat.com/v1/reactions/populated"
    
    type_response = call_api(type_url)
    giphy_types = type_response['tags']        
    for type in giphy_types:
        giphy_tags.append(type['tag'])
    

    json_response = call_api(test_api_url)
    giphy_list = json_response['gfycats']
    for giphy in giphy_list:
        type_list.append(giphy['max5mbGif'])

    data = {'type_list': type_list, 'tags': giphy_tags}

    return render(request, 'pages/type.html', data)