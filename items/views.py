from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from authentication.models import User
from authentication.views import get_response_json
from . import database
from . import models
import parsers

# Create your views here.

class MyPlaylistsView(LoginRequiredMixin, generic.ListView):
    template_name="my-playlists.html"

    def get_queryset(self):
        try:
            models.Playlist.objects.get(pk=parsers.get_user_favourite_pl_id(self.request.user.spotify_id))
        except models.Playlist.DoesNotExist: 
            favourites = models.Playlist.from_json(self.request.user, 'favourites')
            favourites.save()

        try: models.Playlist.objects.get(pk=parsers.get_user_recently_played_pl_id(self.request.user.spotify_id))
        except models.Playlist.DoesNotExist:
            recently_played = models.Playlist.from_json(self.request.user, 'recently_played')
            recently_played.save()

        return database.get_save_my_playlists(self.request.user)
    
class PlaylistTracksView(generic.ListView):
    template_name = 'playlist.html'
    paginate_by = 100

    def get_queryset(self):
        return None
    
    def get_context_data(self, **kwargs):
        id = self.kwargs['playlist_id']
        playlist = get_object_or_404(models.Playlist, pk=id)

        if playlist.type in ['favourites', 'recently_played']:
            if playlist.owner_id != self.request.user.spotify_id:
                raise Http404('Forbidden for current user')
            
        if not playlist.playlisttrack_set.exists():
            database.update_playlist_tracks(self.request.user, playlist)
        object_list = playlist.playlisttrack_set.all().order_by('-added_played_at')

        context = super().get_context_data(**kwargs, object_list=object_list)
        context.update({'playlist': playlist})
        return context

def refresh_playlist_track_view(request, playlist_id):
    url = reverse('playlist', args=[playlist_id])
    if request.method == 'POST':
        playlist = get_object_or_404(models.Playlist, pk=playlist_id)
        database.update_playlist_tracks(request.user, playlist)
    else:
        pass

    return HttpResponseRedirect(url)

class MyTopItemsView(LoginRequiredMixin, generic.ListView):
    template_name="my-top-items.html"

    def get_queryset(self):
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        artists_time_range = self.request.GET.get('artists_time_range')
        if artists_time_range is None:
            artists_time_range = 'long_term'
        artists_time_range_text = {
            'short_term': '1 Month',
            'medium_term': '6 Months',
            'long_term': '12 Months',
        }[artists_time_range]

        tracks_time_range = self.request.GET.get('tracks_time_range')
        if tracks_time_range is None:
            tracks_time_range = 'long_term'
        tracks_time_range_text = {
            'short_term': '1 Month',
            'medium_term': '6 Months',
            'long_term': '12 Months',
        }[tracks_time_range]

        context.update({
            "artists_time_range_text": artists_time_range_text,
            "artists_time_range": artists_time_range,
            "tracks_time_range": tracks_time_range,
            "tracks_time_range_text": tracks_time_range_text,
        })

        if self.request.user.topartist_set.filter(time_range=artists_time_range).count() == 0:
            database.update_top_artists(self.request.user, artists_time_range)
        top_artists = self.request.user.topartist_set.filter(time_range=artists_time_range)[:99]
        database.update_artist_image_urls(self.request.user, top_artists)

        if self.request.user.toptrack_set.filter(time_range=tracks_time_range).count() == 0:
            database.update_top_tracks(self.request.user, tracks_time_range)
        top_tracks = self.request.user.toptrack_set.filter(time_range=tracks_time_range)[:99]

        genres = {}
        for top_track in top_tracks:
            for track_artist in top_track.track.trackartist_set.all():
                    for artist_genre in track_artist.artist.artistgenre_set.all():
                        if artist_genre.genre in genres.keys():
                            genres[artist_genre.genre] += 1
                        else:
                            genres[artist_genre.genre] = 1
        
        sorted_genres = {k: v for k, v in sorted(genres.items(), key=lambda item: item[1], reverse=True)}
        try:
            max_genre = list(sorted_genres.values())[0]
        except IndexError:
            max_genre = 0

        context.update({"topartist_list": top_artists, "toptrack_list": top_tracks, "genres": sorted_genres, "max_genre": max_genre})

        return context
    
class TrackDetailView(generic.DetailView):
    template_name = 'track-detail.html'

    def get_object(self):
        track = get_object_or_404(models.Track, pk=self.kwargs['track_id'])
        return track
    
class ArtistDetailView(generic.DeleteView):
    template_name = 'artist-detail.html'

    def get_object(self):
        artist = get_object_or_404(models.Artist, pk=self.kwargs['artist_id'])
        if artist.image_url is None:
            database.update_artist_image_urls(self.request.user, artist)
            artist = get_object_or_404(models.Artist, pk=self.kwargs['artist_id'])
                
        return artist