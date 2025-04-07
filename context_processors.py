from authentication.models import User
from items import models

def overwiev_data(request):
    return {
        'track_count': models.Track.objects.count(),
        'artist_count': models.Artist.objects.count(),
        'user_count': User.objects.count(),
    }