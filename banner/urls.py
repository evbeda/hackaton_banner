from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from .views import EventsView


urlpatterns = [
    url(r'^accounts/profile/$', EventsView.profile, name='profile'),
]
