import datetime

from django import forms


class ContactForm(forms.Form):
    Name = forms.CharField(max_length=50)
    Email = forms.EmailField()
    Message = forms.CharField(widget=forms.Textarea)


class ModularCapsuleForm(forms.Form):
    title = forms.CharField(max_length=250)
    emails = forms.CharField(max_length=2500, required=False)
    twitter = forms.BooleanField(required=False)
    facebook = forms.BooleanField(required=False)


class ModuleForm(forms.Form):
    description = forms.CharField(max_length=250)
    release_date = forms.DateTimeField()
    file = forms.FileField(required=False)

