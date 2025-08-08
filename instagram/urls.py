from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('save/<str:username>/', views.save_instagram_posts, name='save_instagram_posts'),
    path('fetch/<str:username>/<int:post_count>/', views.fetch_instagram_posts, name='fetch_instagram_posts'),
]
