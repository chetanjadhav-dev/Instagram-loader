from django.db import models
from django.core.files import File
from io import BytesIO
from PIL import Image
import requests
import os

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/instagram_images/<username>/<filename>
    return f'instagram_images/{instance.profile.username}/{filename}'

class InstagramProfile(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    post_count = models.IntegerField()

    def __str__(self):
        return self.username

class InstagramPost(models.Model):
    profile = models.ForeignKey(InstagramProfile, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to=user_directory_path)
    caption = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.profile.username} - {self.caption[:30]}..."
