from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE


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
    twitter=models.BooleanField()
    facebook=models.BooleanField()
    
    creator=models.ForeignKey(User,related_name='capsuls', on_delete=CASCADE)
    
    credit_card=models.ForeignKey(Credit_card,related_name='capsuls', on_delete=CASCADE,null=True)
    
class Module(models.Model):
    description=models.CharField(max_length=250)
    release_date=models.DateTimeField()
    
    capsule=models.ForeignKey(Capsule,related_name='modules', on_delete=CASCADE)
    
class File(models.Model):
    url=models.URLField()
    size=models.DecimalField(null=True,max_digits=7, decimal_places=2)
    type=models.CharField(max_length=1,choices=(('F','FILE'),('I','IMAGE')))
    remote_name=models.CharField(max_length=150)
    local_name=models.CharField(max_length=150)
    module=models.ForeignKey(Module, related_name='files', on_delete=CASCADE)
    
