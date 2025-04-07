from base64 import b64encode
import datetime
import os
import requests
import secrets

from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import User

SPOTIFY_API_TOKEN_SCOPES = "playlist-read-private user-library-read playlist-modify-public user-read-recently-played user-top-read"
SPOTIFY_OAUTH_REDIRECT_URI = "http://127.0.0.1:8000/oauth-callback"

SPOTIFY_API_CLIENT_ID = os.environ.get('SPOTIFY_API_CLIENT_ID')
SPOTIFY_API_CLIENT_SECRET = os.environ.get('SPOTIFY_API_CLIENT_SECRET')

class IndexView(generic.TemplateView):
    template_name='index.html'

def login_with_spotify(request):

    state = secrets.token_urlsafe(16)
    request.session['state'] = state

    return HttpResponseRedirect(
        'https://accounts.spotify.com/authorize?' +
        'response_type=' + 'code'
        '&client_id=' + SPOTIFY_API_CLIENT_ID +
        '&scope='+SPOTIFY_API_TOKEN_SCOPES +
        '&redirect_uri='+SPOTIFY_OAUTH_REDIRECT_URI +
        '&state='+state
    )

def oauth_callback(request):
    full_path = request.get_full_path()
    query_string = full_path.split('?')[1].split('#')[0]
    pairs = [x.split('=') for x in query_string.split('&')]
    parsed_result = {}
    for pair in pairs:
        key = pair[0]
        value = pair[1]
        if key in parsed_result:
            parsed_result[key].append(value)
        else:
            parsed_result[key] = value

    try:
        code = parsed_result['code']
        state = parsed_result['state']
    except KeyError:
        return Http404("Failed To Login With Spotify")

    TOKEN_URI = "https://accounts.spotify.com/api/token"

    auth_str = get_encoded_client_id_client_secret()

    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': auth_str
    }
    body = {
        'code': code,
        'redirect_uri': SPOTIFY_OAUTH_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    token_response = requests.post(
        TOKEN_URI, headers=headers, data=body, json=True)

    token = token_response.json()
    access_token = token['access_token']
    token_expiry_date = timezone.now(
    ) + datetime.timedelta(seconds=int(token['expires_in']))

    user_profile_response = requests.get(
        'https://api.spotify.com/v1/me', headers={'Authorization': 'Bearer %s' % access_token})
    user_profile = user_profile_response.json()
    spotify_id = user_profile['id']

    try:
        user = User.objects.get(spotify_id=spotify_id)
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=user_profile['display_name'],
            spotify_id=spotify_id,
            image_url=user_profile['images'][1]['url'],
            user_uri=user_profile["href"],
            spotify_type=user_profile['type'],
            access_token=token['access_token'],
            token_type=token['token_type'],
            token_expiry_date=token_expiry_date,
            refresh_token=token['refresh_token'],
            token_scope=token['scope']
            )

    login(request, user)

    return HttpResponseRedirect(reverse('index'))


def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))









def get_encoded_client_id_client_secret() -> str:
    """"
    returns b64 encoded string "client_id:client_scret"
    """
    id_secret_str = SPOTIFY_API_CLIENT_ID + ':' + SPOTIFY_API_CLIENT_SECRET
    id_secret_bytes = id_secret_str.encode('utf-8')
    encoded_id_secret_bytes = b64encode(id_secret_bytes)
    auth_str = 'Basic ' + encoded_id_secret_bytes.decode('utf-8')
    return auth_str

def load_refresh_token(user):
    if user.token_expiry_date < timezone.now() - datetime.timedelta(seconds=60):
        body = {
            "grant_type": "refresh_token",
            "refresh_token": user.refresh_token,
            "client_id": SPOTIFY_API_CLIENT_ID
        }
        auth_str = get_encoded_client_id_client_secret()
        headers = {
            "Contet-Type": "application/x-www-form-urlencoded",
            "Authorization": auth_str
        }
        response = requests.post("https://accounts.spotify.com/api/token", data=body, headers=headers)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        
        data = response.json()
        user.update_token_data_from_json(data)

        return user.access_token
    elif user.access_token == "":
        return None
    else:
        return user.access_token
    
def get_response_json(user, url):
    print(url)
    headers = {
        "Authorization": "Bearer " + load_refresh_token(user)
        }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()