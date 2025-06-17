from django.contrib import admin
from .models import Agent, Client, Compte, Credit, Remboursement
from django.contrib.auth.admin import UserAdmin

@admin.register(Agent)
class AgentAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_superuser', 'is_active')
    list_filter = ('role', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Rôle dans le système', {'fields': ('role',)}),
    )

admin.site.register(Client)
admin.site.register(Compte)
admin.site.register(Credit)
admin.site.register(Remboursement)

