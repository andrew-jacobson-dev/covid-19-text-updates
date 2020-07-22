from django.contrib import admin
from .models import DailyCountyKnownCases, DailyCountyDeaths

# Register your models here.
admin.site.register(DailyCountyKnownCases)
admin.site.register(DailyCountyDeaths)