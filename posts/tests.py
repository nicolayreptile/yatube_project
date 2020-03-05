from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Post, Group
from yatube.settings  import MEDIA_ROOT
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache

class EmailTest(TestCase):
    def setUp(self):
        self.c = Client()
        user = {
                'username': 'Alex',
                'password1': 'testpassword12345',
                'password2': 'testpassword12345',
                'email': 'test@yatube.com'
        }
        self.c.post("/auth/signup/", user, follow=True)
        self.response = self.c.get(f"/{ user['username'] }/")

    def test_send_mail(self):

        # Проверяем, что существует страница пользователя
        self.assertEqual(self.response.status_code, 200, msg="Page not found")       
        # Проверяем, что письмо лежит в исходящих
        self.assertEqual(len(mail.outbox), 1, msg="Mail not sent")
        # Проверяем, что тема первого письма правильная.
        self.assertEqual(mail.outbox[0].subject, "Подтверждение регистрации", msg="Mail subject is invalid")
    
    def test_profile(self):
        self.assertEqual(self.response.status_code, 200)


class TestPost(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = User.objects.create(username="user", password="test")
        self.new_post = Post.objects.create(text="Тестовый пост.", author=self.user)        

    def test_get_new_post_anonimous_user(self):
        # проверям get для неавторизованного пользоватлея        
        response = self.c.get("/new/", follow=True)
        #self.assertEqual(response.status_code, 302, msg=s"Redirect on get request for unauthorized user doesn't work\n")
        self.assertRedirects(response, "/auth/login/?next=/new/", msg_prefix="Redirect on get request for unauthorized user doesn't work\n")

    def test_create_new_post_anonimouse_user(self):
        # проверям post для неавторизованного пользоватлея 
        response = self.c.post("/new/", { "text": self.new_post.text, }, follow=True)
        self.assertRedirects(response, "/auth/login/?next=/new/", msg_prefix="Redirect on post request for unauthorized user doesn't work\n")

    def test_get_new_post_authorized_user(self):
        # проверяем get для авторизирвоанного пользователя
        self.c.force_login(self.user)
        response = self.c.get("/new/")
        self.assertEqual(response.status_code, 200, msg="New post page doesn't avaliable for authorized user")

    def test_create_new_post_authorized_user(self):   
        # проверяем post для авторизированного пользователя
        cache.clear()
        self.c.force_login(self.user)
        response = self.c.post("/new/", { "author": self.user, "text": self.new_post.text, }, follow=True)
        self.assertRedirects(response, "/", msg_prefix="Redirect after creation post doesn't work")
        # проверяем, что новая запись появилась
        self.assertContains(response, self.new_post.text, status_code=200, msg_prefix="Index page doesn't contain new post text")
        # проверяем, существует ли запись на странице автора
        response = self.c.get(f"/{self.user.username}/")
        self.assertContains(response, self.new_post.text, status_code=200, msg_prefix="Author page doesn't contain new post text")
        # проверяем, существует ли страница с записью
        response = self.c.get(f"/{self.user.username}/{self.new_post.id}/")
        self.assertContains(response, self.new_post.text, status_code=200, msg_prefix="Post page doen't exist")

class TestErrors(TestCase):
    def setUp(self):
        client = Client()
        self.response = client.get("nonexistent-address/")
    
    def test_404_page(self):
        self.assertEqual(self.response.status_code, 404, msg="Wrong status")
        self.assertTemplateUsed(self.response, template_name="misc/404.html")


         
class TestImage(TestCase):
    def setUp(self):
        self.client = Client()             
        user = User.objects.create(username="test", password="test")
        self.group = Group.objects.create(title="Test Group", slug="some-group", description="Something about group") 
        self.image = SimpleUploadedFile("test.jpg", content=open(MEDIA_ROOT+"\\test.jpg", "rb").read(), content_type="image/jpeg")            
        self.post = Post.objects.create(author=user, text="Interesting text", group=self.group)        
        self.client.force_login(user)   
        
    def test_image_upload(self):
        cache.clear()                
        response = self.client.post(reverse("post_edit", kwargs={"username": self.post.author.username, "post_id": self.post.id}), {"author": self.post.author, "text": "Updated text", "image": self.image, "group": self.group.id, }, follow=True)
        self.assertRedirects(response, reverse("post", kwargs={"username": self.post.author.username, "post_id": self.post.id}))         
        response = self.client.get(reverse("index"))
        self.assertContains(response,  "<img ", status_code=200, msg_prefix="Index page doesn't contain image")        
        response = self.client.get(reverse("profile", kwargs={"username": self.post.author.username}))
        self.assertContains(response, "<img ", status_code=200, msg_prefix="Profile page doesn't contain image")
        response = self.client.get(reverse("group", kwargs={"slug": self.post.group.slug }))
        self.assertContains(response, "<img ", status_code=200, msg_prefix="Group page doesn't contain image")

class TestComment(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create(username="author", password="password")
        self.commentator = User.objects.create(username="commentator", password="password")
        self.post = Post.objects.create(text="Long post text", author=self.author)
        self.comment = {"author": self.commentator, "post": self.post, "text": "Interesting comment"}        
    
    def test_anonimous_commentator(self):
        response = self.client.post(f"/{self.post.author.username}/{self.post.id}/comment/", self.comment, follow=True)
        self.assertRedirects(response, f"/auth/login/?next=/{self.post.author.username}/{self.post.id}/comment/", status_code=302)
    
    def test_authorized_commentator(self):
        self.client.force_login(self.commentator)
        response = self.client.post(f"/{self.post.author.username}/{self.post.id}/comment/", self.comment, follow=True)
        self.assertRedirects(response, f"/{self.post.author.username}/{self.post.id}/")
        response = self.client.get(f"/{self.post.author.username}/{self.post.id}/")
        self.assertContains(response, self.comment["text"])
        
class TestCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user("author")
        self.post = Post.objects.create(author=self.author, text="Interesting post")
        self.client.force_login(self.author)        

    def test_cache(self):
        index = reverse("index")
        response = self.client.get(index)
        self.assertContains(response, self.post.text)
        new_post = {"author": self.author, "text": "Second post"}
        self.client.post(reverse("new_post"), new_post, follow=True)
        response = self.client.get(index)
        self.assertNotContains(response, new_post["text"])
        cache.clear()
        response = self.client.get(index)
        self.assertContains(response, new_post["text"])


class TestFollow(TestCase):
    def setUp(self):
        self.client = Client()        
        self.author = User.objects.create(username="followingauthor", password="password")
        self.post = Post.objects.create(text="Тестовый пост", author=self.author)
        self.follower = User.objects.create(username="follower", password="password")
        self.not_follower = User.objects.create(username="notfollwer", password="password")

    def test_follow_anonimous(self):
        response = self.client.get(f"/{self.author.username}/follow/", follow=True)
        self.assertRedirects(response, f"/auth/login/?next=/{self.author.username}/follow/", status_code=302, msg_prefix="Anonimous user must not has possible to follow someone before login")

    def test_unfollow_anonimous(self):
        response = self.client.get(f"/{self.author.username}/unfollow/", follow=True)
        self.assertRedirects(response, f"/auth/login/?next=/{self.author.username}/unfollow/", status_code=302, msg_prefix="Anonimous user must not has possible to unfollow someone before login")

    def test_follow_authorized_user(self):
        self.client.force_login(user=self.follower)
        response = self.client.get(f"/{self.author.username}/follow/", follow=True)
        self.assertRedirects(response, f"/{self.author.username}/", status_code=302, )
        self.assertContains(response, "Отписаться")
        self.assertContains(response, f"Подписчиков: 1")
        response = self.client.get("/follow/")
        self.assertContains(response, self.post.text, msg_prefix="Follow page does not conatain following author post")
        new_post = Post.objects.create(text="Тестовый пост 2", author=self.author)
        response = self.client.get("/follow/")
        self.assertContains(response, new_post.text)
        self.client.force_login(self.not_follower)
        response = self.client.get("/follow/")
        self.assertNotContains(response, new_post.text, msg_prefix="User not follow this author")





