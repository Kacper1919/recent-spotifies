from multipledispatch import dispatch

from django.db import models
from recent_spotifies.settings import STATIC_URL

from authentication.models import User
import parsers

# Create your models here.

class Artist(models.Model):
    spotify_id = models.CharField(max_length=30, primary_key=True, unique= True)
    name = models.CharField(max_length=360)

    image_url = models.URLField(max_length=360, null=True)
    popularity = models.IntegerField(null=True)
    followers = models.IntegerField(null=True)

    temporary_genres_to_save = []

    @classmethod
    def from_json(cls, artist_data):
        artist = cls(spotify_id = artist_data['id'], name = artist_data['name'])
        artist.image_url = parsers.image_url(artist_data)

        try:
            artist.popularity = int(artist_data['popularity'])
            artist.followers = int(artist_data['followers']['total'])
        except KeyError: pass

        try:
            for genre_name in artist_data['genres']:
                try: ArtistGenre.objects.get(artist=artist, genre=genre_name)
                except ArtistGenre.DoesNotExist:
                    genre = ArtistGenre(artist=artist, genre=genre_name)
                    artist.temporary_genres_to_save.append(genre)
        except KeyError:
            pass

        return artist


    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None,):
        super(Artist, self).save(*args, force_insert, force_update, using, update_fields)

        [genre.save() for genre in self.temporary_genres_to_save]
        self.temporary_genres_to_save = None
    
    def __str__(self):
        return self.name

class ArtistGenre(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    genre = models.CharField(max_length=60)

    class Meta:
        unique_together = ('artist', 'genre',)

    def __str__(self):
        return self.artist.name + " - " + self.genre


class Track(models.Model):
    spotify_id = models.CharField(max_length=30, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    artist_names = models.CharField(max_length=360)
    duration_ms = models.IntegerField()
    popularity = models.IntegerField()
    release_date = models.DateField()
    image_url = models.URLField(null = True)

    acousticness = models.FloatField(null=True)
    danceability = models.FloatField(null=True)
    energy = models.FloatField(null=True)
    instrumentalness = models.FloatField(null=True)
    key = models.IntegerField(null=True)
    liveness = models.FloatField(null=True)
    loudness = models.FloatField(null=True)
    mode = models.IntegerField(null=True)
    speechiness = models.FloatField(null=True)
    tempo = models.FloatField(null=True)
    time_signature = models.IntegerField(null=True)
    valence = models.FloatField(null=True)
    analysis_uri = models.URLField(max_length=360, null=True)

    temporary_track_artists_to_save = []

    @classmethod
    def from_json(cls, track_data):
        _arrtist_names = parsers.artist_names(track_data['artists'])
        _release_date = parsers.release_date(track_data['album']['release_date'])

        track = cls(
            spotify_id=track_data['id'],
            name=track_data['name'],
            artist_names=_arrtist_names,
            duration_ms=track_data['duration_ms'],
            popularity=track_data['popularity'],
            release_date=_release_date,
        )

        track.image_url = parsers.image_url(track_data['album'])

        for artist_data in track_data['artists']:
            try:
                artist = Artist.objects.get(pk=artist_data['id'])
            except Artist.DoesNotExist:
                artist = Artist.from_json(artist_data)
            track_artist = TrackArtist(track=track, artist=artist)

            if track_artist is not None:
                track.temporary_track_artists_to_save.append(track_artist)

        return track
    
    def update_audio_features_from_json(self, data):
        self.acousticness = data['acousticness']
        self.danceability = data['danceability']
        self.energy = ['energy']
        self.instrumentalness = data['instrumentalness']
        self.key = data['key']
        self.liveness = data['liveness']
        self.loudness = data['loudness']
        self.mode = data['mode']
        self.speechiness = data['speechiness']
        self.tempo = data['tempo']
        self.time_signature = data['time_signature']
        self.valence = data['valence']
        self.analysis_uri = data['analysis_uri']
        self.save()
    
    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None,):
        super(Track, self).save(*args, force_insert, force_update, using, update_fields)
        [track_artist.save() for track_artist in self.temporary_track_artists_to_save]
    
    def __str__(self):
        return self.name
    
    def get_genres(self):
        genres = []
        for track_artist in self.trackartist_set.all():
            for genre in track_artist.artist.artistgenre_set.all():
                genres.append(genre.genre)

        return tuple(genres)

class TrackArtist(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('track', 'artist',)

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None,):
        try:
            Artist.objects.get(pk=self.artist.pk)
        except Artist.DoesNotExist:
            self.artist.save()

        if not TrackArtist.objects.filter(artist=self.artist, track=self.track).exists():
            super(TrackArtist, self).save(*args, force_insert, force_update, using, update_fields)
        else:
            pass
            #raise Exception("Cannot save duplicate artist for the same track")

    def __str__(self):
        return self.track.name + " - " + self.artist.name


class Playlist(models.Model):
    spotify_id = models.CharField(max_length=30, primary_key=True, unique=True)
    type = models.CharField(max_length=15)
    name = models.CharField(max_length=360)
    owner_id = models.CharField(max_length=30)
    owner_name = models.CharField(max_length=30)
    added_at = models.DateTimeField(null=True)
    image_url = models.URLField(max_length=360, null=True)

    @classmethod
    @dispatch(object, dict)
    def from_json(cls, data: dict, type='playlist'):
        if type != 'playlist': raise Exception
        if not all(x in data.keys() for x in ['id', 'name']): raise ValueError

        image_url = parsers.image_url(data)
            
        playlist = cls(
            spotify_id = data['id'],
            type = type,
            name = data['name'],
            owner_id = data['owner']['id'],
            owner_name = data['owner']['display_name'],
            image_url = image_url,
        )
        return playlist

    @classmethod
    @dispatch(object, object, str)
    def from_json(cls, user: User, type: str):
        if type == 'favourites':
            id = parsers.get_user_favourite_pl_id(user.spotify_id)
            name = "Favourites"
            image_url = STATIC_URL + 'images/liked-songs-300.jpg'
        elif type == 'recently_played':
            id = parsers.get_user_recently_played_pl_id(user.spotify_id)
            name=  "Recently Played"
            image_url = STATIC_URL + 'images/recently-played-300.jpg'
        else:
            raise ValueError
        print(image_url)        

        playlist = cls(
            spotify_id = id,
            type = type,
            name = name,
            owner_id = user.spotify_id,
            owner_name = user.username,
            image_url = image_url,
        )
        return playlist
    
    def __str__(self):
        return self.name
    
class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    added_played_at = models.DateTimeField()

    class Meta:
        unique_together = ('playlist', 'track', 'added_played_at',)

    @classmethod
    def from_json(cls, playlist, playlist_track_data):
        if playlist_track_data['track']['is_local']: raise ValueError

        id = playlist_track_data['track']['id']
        added_played_at = parsers.added_played_at(playlist_track_data)
        try:
            track = Track.objects.get(pk=id)
        except Track.DoesNotExist:
            track = Track.from_json(playlist_track_data['track'])

        playlist_track = cls(
            playlist = playlist,
            track = track,
            added_played_at = added_played_at,
        )
        return playlist_track
    
    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        try: Track.objects.get(pk=self.track.pk)
        except Track.DoesNotExist: self.track.save()
        super().save(*args, force_insert, force_update, using, update_fields)
    
class TopArtist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    time_range = models.CharField(max_length=11)

    class Meta:
        unique_together = ('user', 'artist', 'time_range',)

    @classmethod
    def from_json(cls, user, top_artist_data, time_range):
        if top_artist_data['type'] != 'artist': raise Exception
        artist = Artist.from_json(top_artist_data)

        top_artist = cls(
            user=user,
            artist=artist,
            time_range=time_range,
        )

        return top_artist

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            if len(self.artist.temporary_genres_to_save) > Artist.objects.get(pk=self.artist.pk).artistgenre_set.count():
                self.artist.save()
        except Artist.DoesNotExist: self.artist.save()
        super().save(force_insert, force_update, using, update_fields)

class TopTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    time_range = models.CharField(max_length=11)

    class Meta:
        unique_together = ('user', 'track', 'time_range',)

    @classmethod
    def from_json(cls, user, top_track, time_range):
        if top_track['type'] != 'track': raise Exception
        try: track = Track.objects.get(pk=top_track['id'])
        except Track.DoesNotExist:
            track = Track.from_json(top_track)

        top_track = cls(
            user=user,
            track=track,
            time_range=time_range,
        )

        return top_track

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        try: Track.objects.get(pk=self.track.pk)
        except Track.DoesNotExist: self.track.save()
        super().save(force_insert, force_update, using, update_fields)

