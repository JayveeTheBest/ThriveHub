from django.shortcuts import render
from .models import Caller, CallSession

# Create your views here.


def form(request):
    form = Caller.objects.all()
    return render(request, 'form/form.html', {'form': form})


def callReports(request):
    caller = Caller.objects.all()
    callSession = CallSession.objects.all()

    return render(request, 'form/call_report.html', {
        'caller': caller,
        'callSession': callSession})