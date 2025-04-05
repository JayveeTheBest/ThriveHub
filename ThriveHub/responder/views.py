import io
import base64
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm
from django.contrib import messages


# Create your views here.
def registration(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('settings')
    else:
        form = CustomUserCreationForm()
    return render(request, "responder/registration.html", {"form": form})


def responder_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if user.mfa_enabled:
                request.session['pre_auth_user_id'] = user.responderID
                return render(request, 'otp_verify.html', {'user_id': user.responderID})

            # If MFA is not enabled, log in directly
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('settings')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, "responder/login.html", {"form": form})


def responder_logout(request):
    logout(request)
    return redirect('responder:login')