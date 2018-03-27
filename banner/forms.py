from django import forms


class EventSelected(forms.Form):

    def add_event(self, event):
        self.fields[event['id']] = forms.BooleanField(required=False)
        #self.fields[event['name']['text']] = forms.BooleanField(required=False)
