from django.db import models
from django.core.files import File
from io import BytesIO
from PIL import Image
import requests
import os

def user_directory_path(instance, filename):
    # Determine the folder based on the media type
    media_type_folder = 'images'  # Default folder is for images
    if instance.media_type == 'video':
        media_type_folder = 'videos'
    elif instance.media_type == 'carousel':
        media_type_folder = 'carousels'
    
    # File will be uploaded to MEDIA_ROOT/instagram_images/<username>/<media_type>/<filename>
    return f'instagram_images/{instance.profile.username}/{media_type_folder}/{filename}'

class InstagramProfile(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    post_count = models.IntegerField()

    def __str__(self):
        return self.username

class InstagramPost(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('carousel', 'Carousel'),
    ]

    profile = models.ForeignKey(InstagramProfile, on_delete=models.CASCADE, related_name='posts')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    video = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.profile.username} - {self.caption[:30]}..."
