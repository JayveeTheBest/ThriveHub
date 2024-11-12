from django.contrib import admin
from .models import Caller, CallSession

# Register your models here.
admin.site.register(Caller)
admin.site.register(CallSession)