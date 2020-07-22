from django.contrib import admin
from .models import State, County, Frequency, Recipient, RecipientSelection

# Register your models here.
admin.site.register(State)
admin.site.register(County)
admin.site.register(Frequency)
admin.site.register(Recipient)
admin.site.register(RecipientSelection)