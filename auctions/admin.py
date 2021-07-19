from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Categorie)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)