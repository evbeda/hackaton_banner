# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import skip
from django.test import TestCase
from banner.models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)
from banner.views import BannerView
from django.utils import timezone
from django.contrib.auth import get_user_model
from .factories import (
    BannerFactory,
    BannerDesignFactory,
    UserFactory,
)
# Create your tests here.


class ProjectTests(TestCase):

    def setUp(self):
        login = get_login(self)
        self.assertTrue(login)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_no_banners(self):
        response = self.client.get('/')
        self.assertContains(response, 'No banners yet!')


class BannerViewTest(TestCase):

    def setUp(self):
        login = get_login(self)
        self.assertTrue(login)
        self.banner = BannerFactory()

    def test_banner_view(self):
        response = self.client.get(self.banner.get_absolute_url)
        self.assertEqual(response.status_code, 200)


class BannerDesignTest(TestCase):

    def test_banner_design_creation(self):
        w = BannerDesignFactory()
        self.assertTrue(isinstance(w, BannerDesign))
        self.assertEqual('BannerDesign000', w.name)


class BannerTest(TestCase):

    def test_banner_creation(self):
        w = BannerFactory()
        self.assertTrue(isinstance(w, Banner))
        self.assertEqual('Banner000', w.title)

    @skip('Falta implementar banner_new!')
    def test_banner_new(self):
        design = EventDesign(user=UserFactory())
        design.save()
        ev1 = Event(
            start=timezone.now(),
            end=timezone.now(),
            design=design
        )
        ev2 = Event(
            start=timezone.now(),
            end=timezone.now(),
            design=design
        )
        events = [ev1, ev2]
        bw = BannerView()
        b = bw.banner_new(events)
        self.assertTrue(isinstance(b, Banner))
        self.assertEquals(b, ev1.banner)


def get_login(self):
    self.user = get_user_model().objects.create(
        username='testuser',
        password='12345',
        is_active=True,
        is_staff=True,
        is_superuser=True
    )
    self.user.set_password('hello')
    self.user.save()
    # self.user = authenticate(username='testuser', password='hello')
    login = self.client.login(username='testuser', password='hello')
    return login


# class TestSignup(unittest.TestCase):

#     def setUp(self):
#         self.driver = webdriver.Firefox()

#     def test_signup_fire(self):
#         self.driver.get("http://localhost:8000/add/")
#         self.driver.find_element_by_id('id_title').send_keys("test title")
#         self.driver.find_element_by_id('id_body').send_keys("test body")
#         self.driver.find_element_by_id('submit').click()
#         self.assertIn("http://localhost:8000/", self.driver.current_url)

#     def tearDown(self):
#         self.driver.quit
