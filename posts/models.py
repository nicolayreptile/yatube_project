from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_author")
    group = models.ForeignKey(Group, related_name="post_group", on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    def __str__(self):
        return self.text

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1023)
    created = models.DateTimeField("date created", auto_now_add=True)

    def __str__(self):
        return self.text

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    