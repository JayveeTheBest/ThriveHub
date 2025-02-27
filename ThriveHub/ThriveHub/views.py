from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, F, Q
import calendar, json
from django.db.models.functions import TruncMonth, TruncYear
from django.contrib import messages
from form.models import ReferralContact, Caller, CallSession
from form.forms import ReferralContactForm
from django.core.paginator import Paginator


@login_required(login_url="/responder/login")
def dashboard(request):
    reasons_data = Caller.objects.values('reason').annotate(count=Count('reason'))
    gender_data = Caller.objects.values('gender').annotate(count=Count('gender'))
    risk_data = Caller.objects.values('riskAssessment').annotate(count=Count('riskAssessment'))

    # Group calls by month and year
    monthly_calls = (
        CallSession.objects
        .annotate(
            year=TruncYear('callDate'),  # Group by year
            month=TruncMonth('callDate')  # Group by month
        )
        .values('year', 'month')  # Include both year and month in the grouping
        .annotate(call_count=Count('sessionID'))
        .order_by('year', 'month')  # Order by year and month
    )

    # Prepare data for the bar chart
    calls_data = []
    for item in monthly_calls:
        calls_data.append({
            'year': item['year'].year,  # Extract the year
            'month': item['month'].month,  # Extract the month
            'call_count': item['call_count']  # Extract the call count
        })

    # Convert data to JSON for use in the template
    calls_per_month = json.dumps(calls_data)

    reasons_labels = [item['reason'] for item in reasons_data]
    reasons_counts = [item['count'] for item in reasons_data]
    gender_labels = [item['gender'] for item in gender_data]
    gender_counts = [item['count'] for item in gender_data]
    risk_labels = [item['riskAssessment'] for item in risk_data]
    risk_counts = [item['count'] for item in risk_data]

    print("Reasons Labels:", list(reasons_labels))
    print("Reasons Counts:", list(reasons_counts))
    print("Gender Data:", list(gender_data))
    print("Risk Data:", list(risk_data))
    print("Monthly Calls Data:", calls_per_month)

    # Convert data for charts
    context = {
        'reasons_labels': reasons_labels,
        'reasons_counts': reasons_counts,
        'gender_labels': gender_labels,
        'gender_counts': gender_counts,
        'risk_labels': risk_labels,
        'risk_counts': risk_counts,
        'calls_per_month': calls_per_month,  # Updated data for the bar chart
        'gender_data': list(gender_data),
        'suicide_data': list(risk_data),
        'monthly_calls': list(monthly_calls),
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
        return redirect('settings')  # Redirect to settings after saving

    return render(request, 'settings.html', {'user': user})


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
    return render(request, 'caller_detail.html', {'caller': caller})


def referral_detail(request, id):
    referral = get_object_or_404(ReferralContact, id=id)
    return render(request, 'referral_detail.html', {'referral': referral})