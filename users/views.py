from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.mail import send_mail

from .forms import CreationForm

class SignUp(CreateView):
    form_class = CreationForm
    success_url = "/auth/login/"
    template_name = "signup.html"

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        username = form.cleaned_data["username"]
        send_confirmation_email(username, email="test@test.com",)
        return super().form_valid(form)


def send_confirmation_email(username, email):
    send_mail(
        "Подтверждение регистрации",
        f"Уважаемый {username}, для подтверждения регистрации пройдите по ссылке <будто бы ссылка>",
        "no-reply@yatube.ru",
        [email],
        fail_silently=False,
    )
