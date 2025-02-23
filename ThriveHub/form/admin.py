from django.contrib import admin
from .models import Caller, CallSession, AITranscript, ReferralContact

# Register your models here.
admin.site.register(Caller)
admin.site.register(CallSession)
admin.site.register(AITranscript)
admin.site.register(ReferralContact)