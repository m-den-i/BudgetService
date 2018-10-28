from django.contrib import admin

from django.contrib.admin.models import LogEntry

from budget_auth.models import User

admin.site.register(User)
admin.site.register(LogEntry)
