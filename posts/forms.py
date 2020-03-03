from django import forms
from .models import Post, Comment
from django.contrib.auth import get_user_model

class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ["group", "text", "image"]

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["text"]