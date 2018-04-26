from django.conf.urls import url
from .views import (
    BannerPreview,
    BannerDetailView,
    BannerNewEventsSelectedCreateView,
    BannerDeleteView,
    EditEventDesignView,
    LocalizationView,
    download_video,

)
from . import views


urlpatterns = [

    url(r'^select_event/$',
        BannerNewEventsSelectedCreateView.as_view(
            template_name='event_list.html',
        ),
        name='select_event',),
    url(r'^new/$',
        LocalizationView.as_view(
            template_name='select_localization.html'
        ),
        name='banner_new'),
    url(r'^(?P<pk>[0-9]+)/banner_detail/$',
        BannerDetailView.as_view(),
        name='banner_detail',),
    url(r'^(?P<pk>[0-9]+)/preview/$',
        BannerPreview.as_view(),
        name='preview',),
    url(r'^(?P<pk>[0-9]+)/banner_delete/$',
        BannerDeleteView.as_view(),
        name='banner_delete',),
    url(r'^(?P<pk>[0-9]+)/banner_update/$',
        BannerNewEventsSelectedCreateView.as_view(
            template_name='event_list.html'
        ),
        name='banner_update'
        ),
    url(r'^(?P<pk>[0-9]+)/event/(?P<epk>[0-9]+)/$',
        EditEventDesignView.as_view(),
        name='edit_design'),
    url(r'^download/$', views.video, name='download'),

]
