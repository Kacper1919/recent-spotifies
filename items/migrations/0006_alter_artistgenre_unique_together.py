# Generated by Django 5.1.7 on 2025-04-06 12:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0005_remove_recentlyplayedtrack_track_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='artistgenre',
            unique_together={('artist', 'genre')},
        ),
    ]
