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
from django.views.generic.edit import (
    CreateView,
)
from eventbrite import Eventbrite
from . import forms
from .models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)


DEFAULT_BANNER_DESIGN = 1


@method_decorator(login_required, name='dispatch')
class BannerNewEventsSelectedCreateView(CreateView, LoginRequiredMixin):

    form_class = forms.BannerForm
    template_name = "events/events.html"
    success_url = reverse_lazy('index')

    def get_initial(self):
        access_token = self.request.user.social_auth.all()[0].access_token
        eventbrite = Eventbrite(access_token)
        self.events = eventbrite.get('/users/me/events/')['events']

    def get_context_data(self, **kwargs):
        context = super(
            BannerNewEventsSelectedCreateView,
            self
        ).get_context_data(**kwargs)
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
                'start': event['start']['local'].replace('T', ' '),
                'end': event['end']['local'].replace('T', ' '),
                'organizer': event['organizer_id'],
                'evb_id': event['id'],
                'evb_url': event['url'],
                'logo': logo,
            }
            data_event.append(data)

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
            if not formset.cleaned_data:
                form.add_error(NON_FIELD_ERRORS, 'No event selected')
                return render(
                    request,
                    'events.html',
                    {'form': form, 'formset': formset}
                )
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


class BannerCreateView(CreateView):
    model = Banner
    fields = ['first_name', 'last_name']


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
