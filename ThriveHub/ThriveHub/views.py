from django.shortcuts import render


def dashboard(request):
    return render(request, 'dashboard.html')


def reports(request):
    return render(request,'reports.html')


def referrals(request):
    return render(request, 'referrals.html')
