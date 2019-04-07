from django.forms.models import ModelForm
from main.models import User
from django.forms.widgets import DateInput
from django import forms

class UserForm(ModelForm):
    email=forms.EmailField(required=True)
    class Meta:
            model=User
            fields = ('first_name','last_name','username','password',
                      'email','email_notification','birthdate')
            
            widgets={
                    'birthdate':DateInput(),
                    }