from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm

@cache_page(20)
def index(request):
    post_list = (
        Post.objects.select_related("author")
        .select_related("group")    
        .order_by("-pub_date")
        .annotate(comment_count=Count("comments"))
     )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {'page': page, 'paginator': paginator, })

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = (
        Post.objects.select_related("author")
        .select_related("group")
        .filter(group=group)
        .order_by("-pub_date")
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group":group, 'page': page, "paginator": paginator})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = (
        Post.objects.select_related("author")
        .select_related("group")
        .filter(author=user)
        .order_by("-pub_date")
        .annotate(comment_count=Count("comments"))
    )
    if request.user.is_authenticated:
       following = Follow.objects.filter(user=request.user, author=User.objects.get(username=username)).all()
    else:
        following = False
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {"page": page, "paginator": paginator, "author": user, "following": following, })

def post(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=user)
    comment_form = CommentForm
    comments = post.comments.all()
    return render(request, "post.html", {"post": post, "author": user, "form": comment_form, "comments": comments, })

@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
        else:
            return render(request, "new_post.html", { "form": form, })
    else:
        form = PostForm()
    return render(request, "new_post.html", { "form": form, })

@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.is_authenticated and request.user == post.author:        
        if request.method == "POST":
            form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect("post", username=post.author.username, post_id=post.id)
        else:
            form = PostForm(instance=post)
        return render(request, "edit_post.html", {"form": form, "post": post, })
    else:
        return redirect("post", username=post.author, post_id=post.id)

@login_required
def delete_post(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        post.delete()
    return redirect("profile", username=username)

@login_required
def add_comment(request, username, post_id):
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        print(str(form.is_valid()))
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            post = get_object_or_404(Post, pk=post_id)
            comment.post = post
            comment.save()
        return redirect("post", username=post.author.username, post_id=post.id)

@login_required
def follow_index(request):
        follows = Follow.objects.select_related("author").filter(user=request.user)
        authors = [f.author for f in follows]
        post_list = Post.objects.select_related("author").filter(author__in=authors).order_by("-pub_date").all()
        paginator = Paginator(post_list, 10)
        page_number = request.GET.get("page")
        page = paginator.get_page(page_number)
        return render(request, "follow.html", {"page": page, "paginator": paginator, })

@login_required
def profile_follow(request, username):        
        author = get_object_or_404(User, username=username)
        if Follow.objects.select_related("author").filter(user=request.user, author=author).count() > 0:
            return redirect("profile", username=username)
        follow = Follow.objects.create(user=request.user, author=author)        
        follow.save()
        return redirect("profile", username=username)

@login_required
def profile_unfollow(request, username):
        author = get_object_or_404(User, username=username)
        follow = get_object_or_404(Follow, user=request.user, author=author)
        follow.delete()
        return redirect("profile", username=username)

def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path, }, status=404)

def server_error(request):
    return render(request, "misc/500.html", {"path": request.path, }, status=500)