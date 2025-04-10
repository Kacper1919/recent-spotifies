# Generated by Django 5.1.7 on 2025-04-06 12:24

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0006_alter_artistgenre_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='playlisttrack',
            unique_together={('playlist', 'track', 'added_played_at')},
        ),
        migrations.AlterUniqueTogether(
            name='topartist',
            unique_together={('user', 'artist', 'time_range')},
        ),
        migrations.AlterUniqueTogether(
            name='toptrack',
            unique_together={('user', 'track', 'time_range')},
        ),
        migrations.AlterUniqueTogether(
            name='trackartist',
            unique_together={('track', 'artist')},
        ),
    ]
