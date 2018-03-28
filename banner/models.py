from django.conf import settings
from django.db import models


class EventDesign(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    changed = models.DateTimeField(auto_now=True, blank=True)


class BannerDesign(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    changed = models.DateTimeField(auto_now=True, blank=True)


class Banner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    design = models.ForeignKey(BannerDesign)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    changed = models.DateTimeField(auto_now=True, blank=True)

    @property
    def get_absolute_url(self):
        return "/banner/banner_detail/%i/" % self.id


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    logo = models.CharField(max_length=200)
    organizer = models.CharField(max_length=200)
    custom_title = models.CharField(max_length=200)
    custom_logo = models.CharField(max_length=200)
    custom_description = models.TextField()
    banner = models.ForeignKey(Banner)
    design = models.ForeignKey(EventDesign)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    changed = models.DateTimeField(auto_now=True, blank=True)
