from django.urls import path
from . import views

urlpatterns = [
    path("", views.text_signup_index, name="text_signup_index"),
    path("optout", views.opt_out_index, name="opt_out_index")
]