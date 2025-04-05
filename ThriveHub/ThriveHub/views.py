import base64
import io
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, F, Q
import json
from django.db.models.functions import TruncMonth, TruncYear
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from form.models import ReferralContact, Caller, CallSession, Responder
from form.forms import ReferralContactForm
from django.core.paginator import Paginator
import pyotp
import qrcode


@login_required(login_url="/responder/login")
def dashboard(request):
    # Get all months with available data grouped by year
    available_months = (
        CallSession.objects
        .annotate(
            year=TruncYear('callDate'),
            month=TruncMonth('callDate')
        )
        .values('year', 'month')
        .annotate(call_count=Count('sessionID'))
        .order_by('year', 'month')
    )

    # Create a dictionary mapping years to their available months
    months_by_year = defaultdict(list)
    for item in available_months:
        year = item['year'].year if item['year'] else None
        month = item['month'].month if item['month'] else None
        if year and month:
            months_by_year[year].append(month)

    # Get reasons per month
    reasons_data = (
        Caller.objects
        .annotate(
            year=TruncYear('sessions__callDate'),
            month=TruncMonth('sessions__callDate')
        )
        .values('year', 'month', 'reason')
        .annotate(count=Count('reason'))
        .order_by('year', 'month')
    )

    reasons_per_month = [
        {
            'year': item['year'].year if item['year'] else None,  # Convert to integer
            'month': item['month'].month if item['month'] else None,  # Convert to integer
            'reason': item['reason'],
            'count': item['count']
        }
        for item in reasons_data
    ]

    gender_data = (
        Caller.objects
        .annotate(
            year=TruncYear('sessions__callDate'),
            month=TruncMonth('sessions__callDate')
        )
        .values('year', 'month', 'gender')
        .annotate(count=Count('gender'))
        .order_by('year', 'month')
    )

    gender_per_month = [
        {
            'year': item['year'].year if item['year'] else None,  # Convert to integer
            'month': item['month'].month if item['month'] else None,  # Convert to integer
            'gender': item['gender'],
            'count': item['count']
        }
        for item in gender_data
    ]

    risk_data = (
        Caller.objects
        .annotate(
            year=TruncYear('sessions__callDate'),
            month=TruncMonth('sessions__callDate')
        )
        .values('year', 'month', 'riskAssessment')
        .annotate(count=Count('riskAssessment'))
        .order_by('year', 'month')
    )

    risk_per_month = [
        {
            'year': item['year'].year if item['year'] else None,  # Convert to integer
            'month': item['month'].month if item['month'] else None,  # Convert to integer
            'risk': item['riskAssessment'],
            'count': item['count']
        }
        for item in risk_data
    ]

    # Group calls by month and year
    monthly_calls = (
        CallSession.objects
        .annotate(
            year=TruncYear('callDate'),
            month=TruncMonth('callDate')
        )
        .values('year', 'month')
        .annotate(call_count=Count('sessionID'))
        .order_by('year', 'month')
    )

    calls_data = [
        {
            'year': str(item['year'].year) if item['year'] else None,  # Convert to string
            'month': str(item['month'].month) if item['month'] else None,  # Convert to string
            'call_count': item['call_count']
        }
        for item in monthly_calls
    ]

    # print("\n===== DEBUG OUTPUT =====")
    # print("Reasons Data:", json.dumps(reasons_per_month, indent=2))
    # print("Gender Data:", json.dumps(gender_per_month, indent=2))
    # print("Risk Data:", json.dumps(risk_per_month, indent=2))
    # print("Monthly Calls Data:", json.dumps(calls_data, indent=2))
    # print("========================\n")
    # print("Months by Year:", json.dumps(months_by_year, indent=2))
    # Convert to JSON for safe rendering in template
    context = {
        'reasons_per_month': json.dumps(reasons_per_month),
        'gender_per_month': json.dumps(gender_per_month),
        'risk_per_month': json.dumps(risk_per_month),
        'calls_per_month': json.dumps(calls_data),
        'months_by_year': json.dumps(months_by_year),
    }

    return render(request, 'dashboard.html', context)


@login_required(login_url="/responder/login")
def reports(request):
    return render(request, 'reports.html')


@login_required(login_url="/responder/login")
def referrals(request):
    query = request.GET.get('query', '')
    referralSearch = ReferralContact.objects.all()

    if query:
        referralSearch = referralSearch.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(gender__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    return render(request, 'referrals.html', {'referrals': referralSearch})


@login_required
def settings(request):
    user = request.user
    if not user.mfa_secret:
        user.mfa_secret = pyotp.random_base32()
        user.save()

    otp_uri = pyotp.totp.TOTP(user.mfa_secret).provisioning_uri(
        name=user.email,
        issuer_name="ThriveHub"
    )

    qr = qrcode.make(otp_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    buffer.seek(0)
    qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")

    qr_code_data_uri = f"data:image/png;base64,{qr_code}"

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Update user details
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, "Your profile has been updated successfully.")
        return render(request, 'settings.html', {"qrcode": qr_code_data_uri, 'user': user})  # Redirect to settings after saving

    return render(request, 'settings.html', {"qrcode": qr_code_data_uri, 'user': user})


def verify_2fa_otp(user, otp ):
    totp = pyotp.TOTP(user.mfa_secret)
    if totp.verify(otp):
        user.mfa_enabled = True
        user.save()
        return True
    return False


def verify_mfa(request):
    if request.method == 'POST':
        if request.method == 'POST':
            # Retrieve OTP code from individual input fields
            otp = ''.join([
                request.POST.get('otp_code_1', ''),
                request.POST.get('otp_code_2', ''),
                request.POST.get('otp_code_3', ''),
                request.POST.get('otp_code_4', ''),
                request.POST.get('otp_code_5', ''),
                request.POST.get('otp_code_6', ''),
            ])
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, 'Invalid Responder ID. Please try again.')
            return render(request, 'otp_verify.html', {'user_id': user_id})

        user = Responder.objects.get(responderID=user_id)
        if verify_2fa_otp(user, otp):
            if request.user.is_authenticated:
                messages.success(request, 'Two-Factor Authentication enabled successfully !')
                return redirect('settings')

            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            if request.user.is_authenticated:
                messages.error(request, 'Invalid OTP code. Please try again.')
                return redirect('settings')
            messages.error(request, 'Invalid OTP code. Please try again.')
            return render(request, 'otp_verify.html', {'user_id': user_id})

    return render(request, 'otp_verify.html', {'user_id': user_id})


@login_required
def disable_2fa(request):
    user = request.user
    if user.mfa_enabled:
        user.mfa_enabled = False
        user.save()
        messages.success(request, "Two-Factor Authentication has been disabled.")
        return redirect('settings')
    else:
        messages.info(request, "2FA is already disabled.")
    return redirect('settings')

@login_required
def referrals(request):
    search_query = request.GET.get('search', '')
    filter_gender = request.GET.get('gender', 'All')
    filter_location = request.GET.get('location', '')

    contacts = ReferralContact.objects.all()

    if search_query:
        contacts = contacts.filter(name__icontains=search_query)

    if filter_gender != 'All':
        contacts = contacts.filter(gender=filter_gender)

    if filter_location:
        contacts = contacts.filter(location__icontains=filter_location)

    return render(request, 'referrals.html', {'contacts': contacts})


def add_referral(request):
    if request.method == 'POST':
        form = ReferralContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('referrals')
    else:
        form = ReferralContactForm()
    return render(request, 'referral_new.html', {'form': form})


def edit_referral(request, pk):
    contact = get_object_or_404(ReferralContact, pk=pk)
    if request.method == 'POST':
        form = ReferralContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('referrals')
    else:
        form = ReferralContactForm(instance=contact)
    return render(request, 'referral_new.html', {'form': form})


def delete_referral(request, pk):
    contact = get_object_or_404(ReferralContact, pk=pk)
    contact.delete()
    return redirect('referrals')


def search_results(request):
    query = request.GET.get('q', '').strip()  # Get the search query
    callers = referrals = []

    if query:
        # Search Callers
        callers = Caller.objects.filter(
            Q(callerName__icontains=query) | Q(location__icontains=query)
        )
        print(f"Search Query: {query}")
        print(f"Caller Results: {callers}")  # Print callers to check if any results

        # Search Referral Contacts
        referrals = ReferralContact.objects.filter(
            Q(name__icontains=query) | Q(location__icontains=query) |
            Q(phone__icontains=query) | Q(email__icontains=query)
        )
        print(f"Referral Results: {referrals}")  # Print referrals to check if any results

    # Combine results for pagination
    results = list(callers) + list(referrals)
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search_results.html', {
        'query': query,
        'callers': callers,
        'referrals': referrals,
        'page_obj': page_obj
    })


def caller_detail(request, callerID):
    caller = get_object_or_404(Caller, callerID=callerID)

    # Fetch all call sessions related to this caller
    call_sessions = CallSession.objects.filter(caller=caller).prefetch_related('transcript').order_by('-callDate')

    context = {
        'caller': caller,
        'call_sessions': call_sessions, }

    return render(request, 'caller_detail.html', context)


def referral_detail(request, id):
    referral = get_object_or_404(ReferralContact, id=id)
    return render(request, 'referral_detail.html', {'referral': referral})