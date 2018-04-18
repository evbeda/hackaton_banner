# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from social_django.models import UserSocialAuth
from unittest import skip
from mock import (
    MagicMock,
    patch,
)
from .factories import (
    BannerDesignFactory,
    BannerFactory,
    EventFactory,
    UserFactory,
)
from .models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)
from .views import (
    BannerView,
    BannerNewEventsSelectedCreateView,
    EditEventDesignView,
)
from .forms import (
    EventDesignForm,
)


class TestBase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username='testuser',
            password='12345',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        self.user.set_password('hello')
        self.user.save()
        login = self.client.login(username='testuser', password='hello')
        return login


class IndexViewTest(TestBase):

    def setUp(self):
        super(IndexViewTest, self).setUp()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_no_banners(self):
        response = self.client.get('/')
        self.assertContains(response, 'No banners yet!')


class BannerDesignTest(TestBase):

    def test_banner_design_creation(self):
        w = BannerDesignFactory()
        self.assertTrue(isinstance(w, BannerDesign))
        banner_design_list = BannerDesign.objects.all()
        banner_design = banner_design_list[len(banner_design_list) - 1]
        self.assertEqual(banner_design.name, w.name)


class BannerDesignViewTest(TestBase):

    def setUp(self):
        super(BannerDesignViewTest, self).setUp()
        self.banner = BannerFactory()

    def test_banner_design_view(self):
        response = self.client.get('/banner/' +
                                   str(self.banner.id) +
                                   '/preview/')
        self.assertEqual(response.status_code, 200)

    def test_events_inside_banner(self):
        event1 = EventFactory.build()
        event1.banner = self.banner
        event1.save()

        event2 = EventFactory.build()
        event2.banner = self.banner
        event2.save()

        response = self.client.get('/banner/' +
                                   str(self.banner.id) +
                                   '/preview/')
        self.assertContains(response, 'event-' + str(event1.id))
        self.assertContains(response, 'event-' + str(event2.id))


class BannerTest(TestBase):

    def test_banner_creation(self):
        w = BannerFactory()
        self.assertTrue(isinstance(w, Banner))
        banner_list = Banner.objects.all()
        banner = banner_list[len(banner_list) - 1]
        self.assertEqual(banner.title, w.title)


class BannerDetailViewTest(TestBase):

    def setUp(self):
        super(BannerDetailViewTest, self).setUp()
        self.banner = BannerFactory()

    def test_banner_detail_view(self):
        response = self.client.get(self.banner.get_absolute_url)
        self.assertEqual(response.status_code, 200)


class EventTest(TestBase):

    def test_event_creation(self):
        w = EventFactory()
        self.assertTrue(isinstance(w, Event))
        event_list = Event.objects.all()
        event = event_list[len(event_list) - 1]
        self.assertEqual(event.title, w.title)


class EventViewTest(TestBase):

    def setUp(self):
        super(EventViewTest, self).setUp()
        UserSocialAuth.objects.create(
            user=self.user,
            provider='eventbrite',
            extra_data={'access_token': 'user_token'},
        )

    @patch('banner.views.Eventbrite.get')
    def test_events_page_status_code(self, mock_eventbrite_get):
        response = self.client.get('/banner/new/')
        self.assertEqual(response.status_code, 200)

    @patch('banner.views.Eventbrite.get')
    def test_call_with_correct_parameters(self, mock_eventbrite_get):
        self.client.get('/banner/new/')
        self.assertEquals(
            mock_eventbrite_get.call_args_list[0][0][0],
            '/users/me/events/',
        )

    @skip('implementar pagina de error cuando no hay eventos en Eventbrite')
    @patch('banner.views.Eventbrite.get')
    def test_error_none_events(self, mock_eventbrite_get):
        response = self.client.get('/banner/new/')
        self.assertContains(response, 'You dont have any event in Eventbrite')

    @patch('banner.views.Eventbrite.get')
    def test_call_once_api(self, mock_eventbrite_get):
        self.client.get('/banner/new/')
        mock_eventbrite_get.assert_called_once()


class EventDesignFormTest(TestBase):

    def setUp(self):
        super(EventDesignFormTest, self).setUp()

    def test_edit_design_form_valid(self):
        form_data = {
            u'Edit': [u'Submit'],
            u'csrfmiddlewaretoken': [u'asd'],
            u'html': [
                u'<div class="panel-event">\r\n<div'
                'class="panel-event-header row">\r\n<div class="col-md-8'
                'event-logo">'
                '<em><strong><img class="img-rounded"'
                'src="|| logo ||" /></strong></em></div>\r\n\r\n<div'
                'class="col-md-4'
                'info-panel" style="padding-left:0!important">\r\n<div'
                'class="event-start-date-month"><em><strong>|| startdate_month'
                '||</strong></em></div>\r\n\r\n<div'
                'class="event-start-date-day"><em><strong>|| startdate_day'
                '||</strong></em></div>\r\n\r\n<div'
                'class="event-title"><em><strong>|| title'
                '||</strong></em></div>\r\n</div>\r\n</div>\r\n\r\n<div'
                'class="panel-event-body">\r\n<div class="box row">\r\n<div'
                'class="col-md-8" style="padding:0 !important">\r\n<div'
                'class="event-description"><em><strong>|| description'
                '||</strong></em></div>\r\n</div>\r\n\r\n<div class="col-md-4"'
                '>\r\n<div class="event-qr" id="qrcode">&nbsp;</div>'
                '\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n'
            ]
        }
        form = EventDesignForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_edit_design_form_invalid(self):
        form_data = {
            u'Edit': [u'Submit'],
            u'csrfmiddlewaretoken': [u'asd'],
            u'html': []
        }
        form = EventDesignForm(data=form_data)
        self.assertFalse(form.is_valid())


class EditEventDesignViewTest(TestBase):

    def setUp(self):
        super(EditEventDesignViewTest, self).setUp()
        self.banner = BannerFactory()
        self.event = EventFactory()

    def test_form_post_form_valid(self):

        form_data = {
            u'Edit': [u'Submit'],
            u'csrfmiddlewaretoken': [u'asd'],
            u'html': [
                u'<div>\r\n<div>\r\n<div>'
                '<em><strong><img '
                'src="|| logo ||" /></strong></em></div>\r\n\r\n<div>\r\n<div>'
                '<em><strong>|| startdate_month'
                '||</strong></em></div>\r\n\r\n<div '
                '><em><strong>|| startdate_day'
                '||</strong></em></div>\r\n\r\n<div>'
                '<em><strong>|| title'
                '||</strong></em></div>\r\n</div>\r\n</div>\r\n\r\n<div>'
                '\r\n<div>\r\n<div '
                'style="padding:0 !important">\r\n<div>'
                '<em><strong>|| description'
                '||</strong></em></div>\r\n</div>\r\n\r\n<div>'
                '\r\n<div id="qrcode">&nbsp;</div>'
                '\r\n</div>\r\n</div>\r\n</div>\r\n</div>'
            ]
        }

        response = self.client.post("/banner/{}/event/{}/".format(
            self.banner.id,
            self.event.id,
        ), form_data, follow=True)

        self.assertEquals(200, response.status_code)

        saved_event = Event.objects.select_related(
            'design',
        ).get(
            pk=self.event.id,
        )
        self.assertEquals(self.event, saved_event)
        self.assertEquals(form_data['html'][0], saved_event.design.html)

    def test_form_post_form_invalid(self):

        form_data = {
            u'Edit': [u'Submit'],
            u'csrfmiddlewaretoken': [u'asd'],
            u'html': []
        }

        response = self.client.post("/banner/{}/event/{}/".format(
            self.banner.id,
            self.event.id,
        ), form_data, follow=True)

        self.assertEquals(200, response.status_code)
        self.assertFormError(response, 'form', None, "Can't submit it empty!")

    def test_context_data(self):

        response = self.client.get("/banner/{}/event/{}/".format(
            self.banner.id,
            self.event.id,
        ), follow=True)

        self.assertTrue(
            isinstance(response.context_data['form'], EventDesignForm)
        )
        self.assertTrue(
            isinstance(response.context_data['view'], EditEventDesignView)
        )
        self.assertEquals(self.event, response.context_data['event'])
        self.assertEquals(200, response.status_code)

    def test_form_initial_data(self):

        default_event_design = EventDesign.objects.get(id=1)

        response = self.client.get("/banner/{}/event/{}/".format(
            self.banner.id,
            self.event.id,
        ), follow=True)

        self.assertEquals(
            response.context_data['form'].initial['html'],
            default_event_design.html
        )
