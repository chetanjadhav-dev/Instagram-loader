from django.shortcuts import render, get_object_or_404
from .models import InstagramProfile, InstagramPost
import instaloader
from io import BytesIO
from PIL import Image
import requests
from django.core.files.base import ContentFile

def home(request):
    return render(request, 'instagram/welcome.html')

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        return img
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")

def save_instagram_posts(request, username):
    L = instaloader.Instaloader()

    profile = instaloader.Profile.from_username(L.context, username)
    post_limit = min(1000, profile.mediacount)
    profile_obj, created = InstagramProfile.objects.get_or_create(
        username=profile.username,
        defaults={'post_count': post_limit}
    )

    if not created:
        profile_obj.post_count = post_limit
        profile_obj.save()

    for i, post in enumerate(profile.get_posts()):
        if i >= post_limit:
            break
        
        img = download_image(post.url)
        img_io = BytesIO()
        img.save(img_io, format=img.format)
        img_file = ContentFile(img_io.getvalue(), f"{username}_{i}.{img.format.lower()}")

        InstagramPost.objects.create(
            profile=profile_obj,
            image=img_file,
            caption=post.caption
        )

    return render(request, 'instagram/success.html', {'profile': profile_obj})

def fetch_instagram_posts(request, username, post_count):
    profile = get_object_or_404(InstagramProfile, username=username)

    posts = InstagramPost.objects.filter(profile=profile)[:post_count]

    return render(request, 'instagram/posts.html', {
        'profile': profile,
        'posts': posts
    })
