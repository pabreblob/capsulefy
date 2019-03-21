from django.forms import forms


class fileForm(forms.Form):
    File = forms.FileField()
