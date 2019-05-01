from django.core.exceptions import ValidationError
import re

def validatePassword(password):
    if not re.match(r'^(?=.*[a-z])(?=.*?[A-Z])(?=.*\d)[A-Za-z\d@$!¡¿?/%*#?&.:,;Çç\-*+\\<>]{8,}$', password):
        
        raise ValidationError('Password incorrect, at least 8 characters, one number, one capital letter, one small letter '+\
                                                       ' (Optinal allow: @$!¡¿?/%*#?&.:,;Çç-*+\<>).'
        )
