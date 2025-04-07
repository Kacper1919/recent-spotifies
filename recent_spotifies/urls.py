"""
URL configuration for recent_spotifies project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from authentication import views as authviews
from items import views as itemviews

urlpatterns = [
    path('admin/', admin.site.urls),

    #authentication
    path('', authviews.IndexView.as_view(), name="index"),
    path('login-with-spotify/', authviews.login_with_spotify, name='login_with_spotify'),
    path('oauth-callback/', authviews.oauth_callback, name='oauth_callback'),
    path('log-out', authviews.log_out, name="log_out"),

    #items - basicaly every spotify item track, artist, playlist, top track, top artist etc.
    path('my-playlists/', itemviews.MyPlaylistsView.as_view(), name="my_playlists"),
    path('playlist/<str:playlist_id>', itemviews.PlaylistTracksView.as_view(), name='playlist'),
    path('playlist/<str:playlist_id>-fv', itemviews.PlaylistTracksView.as_view(), name='playlist_favourites'),
    path('playlist/<str:playlist_id>-rp', itemviews.PlaylistTracksView.as_view(), name='playlist_recently_played'),
    path('refresh-playlist/<str:playlist_id>', itemviews.refresh_playlist_track_view, name='refresh_playlist_tracks'),
    path("my-top-items/", itemviews.MyTopItemsView.as_view(), name="my_top_items"),
    path('track/<str:track_id>/', itemviews.TrackDetailView.as_view(), name="track_detail"),
    path('artist/<str:artist_id>', itemviews.ArtistDetailView.as_view(), name='artist_detail'),



]
