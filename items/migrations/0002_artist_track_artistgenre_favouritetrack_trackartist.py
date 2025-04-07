# Generated by Django 5.1.7 on 2025-04-05 00:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('spotify_id', models.CharField(max_length=30, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=360)),
                ('image_url', models.URLField(max_length=360, null=True)),
                ('popularity', models.IntegerField(null=True)),
                ('followers', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('spotify_id', models.CharField(max_length=30, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('artist_names', models.CharField(max_length=360)),
                ('duration_ms', models.IntegerField()),
                ('popularity', models.IntegerField()),
                ('release_date', models.DateField()),
                ('image_url', models.URLField(null=True)),
                ('acousticness', models.FloatField(null=True)),
                ('danceability', models.FloatField(null=True)),
                ('energy', models.FloatField(null=True)),
                ('instrumentalness', models.FloatField(null=True)),
                ('key', models.IntegerField(null=True)),
                ('liveness', models.FloatField(null=True)),
                ('loudness', models.FloatField(null=True)),
                ('mode', models.IntegerField(null=True)),
                ('speechiness', models.FloatField(null=True)),
                ('tempo', models.FloatField(null=True)),
                ('time_signature', models.IntegerField(null=True)),
                ('valence', models.FloatField(null=True)),
                ('analysis_uri', models.URLField(max_length=360, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ArtistGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.CharField(max_length=60)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='items.artist')),
            ],
        ),
        migrations.CreateModel(
            name='FavouriteTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='items.track')),
            ],
        ),
        migrations.CreateModel(
            name='TrackArtist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='items.artist')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='items.track')),
            ],
        ),
    ]
