from django.contrib import admin
from .models import Credit_card, Capsule, Actor, User, Admin, Social_network, Module, File
# Register your models here.
admin.site.register(Credit_card)
admin.site.register(Social_network)
admin.site.register(Capsule)
admin.site.register(Module)
admin.site.register(File)
admin.site.register(User)
admin.site.register(Admin)
