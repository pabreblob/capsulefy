from django.forms.models import ModelForm
from main.models import User
from django.forms.widgets import DateInput

class UserForm(ModelForm):

    class Meta:
            model=User
            fields = ('first_name','last_name','username','password',
                      'email','email_notification','birthdate')
            
            widgets={
                    'birthdate':DateInput(),
                    }