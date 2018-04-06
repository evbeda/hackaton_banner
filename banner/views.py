# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse_lazy
from django.forms import formset_factory
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView,
)
from eventbrite import Eventbrite
from .forms import EventSelectedForm
from .models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)


DEFAULT_BANNER_DESIGN = 1


@method_decorator(login_required, name='dispatch')
class BannerNewEventsSelectedCreateView(CreateView, LoginRequiredMixin):

    model = Banner
    fields = ['title', 'description']
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
                'start': event['start']['local'],
                'end': event['end']['local'],
                'organizer': event['organizer_id'],
                'event_id': event['id'],
                'logo': logo,
            }
            data_event.append(data)
        event_formset = formset_factory(
            EventSelectedForm, max_num=len(self.events))

        context['formset'] = event_formset(initial=data_event)
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            event_formset = formset_factory(EventSelectedForm)
            formset = event_formset(request.POST, request.FILES)
            if not any([
                    selection_cleaned_data['selection']
                    for selection_cleaned_data in formset.cleaned_data
            ]):
                form.add_error(NON_FIELD_ERRORS, 'No event selected')
                return self.form_invalid(form)
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, formset):
        self.get_initial()
        form.instance.user = self.request.user
        selected_events = [
            formset.cleaned_data[i] for i in
            range(len(formset.cleaned_data))
            if formset.cleaned_data[i]['selection']
        ]
        if any(selected_events):
            design = BannerDesign.objects.get(
                id=DEFAULT_BANNER_DESIGN
            )
            banner = form.save(commit=True)
            banner.design = design
            banner.save()

            for event in self.events:
                for selected in selected_events:
                    if event['id'] == selected['event_id']:
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
                        even1.logo = logo
                        even1.event_id = event['id']
                        even1.custom_title = selected['title']
                        even1.custom_description = selected['description']
                        if selected['custom_logo'] is not None:
                            fs = FileSystemStorage()
                            filename = fs.save(
                                selected['custom_logo'].name,
                                selected['custom_logo']
                            )
                            even1.custom_logo = fs.url(filename)
                        even1.save()
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
