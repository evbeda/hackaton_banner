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
from django.views.generic.edit import FormView
from django.shortcuts import render
import calendar
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
from forms import LocalizationForm
from django.views.generic.edit import FormView
from django.shortcuts import render, get_object_or_404
import os
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
from django.http import HttpResponse
from django.conf import settings
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
import imgkit
from django.http import HttpResponse
import uuid



DEFAULT_BANNER_DESIGN = 1
DEFAULT_EVENT_DESIGN = 1


@method_decorator(login_required, name='dispatch')
class BannerNewEventsSelectedCreateView(FormView, LoginRequiredMixin):

    form_class = forms.BannerForm
    template_name = 'events_list.html'
    success_url = reverse_lazy('index')

    def get_api_events(self, social_auth):
        access_token = social_auth[0].access_token
        eventbrite = Eventbrite(access_token)
        return eventbrite.get('/users/me/events/')['events']

    def get_context_data(self, **kwargs):

        context = super(
            BannerNewEventsSelectedCreateView,
            self
        ).get_context_data()

        social_auth = self.request.user.social_auth.filter(
            provider='eventbrite'
        )
        if len(social_auth) > 0:
            events = self.get_api_events(social_auth)

        if self.kwargs:
            existing_events = Event.objects.filter(
                banner_id=self.kwargs['pk'],
            )
            list_evb_id = [event.evb_id for event in existing_events]
        else:
            list_evb_id = []

        data_event = []
        for event in events:
            if parse_date(event['start']['local']) >= datetime.today():
                if int(event['id']) not in list_evb_id:
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

        messages = []
        if data_event == [] and 'existing_events' not in locals():
            messages.append('You dont have active events')
            context['messages'] = messages
        else:
            EventFormSet = modelformset_factory(
                Event,
                form=forms.EventForm,
                extra=len(data_event),
            )
            if self.kwargs:
                formset = EventFormSet(
                    initial=data_event,
                    queryset=Event.objects.filter(
                        banner_id=self.kwargs['pk']
                    ),
                )
            else:
                formset = EventFormSet(
                    initial=data_event,
                    queryset=Event.objects.none(),
                )
            context['formset'] = formset
        return context

    def get_form_kwargs(self, *args, **kwargs):
        if self.kwargs:
            banner = Banner.objects.get(id=self.kwargs['pk'])
            kwargs = super(
                BannerNewEventsSelectedCreateView, self
            ).get_form_kwargs()
            kwargs['initial']['title'] = banner.title
            kwargs['initial']['description'] = banner.description
        return kwargs

    def edit_banner(self, form, formset, pk, *args, **kwargs):
        form.instance.user = self.request.user
        updating_banner = Banner.objects.get(id=self.kwargs['pk'])
        updating_banner.title = form.cleaned_data['title']
        updating_banner.description = form.cleaned_data['description']
        updating_banner.save()
        updating_events = Event.objects.filter(banner_id=self.kwargs['pk'])
        events_evb_id_list = [event.evb_id for event in updating_events]
        updated_events = formset.cleaned_data
        '''delete events'''
        updated_evb_id_list = [
            event['evb_id'] for event in updated_events
            if event['selection']
        ]
        # import ipdb; ipdb.set_trace()
        for updating_event in updating_events:
            if updating_event.evb_id not in updated_evb_id_list:
                Event.objects.get(id=updating_event.id)
                updating_event.delete()
        for event in updated_events:
            if event['selection']:

                '''create evetns'''
                if int(event['evb_id']) not in events_evb_id_list:
                    e_design = EventDesign.objects.get(
                        id=DEFAULT_EVENT_DESIGN,
                    )
                    new_event = Event()
                    new_event.banner = updating_banner
                    new_event.design = e_design
                    if event['custom_logo']:
                        fs = FileSystemStorage()
                        filename = fs.save(
                            event['custom_logo'].name,
                            event['custom_logo']
                        )
                        new_event.custom_logo = fs.url(filename)
                    new_event.title = event['title']
                    new_event.description = event['description']
                    new_event.start = event['start']
                    new_event.end = event['end']
                    new_event.logo = event['logo']
                    new_event.organizer = event['organizer']
                    new_event.evb_id = event['evb_id']
                    new_event.evb_url = event['evb_url']
                    new_event.custom_title = event['custom_title']
                    new_event.custom_description = event['custom_description']
                    new_event.save()
                else:
                    for updating_event in updating_events:
                        '''update events'''
                        if int(event['evb_id']) == updating_event.evb_id:
                            updating_event.custom_title = event['custom_title']
                            updating_event.custom_description \
                                = event['custom_description']
                            try:
                                if event['custom_logo']:
                                    fs = FileSystemStorage()
                                    filename = fs.save(
                                        event['custom_logo'].name,
                                        event['custom_logo']
                                    )
                                    updating_event.custom_logo \
                                        = fs.url(filename)
                                # updating_event.save()
                            except IntegrityError as e:
                                print e.message
                            updating_event.save()
        return super(
            BannerNewEventsSelectedCreateView,
            self,
        ).form_valid(form)

    def post(self, request, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
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
        # import ipdb; ipdb.set_trace()
        if form.is_valid() and formset.is_valid():
            if not any([
                    selection_cleaned_data['selection']
                    for selection_cleaned_data in formset.cleaned_data
            ]):
                form.add_error(NON_FIELD_ERRORS, 'No events selected')
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

                e_design = EventDesign.objects.get(
                    id=DEFAULT_EVENT_DESIGN,
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
        banners = Banner.objects.filter(user=self.request.user)
        for banner in banners:
            events = Event.objects.filter(banner=banner)
            images = [event.logo for event in events]
        # if algo:
            # make_video(["downloaded.png", "banner/static/images/Eventbrite_wordmark_orange.png"], format=VideoWriter_fourcc(*'PIM1'))
        context['banners'] = banners
        return context


def video(request, pk):
    files = get_banner_images(pk)
    video_output = str(uuid.uuid4()) + '.avi'
    vid = make_video(files, format=VideoWriter_fourcc(*'PIM1'), outvid=video_output)
    DATA_ROOT = ''
    file_path = os.path.join(DATA_ROOT, video_output)
    filename = os.path.basename(video_output)
    chunk_size = 8192
    response = StreamingHttpResponse(
        FileWrapper(open(file_path, 'rb'), chunk_size),
        content_type="application/octet-stream"
    )
    response['Content-Length'] = os.path.getsize(video_output)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    cv2.destroyAllWindows()
    return response


def make_video(images, outimg=None, fps=5, size=None,
               is_color=True, format="XVID", outvid='image_video.avi'):
    fourcc = VideoWriter_fourcc(*'PIM1')
    vid = None
    for image in images:
        if not os.path.exists(image):
            raise Exception("image")
        img = imread(image)
        if vid is None:
            if size is None:
                size = img.shape[1], img.shape[0]
                size = 1000, 400
            vid = VideoWriter(outvid, fourcc, float(fps), size, is_color)
        if size[0] != img.shape[1] and size[1] != img.shape[0]:
            img = resize(img, size)
        vid.write(img)
    vid.release()
    return vid


@method_decorator(login_required, name='dispatch')
class BannerDetailView(DetailView, LoginRequiredMixin):

    model = Banner

    def get_context_data(self, **kwargs):
        context = super(BannerDetailView, self).get_context_data(**kwargs)
        banner = Banner.objects.get(id=self.kwargs['pk'])
        events = Event.objects.filter(banner=banner)

        context['banner'] = banner
        context['events'] = events
        return context


class BannerPreview(TemplateView, LoginRequiredMixin):

    template_name = 'banner/preview.html'

    def get_context_data(self, **kwargs):
        context = super(BannerPreview, self).get_context_data(**kwargs)
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
        '''events order'''
        # events.sort(key=lambda tup: tup[0])

        for event in events:
            idx, event = event
            event = self.replace_data(event)
            yield {
                'data_x': (idx + 1) * banner.design.data_x,
                'data_y': (idx + 1) * banner.design.data_y,
                'data_z': (idx + 1) * banner.design.data_z,
                'data_rotate': banner.design.data_rotate,
                'data_scale': banner.design.data_scale,
                'event': event,
            }

    def replace_data(self, event):
        if event.custom_title:
            event.design.html = unicode(event.design.html).replace(
                '|| title ||', unicode(event.custom_title)
            )
        else:
            event.design.html = unicode(event.design.html).replace(
                '|| title ||', unicode(event.title)
            )

        if event.custom_description:
            event.design.html = unicode(event.design.html).replace(
                '|| description ||', unicode(event.custom_description)
            )
        else:
            event.design.html = unicode(event.design.html).replace(
                '|| description ||', unicode(event.description)
            )

        if event.custom_logo:
            event.design.html = unicode(event.design.html).replace(
                '|| logo ||', unicode(event.custom_logo)
            )
        else:
            event.design.html = unicode(event.design.html).replace(
                '|| logo ||', unicode(event.logo)
            )

        event.design.html = unicode(event.design.html).replace(
            '|| startdate_month ||',
            calendar.month_name[event.start.month][:3].upper() + '.'
        )

        event.design.html = unicode(event.design.html).replace(
            '|| startdate_day ||', unicode(event.start.day)
        )

        event.design.html = unicode(event.design.html).replace(
            '|| evb_url ||', unicode(event.evb_url)
        )

        event.design.html = unicode(event.design.html).replace(
            '|| id ||', unicode(event.id)
        )

        return event


@method_decorator(login_required, name='dispatch')
class EditEventDesignView(FormView, LoginRequiredMixin):

    template_name = 'event/edit_design.html'
    form_class = forms.EventDesignForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super(EditEventDesignView, self).get_context_data(**kwargs)
        event = Event.objects.get(pk=self.kwargs['epk'])
        context['event'] = event
        return context

    def get_form_kwargs(self):
        kwargs = super(EditEventDesignView, self).get_form_kwargs()
        event = Event.objects.select_related(
            'design'
        ).get(
            pk=self.kwargs['epk']
        )
        kwargs['initial']['html'] = event.design.html
        return kwargs

    def post(self, request, *args, **kwargs):

        event = Event.objects.select_related(
            'design'
        ).get(
            pk=self.kwargs['epk']
        )

        if event.design.name == 'default':
            form = forms.EventDesignForm(
                request.POST,
            )
        else:
            form = forms.EventDesignForm(
                request.POST,
                instance=event.design,
            )
        if form.is_valid():
            return self.form_valid(form)

        form.add_error(NON_FIELD_ERRORS, "Can't submit it empty!")
        return render(
            request,
            'event/edit_design.html',
            {'form': form}
        )

    def form_valid(self, form, *args, **kwargs):
        form.instance.user = self.request.user
        event_design = form.save()
        if event_design.name != 'default':
            event = Event.objects.select_related(
                'design'
            ).get(
                pk=self.kwargs['epk']
            )
            event.design = event_design
        event_design.save()
        event.save()

        return super(
            EditEventDesignView,
            self,
        ).form_valid(form)


class LocalizationView(FormView):
    form_class = LocalizationForm
    template_name = "select_localization.html"

    def post(self, request, *args, **kwargs):
        form = forms.LocalizationForm(
            request.POST,
        )

class SelectEventFromLocalization(FormView):
    form_class = forms.BannerForm
    template_name = 'events_list.html'
    success_url = reverse_lazy('index')

    def get_api_events(self, social_auth, latitude, longitude):
        access_token = social_auth[0].access_token
        eventbrite = Eventbrite(access_token)
        data = {
            'event_search': {
                'page_size': 35,
                'dates': 'current_future',
                'point_radius': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius': '5km'
                }
            }
        }
        return eventbrite.post('/destination/search/', data)['events']

    def get_context_data(self, **kwargs):

        context = super(
            BannerNewEventsSelectedCreateView,
            self
        ).get_context_data()

        social_auth = self.request.user.social_auth.filter(
            provider='eventbrite'
        )
        if len(social_auth) > 0:
            events = self.get_api_events(social_auth)

        if self.kwargs:
            existing_events = Event.objects.filter(
                banner_id=self.kwargs['pk'],
            )
            list_evb_id = [event.evb_id for event in existing_events]
        else:
            list_evb_id = []

        data_event = []
        for event in events:
            if parse_date(event['start']['local']) >= datetime.today():
                if int(event['id']) not in list_evb_id:
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

        messages = []
        if data_event == [] and 'existing_events' not in locals():
            messages.append('You dont have active events')
            context['messages'] = messages
        else:
            EventFormSet = modelformset_factory(
                Event,
                form=forms.EventForm,
                extra=len(data_event),
            )
            if self.kwargs:
                formset = EventFormSet(
                    initial=data_event,
                    queryset=Event.objects.filter(
                        banner_id=self.kwargs['pk']
                    ),
                )
            else:
                formset = EventFormSet(
                    initial=data_event,
                    queryset=Event.objects.none(),
                )
            context['formset'] = formset
        return context


def get_banner_images(pk):
    banner = Banner.objects.get(pk=pk)
    events = Event.objects.select_related('design').filter(banner=banner)
    # output = ''
    files = []
    for event in events:
        event = replace_data(event)
        name = str(uuid.uuid4()) + '.jpg'
        # event.design.html
        try:
            body = '<div style="width:100px; height: 50px">'
            end = '</div>'
            imgkit.from_string(body + event.design.html + end, name)
        except Exception:
            pass

        files.append(name)
    return files


def replace_data(event):
    if event.custom_title:
        event.design.html = unicode(event.design.html).replace(
            '|| title ||', unicode(event.custom_title)
        )
    else:
        event.design.html = unicode(event.design.html).replace(
            '|| title ||', unicode(event.title)
        )

    if event.custom_description:
        event.design.html = unicode(event.design.html).replace(
            '|| description ||', unicode(event.custom_description)
        )
    else:
        event.design.html = unicode(event.design.html).replace(
            '|| description ||', unicode(event.description)
        )

    if event.custom_logo:
        event.design.html = unicode(event.design.html).replace(
            '|| logo ||', unicode(event.custom_logo)
        )
    else:
        event.design.html = unicode(event.design.html).replace(
            '|| logo ||', unicode(event.logo)
        )

    event.design.html = unicode(event.design.html).replace(
        '|| startdate_month ||',
        calendar.month_name[event.start.month][:3].upper() + '.'
    )

    event.design.html = unicode(event.design.html).replace(
        '|| startdate_day ||', unicode(event.start.day)
    )

    event.design.html = unicode(event.design.html).replace(
        '|| evb_url ||', unicode(event.evb_url)
    )

    event.design.html = unicode(event.design.html).replace(
        '|| id ||', unicode(event.id)
    )

    return event

