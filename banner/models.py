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
    name = models.CharField(
        default='horizontal layout',
        max_length=200,
        null=True
    )
    data_x = models.IntegerField(default=-2000, null=True)
    data_y = models.IntegerField(default=0, null=True)
    data_z = models.IntegerField(default=0, null=True)
    data_rotate = models.IntegerField(default=0, null=True)
    data_scale = models.IntegerField(default=1, null=True)
    multiplier_x = models.IntegerField(default=0, null=True)
    multiplier_y = models.IntegerField(default=0, null=True)
    multiplier_z = models.IntegerField(default=0, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    changed = models.DateTimeField(auto_now=True, blank=True)


class Banner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    design = models.ForeignKey(BannerDesign, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    changed = models.DateTimeField(auto_now=True, blank=True)

    @property
    def get_absolute_url(self):
        return "/banner/%i/banner_detail/" % self.id


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    logo = models.CharField(max_length=1000)
    organizer = models.CharField(max_length=200)
    custom_title = models.CharField(max_length=200)
    custom_logo = models.FileField()
    custom_description = models.TextField()
    banner = models.ForeignKey(Banner)
    design = models.ForeignKey(EventDesign, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    changed = models.DateTimeField(auto_now=True, blank=True)

    def get_absolute_url(self):
        return 'https://www.eventbrite.com/e/%i' % self.id
