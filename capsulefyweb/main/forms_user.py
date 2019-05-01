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
            
class PasswordForm(ModelForm):
    old_pass=forms.CharField(max_length=128)
    class Meta:
            model=User
            fields = ('password',)
    
    def clean_old_pass(self):
        data = self.cleaned_data['old_pass']
        
        if not self.instance.check_password(data):
            raise forms.ValidationError('The old password is not correct.')
        return data
            