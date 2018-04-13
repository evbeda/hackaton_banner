# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse_lazy
from django.db import IntegrityError, transaction
from django.forms import modelformset_factory
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.shortcuts import render
from dateutil.parser import parse as parse_date
import datetime
from datetime import datetime
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
)
from eventbrite import Eventbrite
from . import forms
from .models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)
from django.views.generic.edit import FormView
from django.shortcuts import render, get_object_or_404


DEFAULT_BANNER_DESIGN = 1


@method_decorator(login_required, name='dispatch')
class BannerNewEventsSelectedCreateView(FormView, LoginRequiredMixin):

    form_class = forms.BannerForm
    template_name = 'events_list.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):

        context = super(
            BannerNewEventsSelectedCreateView,
            self
        ).get_context_data(**kwargs)

        social_auth = self.request.user.social_auth.filter(
            provider='eventbrite'
        )
        if len(social_auth) > 0:
            access_token = social_auth[0].access_token
            eventbrite = Eventbrite(access_token)
            self.events = eventbrite.get('/users/me/events/')['events']

        data_event = []
        for event in self.events:
            if event['logo'] is not None:
                logo = event['logo']['url']
            else:
                logo = 'none'

            if parse_date(event['start']['local']) >= datetime.today():

                data = {
                    'title': event['name']['text'],
                    'description': event['description']['text'],
                    'start': event['start']['local'].replace('T', ' '),
                    'end': event['end']['local'].replace('T', ' '),
                    'organizer': event['organizer_id'],
                    'evb_id': event['id'],
                    'evb_url': event['url'],
                    'logo': logo,
                }
                data_event.append(data)

        messages = []
        if data_event == []:
            messages = 'You dont have active events'
            context['messages'] = messages
        else:

            EventFormSet = modelformset_factory(
                Event,
                form=forms.EventForm,
                extra=len(data_event),
            )

            formset = EventFormSet(
                initial=data_event,
                queryset=Event.objects.none(),
            )

            context['formset'] = formset
        return context

    def edit_banner(self, form, formset, pk, *args, **kwargs):
        form.instance.user = self.request.user
        updating_banner = Banner.objects.get(id=self.kwargs['pk'])
        updating_banner.title = form.cleaned_data['title']
        updating_banner.description = form.cleaned_data['description']
        updating_banner.save()
        updating_events = Event.objects.filter(banner_id=self.kwargs['pk'])
        events_evb_id_list = [event.evb_id for event in updating_events]
        updated_events = formset.save(commit=False)
        '''delete events'''
        ev_id_list = [
            event.evb_id for event in updated_events
            if event is not None
        ]
        for updating_event in updating_events:
            if updating_event.evb_id not in ev_id_list:
                Event.objects.get(id=updating_event.id)
                updating_event.delete()
        for event in updated_events:
            if event is not None:

                '''create evetns'''
                if event.evb_id not in events_evb_id_list:
                    e_design = EventDesign.objects.create(
                        user=self.request.user,
                    )
                    event.banner = updating_banner
                    event.design = e_design
                    if event.custom_logo:
                        fs = FileSystemStorage()
                        filename = fs.save(
                            event.custom_logo.name,
                            event.custom_logo
                        )
                        event.custom_logo = fs.url(filename)
                    event.save()
                else:
                    for updating_event in updating_events:

                        '''update events'''
                        if event.evb_id == updating_event.evb_id:
                            updating_event.custom_title = event.custom_title
                            updating_event.custom_description \
                                = event.custom_description
                            updating_event.start = event.start
                            updating_event.end = event.end
                            try:
                                if event.custom_logo:
                                    fs = FileSystemStorage()
                                    filename = fs.save(
                                        event.custom_logo.name,
                                        event.custom_logo
                                    )
                                    updating_event.custom_logo \
                                        = fs.url(filename)
                                updating_event.save()
                            except IntegrityError as e:
                                print e.message
        return super(
            BannerNewEventsSelectedCreateView,
            self,
        ).form_valid(form)

    def post(self, request, *args, **kwargs):
        form = forms.BannerForm(
            request.POST,
        )

        EventFormSet = modelformset_factory(
            Event,
            form=forms.EventForm,
        )

        formset = EventFormSet(
            request.POST,
            request.FILES,
            queryset=Event.objects.none(),
        )
        if form.is_valid() and formset.is_valid():
            if not any([
                    selection_cleaned_data['selection']
                    for selection_cleaned_data in formset.cleaned_data
            ]):
                form.add_error(NON_FIELD_ERRORS, 'No event selected')
                return render(
                    request,
                    'event_list.html',
                    {'form': form, 'formset': formset}
                )
            if 'pk' in self.kwargs:
                return self.edit_banner(form, formset, self.kwargs['pk'])
            else:
                return self.form_valid(form, formset)
        else:
            return self.form_invalid(form)

    @transaction.atomic
    def form_valid(self, form, formset):
        form.instance.user = self.request.user
        banner = form.save(commit=False)
        events = formset.save(commit=False)
        try:
            with transaction.atomic():
                b_design = BannerDesign.objects.get(
                    id=DEFAULT_BANNER_DESIGN,
                )
                banner.design = b_design
                banner.save()

                e_design = EventDesign.objects.create(
                    user=self.request.user,
                )

                for event in events:
                    if event is not None:
                        event.banner = banner
                        event.design = e_design
                        if event.custom_logo:
                            fs = FileSystemStorage()
                            filename = fs.save(
                                event.custom_logo.name,
                                event.custom_logo
                            )
                            event.custom_logo = fs.url(filename)
                        event.save()
        except IntegrityError as e:
            print e.message

        return super(
            BannerNewEventsSelectedCreateView,
            self,
        ).form_valid(form)


class BannerDeleteView(DeleteView):
    model = Banner
    template_name = 'delete_banner.html'
    success_url = reverse_lazy('index')


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

    def get_object(self, queryset=None):
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


