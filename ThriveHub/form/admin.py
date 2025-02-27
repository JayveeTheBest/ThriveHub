from django.contrib import admin
from .models import Caller, CallSession, AITranscript, ReferralContact, Patient, Representative

# Register your models here.
admin.site.register(Caller)
admin.site.register(Patient)
admin.site.register(Representative)
admin.site.register(CallSession)
admin.site.register(AITranscript)
admin.site.register(ReferralContact)