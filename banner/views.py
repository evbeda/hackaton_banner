# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from .models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)
from eventbrite import Eventbrite


@method_decorator(login_required, name='dispatch')
class EventsView(TemplateView, LoginRequiredMixin):

    template_name = 'events.html'

    def get_context_data(self, **kwargs):
        context = super(EventsView, self).get_context_data(**kwargs)
        access_token = self.request.user.social_auth.all()[0].access_token
        eventbrite = Eventbrite(access_token)
        context['events'] = [
            event
            for event in eventbrite.get('/users/me/events/')['events']
        ]
        return context

    # def post(self, events):
    #     # even1 = Event(start="1994-10-10 11:11", end="1995-11-11 11:11", design=EventDesign(user=UserFactory()))
    #     # even2 = Event(start="1994-10-10 11:11", end="1995-11-11 11:11", design=EventDesign(user=UserFactory()))
    #     events = events
    #     # events.append(even1)
    #     # events.append(even2)
    #     if events:
    #         design = BannerDesign.objects.create(user=UserFactory())
    #         design.save()
    #         banner = Banner.objects.create(design=design, user=UserFactory())
    #         banner.title = 'New banner'
    #         banner.description = 'This is the new banner'
    #         banner.save()
    #         for event in events:
    #             edesign = EventDesign.objects.create(user=UserFactory())
    #             edesign.save()
    #             event.banner = banner
    #             event.design = edesign
    #             event.save()
    #             return banner
    #     return Banner()



@method_decorator(login_required, name='dispatch')
class BannerView(TemplateView, LoginRequiredMixin):

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        # self.banner_new()
        context = super(BannerView, self).get_context_data(**kwargs)
        context['banners'] = Banner.objects.all()
        return context


@method_decorator(login_required, name='dispatch')
class BannerDetailView(DetailView, LoginRequiredMixin):

    model = Banner

    def get_object(self):
        banner = Banner.objects.get(id=self.kwargs['pk'])
        return banner
