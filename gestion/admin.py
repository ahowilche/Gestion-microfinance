from django.contrib import admin
from .models import Agent, Client, Compte, Credit, Remboursement
from django.contrib.auth.admin import UserAdmin

admin.site.register(Agent, UserAdmin)
admin.site.register(Client)
admin.site.register(Compte)
admin.site.register(Credit)
admin.site.register(Remboursement)

