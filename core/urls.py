from django.urls import path
from .views import index, openai_index, login_view, signup_view, logout_view

urlpatterns = [
    path('', openai_index, name="openai_index"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('talivy/', index, name='index'),
]
