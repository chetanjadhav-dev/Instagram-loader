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
        
        if post.typename == 'GraphImage':
            # Handle single image post
            img = download_image(post.url)
            img_io = BytesIO()
            img.save(img_io, format=img.format)
            img_file = ContentFile(img_io.getvalue(), f"{username}_{i}.{img.format.lower()}")

            InstagramPost.objects.create(
                profile=profile_obj,
                media_type='image',
                image=img_file,
                caption=post.caption
            )

        elif post.typename == 'GraphVideo':
            # Handle video post
            video_response = requests.get(post.video_url)
            if video_response.status_code == 200:
                video_file = ContentFile(video_response.content, f"{username}_{i}.mp4")

                InstagramPost.objects.create(
                    profile=profile_obj,
                    media_type='video',
                    video=video_file,
                    caption=post.caption
                )
        
        elif post.typename == 'GraphSidecar':
            # Handle carousel post
            for j, sidecar in enumerate(post.get_sidecar_nodes()):
                if sidecar.is_video:
                    media_response = requests.get(sidecar.video_url)
                    media_type = 'video'
                    ext = 'mp4'
                else:
                    media_response = requests.get(sidecar.display_url)
                    media_type = 'image'
                    ext = 'jpg'
                
                if media_response.status_code == 200:
                    media_file = ContentFile(media_response.content, f"{username}_{i}_carousel_{j}.{ext}")

                    InstagramPost.objects.create(
                        profile=profile_obj,
                        media_type=media_type,
                        image=media_file if media_type == 'image' else None,
                        video=media_file if media_type == 'video' else None,
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
