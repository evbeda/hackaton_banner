from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from .views import (
    BannerView,
    BannerDetailView,
    EventsView,
)


urlpatterns = [

    url(r'^new/$',
        EventsView.as_view(template_name='events.html'),
        name='banner_new',
        ),
    url(r'^$',
        BannerView.as_view(template_name='banners.html'),
        name='banners',
        ),
    url(r'^banner_detail/(?P<pk>[0-9]+)/$',
        BannerDetailView.as_view(),
        name='banner_detail',
        ),
]
