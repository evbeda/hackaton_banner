from django.conf.urls import url
from .views import (
    BannerDesignView,
    BannerDetailView,
    BannerNewEventsSelectedCreateView,
    BannerDeleteView,
    # BannerUpdateView,
)


urlpatterns = [

    url(r'^new/$',
        BannerNewEventsSelectedCreateView.as_view(
            template_name='event_list.html'
        ),
        name='banner_new',
        ),
    url(r'^(?P<pk>[0-9]+)/banner_detail/$',
        BannerDetailView.as_view(),
        name='banner_detail',
        ),
    url(r'^(?P<pk>[0-9]+)/banner_design/$',
        BannerDesignView.as_view(),
        name='banner_design',
        ),
    url(r'^(?P<pk>[0-9]+)/banner_delete/$',
        BannerDeleteView.as_view(),
        name='banner_delete'
        ),
    url(r'^(?P<pk>[0-9]+)/banner_update/$',
        BannerNewEventsSelectedCreateView.as_view(
            template_name='event_list.html'
        ),
        name='banner_update'
        ),
]
