import datetime
import requests

from django.utils import timezone

from authentication.models import User
from authentication.views import get_response_json
from . import models
import parsers

def get_save_my_playlists(user: User):
    """
    Returns list of playlist querry based on api request with user's token.
    """
    playlists = models.Playlist.objects.none()

    next_url = (
        'https://api.spotify.com/v1/me/playlists?' +
        '&limit=50' +
        '&offset=0'
    )
    while next_url is not None:
        data = get_response_json(user, next_url)
        next_url = data['next']

        for playlist_data in data['items']:
            try:
                playlist = models.Playlist.objects.get(pk=playlist_data['id'])
            except models.Playlist.DoesNotExist:
                playlist = models.Playlist.from_json(playlist_data, type='playlist')
                playlist.save()
                
            playlists |=  models.Playlist.objects.filter(pk=playlist.pk)

    return playlists

def update_playlist_tracks(user: User, playlist: models.Playlist, offset=0, calls_limit=2):
    if playlist.type == 'playlist':
        next_url = f'https://api.spotify.com/v1/playlists/{playlist.spotify_id}/tracks'
    elif playlist.type == 'favourites':
        next_url = 'https://api.spotify.com/v1/me/tracks'
    elif playlist.type == 'recently_played':
        next_url = 'https://api.spotify.com/v1/me/player/recently-played'
    else:
        raise ValueError('Not allowed playlist.type')
    
    next_url = (
        next_url + '?' +
        'limit=50' +
        '&offset=' + str(offset)
    )

    total = None
    while next_url is not None and calls_limit > 0:
        data = get_response_json(user, next_url)
        calls_limit -= 1
        next_url = data['next']
        try: total = data['total']
        except KeyError: total = None

        for playlist_track in data['items']:
            if playlist_track['track']  ['is_local']:
                continue

            potential_playlist_track = models.PlaylistTrack.from_json(playlist, playlist_track)
            try:
                playlist_track_same_tracks = playlist.playlisttrack_set.filter(track=potential_playlist_track.track)
                playlist_track_same_tracks.get(added_played_at=potential_playlist_track.added_played_at)
                next_url = None
            except models.PlaylistTrack.DoesNotExist:
                next_url = data['next']
                potential_playlist_track.save()
        

    if total is not None and playlist.playlisttrack_set.count() < total:
        update_playlist_tracks(user, playlist, playlist.playlisttrack_set.count() - 1, calls_limit)
    
def update_top_artists(user: models.User, time_range='medium_term', calls_limit=2):

    next_url = ('https://api.spotify.com/v1/me/top/artists?' + 
        'time_range=' + time_range + 
        '&limit=50' + 
        '&offset=0'
    )

    while next_url is not None and calls_limit > 0:
        data = get_response_json(user, next_url)
        calls_limit -= 1
        #Make sure to not send request to the same url two times.
        if next_url != data['next']:
            next_url = data['next']
        else:
            next_url = None
        
        for artist_data in data['items']:
            top_artist = models.TopArtist.from_json(user, artist_data, time_range)
            top_artist.save()
            top_artist.artist.update_genres_from_json(artist_data)

def update_artist_image_urls(user, some_artist_query):
    artist_to_get_ids = []

    try:
        iter(some_artist_query)
    except TypeError:
        some_artist_query = [some_artist_query]

    for some_artist in some_artist_query:
        if isinstance(some_artist, models.TopArtist):
            if some_artist.artist.image_url is None:
                artist_to_get_ids.append(some_artist.artist.spotify_id)
        elif isinstance(some_artist, models.Artist) :
            artist_to_get_ids.append(some_artist.spotify_id)
        else:
            raise ValueError(type(some_artist), 'Is not allowed object')

    max_len = 50
    chunks = [artist_to_get_ids[x:x+max_len] for x in range(0, len(artist_to_get_ids), max_len)]

    for chunk in chunks:
        ids_str = ','.join(chunk)
        url = 'https://api.spotify.com/v1/artists?' + 'ids=' + ids_str
        data = get_response_json(user, url)

        for artist_data in data['artists']:
            artist = models.Artist.objects.get(pk=artist_data['id'])
            artist.image_url = parsers.image_url(artist_data)
            artist.save()

def update_top_tracks(user: models.User, time_range='medium_term', calls_limit=2):
    #user.toptrack_set.all().delete()

    next_url = ('https://api.spotify.com/v1/me/top/tracks?' + 
        'time_range=' + time_range + 
        '&limit=50' + 
        '&offset=0'
    )

    while next_url is not None and calls_limit > 0:
        data = get_response_json(user, next_url)
        calls_limit -= 1
        if next_url != data['next']:
            next_url = data['next']
        else:
            next_url = None

        for track_data in data['items']:
            top_track = models.TopTrack.from_json(user, track_data, time_range)
            top_track.save()