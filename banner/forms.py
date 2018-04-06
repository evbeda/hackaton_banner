from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import inlineformset_factory
from .models import (
    Banner,
    Event,
)

class EventSelectedForm(forms.Form):

    class Meta:
        model = Event
        exclude = ()

    title = forms.CharField(required=False)
    description = forms.CharField(required=False)
    start = forms.CharField(required=False)
    end = forms.CharField(required=False)
    organizer = forms.HiddenInput()
    logo = forms.CharField(initial='logo', required=False)
    selection = forms.BooleanField(required=False)
    event_id = forms.CharField(required=False)
    custom_title = forms.CharField(required=False)
    custom_description = forms.CharField(required=False)
    custom_logo = forms.FileField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg'])
        ]
    )


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        exclude = ('user',)

EventSelectedFormSet = inlineformset_factory(
    Banner,
    Event,
    form=EventSelectedForm, extra=1
)
