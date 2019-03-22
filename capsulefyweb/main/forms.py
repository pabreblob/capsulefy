from django import forms
from datetime import datetime, timedelta, timezone


class ContactForm(forms.Form):
    Name = forms.CharField(max_length=50)
    Email = forms.EmailField()
    Message = forms.CharField(widget=forms.Textarea)


class NewFreeCapsuleForm(forms.Form):
    title = forms.CharField(max_length=250)
    description = forms.CharField(max_length=250)
    release_date = forms.DateTimeField()
    emails = forms.CharField(max_length=2500, required=False)
    twitter = forms.BooleanField(required=False)
    facebook = forms.BooleanField(required=False)
    file = forms.FileField(required=False)

    def clean_release_date(self):
        data = self.cleaned_data['release_date']
        yearafter = datetime.now(timezone.utc) + timedelta(days=365)
        if data > yearafter:
            raise forms.ValidationError('The release date must be within 1 year from now')
        return data

    def clean_file(self):
        data = self.cleaned_data['file']
        if data is not None and data.size > 99999999:
            raise forms.ValidationError('The file size must not be over 10 B')
        return data


class EditFreeCapsuleForm(forms.Form):
    title = forms.CharField(max_length=250)
    description = forms.CharField(max_length=250)
    release_date = forms.DateTimeField()
    emails = forms.CharField(max_length=2500, required=False)
    twitter = forms.BooleanField(required=False)
    facebook = forms.BooleanField(required=False)

    def clean_release_date(self):
        data = self.cleaned_data['release_date']
        yearafter = datetime.now(timezone.utc) + timedelta(days=365)
        if data > yearafter:
            raise forms.ValidationError('The release date must be within 1 year from now')
        return data
