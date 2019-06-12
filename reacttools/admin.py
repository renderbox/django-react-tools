from django.contrib import admin

from reacttools.models import ReactAppSettings

###############
# MODEL ADMINS
###############

class ReactAppSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)

###############
# REGISTRATION
###############

admin.site.register(ReactAppSettings, ReactAppSettingsAdmin)
