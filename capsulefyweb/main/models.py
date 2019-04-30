from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE


from datetime import timezone, datetime
from django.core.exceptions import ValidationError
import re


# Create your models here.
def birthdate_validator(value):
        
        if value >= datetime.now(timezone.utc).date():
            raise ValidationError('The birthdate must be in the past')
       
class Actor(User):
     
    birthdate=models.DateField(validators=[birthdate_validator,])
    class Meta:
        abstract = True

class User(Actor):
    email_notification=models.EmailField(blank=True)
    
    def clean(self):
        if not re.match(r'^(?=.*[a-z])(?=.*?[A-Z])(?=.*\d)[A-Za-z\d@$!¡¿?/%*#?&.:,;Çç\-*+\\<>]{8,}$', self.password):
            raise ValidationError({'password': ValidationError('Password incorrect, at least 8 characters, one number, one capital letter, one small letter '+\
                                                           ' (Optinal allow: @$!¡¿?/%*#?&.:,;Çç-*+\<>).'),})
            

class Social_network(models.Model):
    social_type=models.CharField(max_length=1,choices=(('F','FACEBOOK'),('T','TWITTER')))
    token=models.CharField(max_length=100)
    secret=models.CharField(max_length=100,null=True)
    user=models.ForeignKey(User,related_name='social_networks', on_delete=CASCADE)
    
    
class Admin(Actor):
    pass

class Capsule(models.Model):
    creation_date=models.DateTimeField(auto_now_add=True)
    title=models.CharField(max_length=250)
    emails=models.CharField(blank=True, null=True, max_length=2500)
    capsule_type=models.CharField(max_length=1,choices=(('F','FREE'),('P','PREMIUM'),('M','MODULAR')))
    private=models.BooleanField()
    price=models.DecimalField(null=True,max_digits=7, decimal_places=2)
    dead_man_switch=models.BooleanField()
    dead_man_counter=models.BigIntegerField()
    dead_man_initial_counter=models.BigIntegerField()
    time_unit=models.IntegerField(null=True,choices=((0,'minutes'),(1,'days'),(2,'months'),(3,'years')))
    twitter=models.BooleanField()
    facebook=models.BooleanField()
    creator=models.ForeignKey(User,related_name='capsuls', on_delete=CASCADE)
    payment_id=models.CharField(max_length=60,null=True)
    expiration_notify = models.BooleanField(default=False)
    ''' Una capsula es liberada si tiene algún 
    modulo que este liberado '''
    @property
    def is_released(self):
        res=False
        for i in self.modules.all():
            if(i.is_released):
                res=True
                break
        return res

    def seconds_to_unit(self):
        conversion_to_seconds = [60, 86400, 2592000, 31536000]
        if self.time_unit!=None:
            res=round(self.dead_man_counter/conversion_to_seconds[int(self.time_unit)])
        else:
            res=0
        return res

    def unit_to_seconds(self,unit):
        conversion_to_seconds = [60, 86400, 2592000, 31536000]
        if unit!=None:
            res=self.dead_man_counter*conversion_to_seconds[unit]
        else:
            res=0
        return res
class Module(models.Model):
    description=models.CharField(max_length=250)
    release_date=models.DateTimeField()
    capsule=models.ForeignKey(Capsule,related_name='modules', on_delete=CASCADE)
    release_notify=models.BooleanField(default=False)
    facebook_notify = models.BooleanField(default=False)
    twitter_notify = models.BooleanField(default=False)
    @property
    def is_released(self):
        return datetime.now(timezone.utc) >= self.release_date
    
class File(models.Model):
    url=models.URLField()
    size=models.DecimalField(null=True,max_digits=7, decimal_places=2)
    type=models.CharField(max_length=1,choices=(('F','FILE'),('I','IMAGE'),('V','VIDEO')))
    remote_name=models.CharField(max_length=150)
    local_name=models.CharField(max_length=150)
    module=models.ForeignKey(Module, related_name='files', on_delete=CASCADE)

