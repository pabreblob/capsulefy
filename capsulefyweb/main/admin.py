from django.contrib import admin
from .models import Capsule, Actor, User, Admin, Social_network, Module, File
# Register your models here.
admin.site.register(Social_network)
admin.site.register(Capsule)
admin.site.register(Module)
admin.site.register(File)
admin.site.register(User)
admin.site.register(Admin)
