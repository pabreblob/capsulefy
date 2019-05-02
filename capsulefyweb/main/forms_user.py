from django.forms.models import ModelForm
from main.models import User
from django.forms.widgets import DateInput
from django import forms
from main.validators import validatePassword

class UserForm(ModelForm):
    email=forms.EmailField(required=True)
    class Meta:
            model=User
            fields = ('first_name','last_name','username','password',
                      'email','email_notification','birthdate')
            
            widgets={
                    'birthdate':DateInput(),
                    }
    
    def clean_password(self):
        password= self.cleaned_data['password'] 
        validatePassword(password)
        return password
class PasswordForm(ModelForm):
    old_pass=forms.CharField(max_length=128)
    class Meta:
            model=User
            fields = ('password',)
    def clean_password(self):
        password= self.cleaned_data['password'] 
        validatePassword(password)
        return password
    def clean_old_pass(self):
        data = self.cleaned_data['old_pass']
        
        if not self.instance.check_password(data):
            raise forms.ValidationError('The old password is not correct.')
        return data

    def clean(self):
        if not re.match(r'^(?=.*[a-z])(?=.*?[A-Z])(?=.*\d)[A-Za-z\d@$!¡¿?/%*#?&.:,;Çç\-*+\\<>]{8,}$', self.password):
            raise forms.ValidationError({'password': forms.ValidationError(
                'Password incorrect, at least 8 characters, one number, one capital letter, one small letter ' + \
                ' (Optinal allow: @$!¡¿?/%*#?&.:,;Çç-*+\<>).'), })