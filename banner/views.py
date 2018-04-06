# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from eventbrite import Eventbrite
from .models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)
from .forms import EventSelected

from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django import forms
from django.core.urlresolvers import reverse_lazy


DEFAULT_BANNER_DESIGN = 1


@method_decorator(login_required, name='dispatch')
class EventsView(FormView, LoginRequiredMixin):

    form_class = forms.Form
    template_name = "events/events.html"
    success_url = reverse_lazy('')

    def get_initial(self):
        access_token = self.request.user.social_auth.all()[0].access_token
        eventbrite = Eventbrite(access_token)
        self.events = eventbrite.get('/users/me/events/')['events']

    def get_context_data(self, **kwargs):
        context = super(EventsView, self).get_context_data(**kwargs)
        access_token = self.request.user.social_auth.all()[0].access_token
        eventbrite = Eventbrite(access_token)
        self.events = eventbrite.get('/users/me/events/')['events']

        data_event = []
        for event in self.events:
            if event['logo'] is not None:
                logo = event['logo']['url']
            else:
                logo = 'none'

            data = {
                'title': event['name']['text'],
                'description': event['description']['text'],
                'start': event['start']['local'],
                'end': event['end']['local'],
                'organizer': event['organizer_id'],
                'event_id': event['id'],
                'logo': logo,
            }
            data_event.append(data)
        event_formset = formset_factory(
            EventSelected, max_num=len(self.events))

        context['formset'] = event_formset(initial=data_event)
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            event_formset = formset_factory(EventSelected)
            formset = event_formset(request.POST, request.FILES)
            if not any([
                selection_cleaned_data['selection']
                for selection_cleaned_data in formset.cleaned_data
            ]):
                from django.core.exceptions import NON_FIELD_ERRORS
                form.add_error(NON_FIELD_ERRORS, 'No event selected')
                return self.form_invalid(form)
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, formset):
        self.get_initial()
        for i in range(len(formset.cleaned_data)):
            if formset.cleaned_data[i]['selection']:
                design = BannerDesign.objects.create(
                    user=self.request.user
                )
                banner = Banner.objects.create(
                    design=design,
                    user=self.request.user,
                )
                banner.description = 'This is the new banner'
                banner.title = 'New banner'
                banner.save()
                break
        for i in range(len(formset.cleaned_data)):
            if formset.cleaned_data[i]['selection']:
                for event in self.events:
                    if event['id'] == formset.cleaned_data[i]['event_id']:
                        edesign = EventDesign.objects.create(
                            user=self.request.user,
                        )
                        edesign.save()
                        even1 = Event()
                        even1.banner = banner
                        even1.design = edesign
                        even1.title = event['name']['text']
                        even1.description = event['description']['text']
                        even1.start = event['start']['local']
                        even1.end = event['end']['local']
                        if event['logo'] is not None:
                            logo = event['logo']['url']
                        else:
                            logo = 'none'
                        even1.logo = logo
                        even1.event_id = event['id']
                        if formset.cleaned_data[i]['custom_title'] is not None:
                            custom_title = formset.cleaned_data[i]['title']
                        else:
                            custom_title = 'none'
                        even1.custom_title = custom_title
                        if formset.cleaned_data[i]['custom_description'] is not None:
                            custom_description = formset.cleaned_data[i]['description']
                        else:
                            custom_description = 'none'
                        even1.custom_description = custom_description

                        even1.save()
        return super(EventsView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class BannerView(TemplateView, LoginRequiredMixin):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(BannerView, self).get_context_data(**kwargs)
        context['banners'] = Banner.objects.filter(user=self.request.user)
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
        banner = Banner.objects.select_related(
            'design'
        ) .get(
            id=self.kwargs['pk']
        )

        # Should be refactored when assigning positions
        # to the events in the banner
        events = [
            (idx, event)
            for idx, event in
            enumerate(
                Event.objects.filter(
                    banner=banner
                )
            )
        ]
        events_data = [
            event for event in self.get_events_data(events, banner)
        ]
        context['banner'] = banner
        context['events_data'] = events_data
        return context

    def get_events_data(self, events, banner):
        for event in events:
            yield {
                'data_x': (event[0] + 1) * banner.design.data_x,
                'data_y': (event[0] + 1) * banner.design.data_y,
                'data_z': (event[0] + 1) * banner.design.data_z,
                'data_rotate': banner.design.data_rotate,
                'data_scale': banner.design.data_scale,
                'event': event[1],
            }
