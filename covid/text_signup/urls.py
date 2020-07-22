from django.urls import path
from . import views

urlpatterns = [
    path("", views.text_signup_index, name="text_signup_index"),
]