# -*- coding: utf-8 -*-
from datetime import datetime
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
from .forms import EventSelected
from .models import Event, Banner, EventDesign, BannerDesign
from django.views.generic.edit import FormView
from django.utils import timezone
from django.shortcuts import redirect



@method_decorator(login_required, name='dispatch')
class EventsView(FormView, LoginRequiredMixin):

    form_class = EventSelected
    template_name = "events/events.html"
    success_url = '../..'

    def __init__(self, *args, **kwargs):
        super(EventsView, self).__init__(*args, **kwargs)
        self.form_init = False

    def get_initial(self):
        access_token = self.request.user.social_auth.all()[0].access_token
        eventbrite = Eventbrite(access_token)
        self.events = eventbrite.get('/users/me/events/')['events']


    def get_form(self):
        form = super(EventsView, self).get_form()
        if not self.form_init:
            self.form_init = True
            for event in self.events:
                form.add_event(event)
        return form

    def form_valid(self, form, *args, **kwargs):
        if any(form.cleaned_data.values()):
            design = BannerDesign.objects.create(user=self.request.user)
            banner = Banner.objects.create(
                design=design,
                user=self.request.user,
            )
            banner.description = 'This is the new banner'
            banner.title = 'New banner'
            banner.save()
            for eventbrite_id, selected in form.cleaned_data.items():
                for event in self.events:
                    if event['id'] == eventbrite_id and form.cleaned_data[eventbrite_id]:
                        even1 = Event(start=timezone.now(), end=timezone.now())
                        # import ipdb; ipdb.set_trace()
                        edesign = EventDesign.objects.create(
                            user=self.request.user,
                        )
                        edesign.save()
                        even1.banner = banner
                        even1.design = edesign
                        even1.title = event['name']['text']
                        even1.description = event['description']['text']
                        even1.start = event['start']['local']
                        even1.end = event['end']['local']
                        even1.organizer = event['organizer_id']
                        even1.logo = event['logo']['url']
                        even1.custom_title = 'none'
                        even1.custom_logo = 'none'
                        even1.custom_description = 'none'
                        even1.save()
        return super(EventsView, self).form_valid(form, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class BannerView(TemplateView, LoginRequiredMixin):

    template_name = 'index.html'

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


@method_decorator(login_required, name='dispatch')
class BannerDesignView(TemplateView, LoginRequiredMixin):

    template_name = 'banner/banner_design.html'

    def get_context_data(self, **kwargs):
        context = super(BannerDesignView, self).get_context_data(**kwargs)
        context['banner'] = Banner.objects.get(id=self.kwargs['pk'])
        context['events'] = [
            event
            for event in Event.objects.filter(banner=context['banner'])
        ]
        return context
