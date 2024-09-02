from django.urls import path
from . import views

urlpatterns = [
    path('save_posts/<str:username>/', views.save_instagram_posts, name='save_instagram_posts'),
    path('fetch_posts/<str:username>/<int:post_count>/', views.fetch_instagram_posts, name='fetch_instagram_posts'),
]
