from django.contrib import admin

from .models import DailyWord, ProWord


@admin.register(DailyWord)
class DailyWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'user_openid', 'created_at')
    search_fields = ('word', 'translation', 'user_openid')


@admin.register(ProWord)
class ProWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation_with_pos', 'user_openid', 'created_at')
    search_fields = ('word', 'translation_with_pos', 'user_openid')
