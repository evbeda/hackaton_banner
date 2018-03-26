# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from banner.models import Banner
from banner.models import BannerDesign
from django.utils import timezone
# from django.core.urlresolvers import reverse
# import unittest
# from selenium import webdriver
from .factories import UserFactory, BannerDesignFactory
# Create your tests here.


class BannerDesignTest(TestCase):

    def create_banner_design(self, name="Banner design"):
        return BannerDesign.objects.create(
            user=UserFactory(),
            banner_design_name=name,
            created_date=timezone.now(),
            )

    def test_banner_design_creation(self):
        w = self.create_banner_design()
        self.assertTrue(isinstance(w, BannerDesign))
        self.assertEqual("Banner design", w.banner_design_name)


class BannerTest(TestCase):

    def create_banner(
            self, banner_title='Banner title',
            banner_description='A description'
            ):
        return Banner.objects.create(
            banner_design=BannerDesignFactory(),
            user=UserFactory(),
            banner_title=banner_title,
            banner_description=banner_description,
            created_date=timezone.now(),
            )

    def test_banner_design_creation(self):
        w = self.create_banner()
        self.assertTrue(isinstance(w, Banner))
        self.assertEqual("Banner title", w.banner_title)


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