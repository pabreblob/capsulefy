from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE

import datetime
from datetime import timezone


# Create your models here.
class Credit_card(models.Model):
    holder_name = models.CharField(max_length=50)
    brand_name = models.CharField(max_length=50)
    number = models.CharField(max_length=24)
    expiration_month = models.IntegerField(validators=[MaxValueValidator(12), MinValueValidator(1)])
    expiration_year = models.IntegerField(validators=[MaxValueValidator(9999), MinValueValidator(2019)])
    cvv = models.IntegerField(validators=[MaxValueValidator(999), MinValueValidator(100)])



class Actor(User):
    birthdate=models.DateField()
    class Meta:
        abstract = True

class User(Actor):
    email_notification=models.EmailField()

class Social_network(models.Model):
    social_type=models.CharField(max_length=1,choices=(('F','FACEBOOK'),('T','TWITTER')))
    token=models.CharField(max_length=50)

    user=models.ForeignKey(User,related_name='social_networks', on_delete=CASCADE)
    
    
class Admin(Actor):
    pass

class Capsule(models.Model):
    creation_date=models.DateTimeField(auto_now_add=True)
    title=models.CharField(max_length=250)
    emails=models.CharField(blank=True,max_length=2500)
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
    
    credit_card=models.ForeignKey(Credit_card,related_name='capsuls', on_delete=CASCADE,null=True)
    
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
    @property
    def is_released(self):
        return datetime.datetime.now(timezone.utc) >= self.release_date
    
class File(models.Model):
    url=models.URLField()
    size=models.DecimalField(null=True,max_digits=7, decimal_places=2)
    type=models.CharField(max_length=1,choices=(('F','FILE'),('I','IMAGE'),('V','VIDEO')))
    remote_name=models.CharField(max_length=150)
    local_name=models.CharField(max_length=150)
    module=models.ForeignKey(Module, related_name='files', on_delete=CASCADE)

