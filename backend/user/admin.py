from django.contrib import admin

from . import models


@admin.register(models.CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    ordering = ('email', )
    empty_value_display = '-пусто-'
