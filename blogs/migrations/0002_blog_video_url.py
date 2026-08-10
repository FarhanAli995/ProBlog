# Generated migration for adding video_url field to Blog model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0002_blogmedia'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='video_url',
            field=models.URLField(blank=True, null=True, help_text='URL to video file (MP4, WebM, or embedded video URL)'),
        ),
    ]
