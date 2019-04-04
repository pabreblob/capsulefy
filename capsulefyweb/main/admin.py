from django.contrib import admin
from .models import Capsule, Actor, User, Admin, Social_network, Module, File
from django.contrib.admin.sites import AdminSite
from django import forms
# Register your models here.
class MyAdminSite(AdminSite):
    site_header = 'Capsulefy Admin'
admin_site = MyAdminSite(name='myadmin')

admin_site.register(Social_network)
admin_site.register(Capsule)
admin_site.register(Module)
admin_site.register(File)
  
class UserAdmin(admin.ModelAdmin):
    model=User
    list_display=['username','first_name','last_name',
                  'birthdate','is_active','email_notification']

    list_editable=['is_active',]
    list_display_links = 'username',
    search_fields = ['username','first_name','last_name',
                  'birthdate','email_notification',]
    class Meta:
        labels = {
                'is_active': 'Banned',
            }
    list_per_page = 10
admin_site.register(User, UserAdmin)
admin_site.register(Admin)
