import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    spotify_id = models.CharField(max_length=40, unique=True)
    image_url = models.URLField(max_length=360)
    user_uri = models.URLField(max_length=360)
    spotify_type = models.CharField(max_length=50)

    access_token = models.CharField(max_length=360)
    token_type = models.CharField(max_length=30)
    token_expiry_date = models.DateTimeField(null=True)
    refresh_token = models.CharField(max_length=360)
    token_scope = models.CharField(max_length=360)

    def update_token_data_from_json(self, data):
        self.access_token = data['access_token']
        self.token_type = data['token_type']
        self.token_expiry_date = timezone.now(
        ) + datetime.timedelta(seconds=data['expires_in'])
        if "refresh_token" in data.keys():
            self.refresh_token = data['refresh_token']
        self.token_scope = data['scope']
        self.save()
