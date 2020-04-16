from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_post, name="new_post"),
    path("group/<slug:slug>/", views.group_posts, name="group"),
    #Подписки
    path("follow/", views.follow_index, name="follow_index"),
    #Профайл пользователя
    path("<username>/", views.profile, name="profile"),
    #Пост пользователя
    path("<username>/<int:post_id>/", views.post, name="post"),
    path("<username>/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("<username>/<int:post_id>/comment/", views.add_comment, name="add_comment"),  
    path("<username>/<int:post_id>/delete/", views.delete_post, name="delete_post"),  
    #Подписаться или отписаться
    path("<username>/follow/", views.profile_follow, name="profile_follow"),
    path("<username>/unfollow/", views.profile_unfollow, name="profile_unfollow"),
]