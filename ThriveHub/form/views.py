from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now
from django.core.paginator import Paginator
from .models import Caller, CallSession, AITranscript, Patient, Representative
from .forms import AddCall, AddCallSession, AddPatientForm, AddRepresentativeForm
from groq import Groq
from .config import GROQ_API_KEY
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
import openpyxl
from django.http import HttpResponse


# Create your views here.


@login_required()
def callReports(request):
    # Get the current year's last two digits
    current_year = datetime.now().year % 100  # e.g., 2024 -> 24

    # Get the last sessionID for the current year
    last_session = CallSession.objects.filter(callDate__year=datetime.now().year).aggregate(Max('sessionID'))
    last_session_id = last_session['sessionID__max']

    if last_session_id:
        # Increment the last sessionID
        next_session_id = last_session_id + 1
    else:
        # If no sessions exist for the current year, start from 1
        next_session_id = 1

    # Format the sessionID for display
    formatted_session_id = f'TPCB{current_year}-{next_session_id:04}'
    caller = Caller.objects.all()
    if request.user.is_staff or request.user.is_superuser:
        # Admin can see all call sessions
        callSession = CallSession.objects.all().select_related('caller').prefetch_related('transcript')
    else:
        # Regular users can only see their own call sessions
        callSession = CallSession.objects.filter(responder=request.user).select_related('caller').prefetch_related('transcript')
    for session in callSession:
        # Combine with an arbitrary date to calculate the duration
        start_datetime = datetime.combine(datetime.today(), session.startTime)
        end_datetime = datetime.combine(datetime.today(), session.endTime)

        # Adjust for overnight calls
        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)

        # Calculate duration
        session.duration = end_datetime - start_datetime

        # Pagination: Show 10 records per page
        paginator = Paginator(callSession, 10)  # Adjust page size if needed
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    return render(request, 'form/call_report.html', {
        'caller': caller,
        'callSession': page_obj})


@login_required
def exportCallReports(request):
    callSession = CallSession.objects.all().select_related('caller')

    # Apply filters from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    responder = request.GET.get('responder')
    reason = request.GET.get('reason')

    if start_date:
        callSession = callSession.filter(callDate__gte=parse_date(start_date))

    if end_date:
        callSession = callSession.filter(callDate__lte=parse_date(end_date))

    if responder:
        callSession = callSession.filter(responder__username=responder)

    if reason:
        callSession = callSession.filter(caller__reason=reason)

    # Create an Excel workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Summary of Information"

    # Define column headers
    headers = ["Session ID", "Call Duration", "Caller Name", "Gender", "Civil Status", "Age", "Location", "Info Source", "Reason", "Intervention", "Risk Assessment", "Responder"]
    ws.append(headers)

    # Populate data
    for session in callSession:
        start_datetime = datetime.combine(datetime.today(), session.startTime)
        end_datetime = datetime.combine(datetime.today(), session.endTime)
        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)

        duration = end_datetime - start_datetime
        ws.append([
            f"TPCB24-00{session.sessionID}",
            str(duration),
            session.caller.callerName,
            session.caller.gender,
            session.caller.civilStatus,
            session.caller.age,
            session.caller.location,
            session.caller.infoSource,
            session.caller.reason,
            session.caller.intervention,
            session.caller.riskAssessment,
            session.responder.username
        ])

    # Prepare response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=CallReports.xlsx'
    wb.save(response)
    return response


def addCall(request):
    current_year = datetime.now().year % 100  # Get the last two digits of the year

    # Get the last session ID of the current year
    last_session = CallSession.objects.filter(callDate__year=datetime.now().year).aggregate(Max('sessionID'))
    last_session_id = last_session['sessionID__max']

    # Generate the next session ID
    next_session_id = last_session_id + 1 if last_session_id else 1
    formatted_session_id = f'TPCB{current_year}-{next_session_id:04}'

    if request.method == 'POST':
        caller_form = AddCall(request.POST)
        session_form = AddCallSession(request.POST)
        patient_form = AddPatientForm(request.POST)
        representative_form = AddRepresentativeForm(request.POST)

        if (
            caller_form.is_valid()
            and session_form.is_valid()
            and patient_form.is_valid()
            and representative_form.is_valid()
        ):
            try:
                caller = caller_form.save()

                # Save Patient
                patient = patient_form.save()

                # Save Representative (ensure the Representative model has a `patient` field)
                representative = representative_form.save(commit=False)
                representative.patient = patient
                representative.save()

                # Save Call Session
                session = session_form.save(commit=False)
                session.caller = caller
                session.sessionID = next_session_id
                session.responder = request.user
                session.save()

                # Generate summary using Groq API
                chat_completion_text = generate_summary_with_groq(caller, session)

                # Save AI-generated summary
                AITranscript.objects.create(
                    call_session=session,
                    transcriptSummary=chat_completion_text,
                    generatedTimestamp=now()
                )

                messages.success(request, "Call successfully logged and summary generated.")
                return redirect('SummaryPage', session_id=session.sessionID)

            except Exception as e:
                print(f"Error while saving call or generating summary: {e}")
                messages.error(request, "An error occurred. Please try again.")

        else:
            print("Caller Form Errors:", caller_form.errors)
            print("Session Form Errors:", session_form.errors)
            print("Patient Form Errors:", patient_form.errors)
            print("Representative Form Errors:", representative_form.errors)
            messages.error(request, "Please correct the errors in the form.")

    else:
        caller_form = AddCall()
        session_form = AddCallSession(initial={'startTime': datetime.now().strftime('%H:%M')})
        patient_form = AddPatientForm()
        representative_form = AddRepresentativeForm()

    context = {
        'caller_form': caller_form,
        'session_form': session_form,
        'patient_form': patient_form,
        'representative_form': representative_form,
        'formatted_session_id': formatted_session_id,
    }
    return render(request, 'form/call_new.html', context)


def generate_summary_with_groq(caller, session, patient=None, representative=None):
    try:
        # Debug: Print variable types
        print(
            f"caller: {type(caller)}, session: {type(session)}, patient: {type(patient)}, representative: {type(representative)}")

        # Ensure required objects are not None
        if caller is None:
            raise ValueError("Caller object is None")
        if session is None:
            raise ValueError("Session object is None")
        if patient is None:
            print("Warning: Patient object is None")
        if representative is None:
            print("Warning: Representative object is None")

        # Construct the prompt
        prompt = (
            f"You are a professional mental health helpline responder tasked with generating a concise, "
            f"well-structured call report summary. Using only the details provided below, craft the summary in a "
            f"coherent paragraph without introducing additional information or assumptions. Do not include a "
            f"breakdown or list of the details unless explicitly requested. Focus on presenting the information in a "
            f"natural and narrative style:\n"
            f"Caller Name: {caller.callerName}\n"
            f"Gender: {caller.gender}\n"
            f"Civil Status: {caller.civilStatus}\n"
            f"Age: {caller.age}\n"
            f"Location: {caller.location}\n"
            f"Information Source: {caller.infoSource}\n"
            f"Reason for Calling: {caller.reason}\n"
            f"Intervention: {caller.intervention}\n"
            f"Risk Assessment: {caller.riskAssessment}\n\n"
            f"Session Start Time: {session.startTime}\n"
            f"Session End Time: {session.endTime}\n"
            f"Outcome: {session.outcome}\n"
            f"Additional Notes: {session.notes}\n"
        )

        # Include Patient details only if available
        if patient:
            prompt += (
                f"Patient Name: {patient.name}\n"
            )

        # Include Representative details only if available
        if representative:
            prompt += (
                f"Representative's Organization: {representative.organization}\n"
                f"Relationship to the Patient: {representative.patientRelationship}\n"
            )

        prompt += (
            f"Intervention: {caller.intervention}\n"
            f"Risk Assessment: {caller.riskAssessment}\n\n"
            f"Session Start Time: {session.startTime}\n"
            f"Session End Time: {session.endTime}\n"
            f"Outcome: {session.outcome}\n"
            f"Additional Notes: {session.notes}\n"
            f"Ensure the summary is clear, professional, and free from extraneous content. No need to include Session "
            f"Start Time, Session Date, or anything related to call date and time, and the phrase 'Here is a concise "
            f"and well-structured call report summary'."
        )

        print("Generated Prompt:")
        print(prompt)

        # API call
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        print("API Response:", response)
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error generating summary from Groq API: {type(e).__name__} - {e}")
        return "Error: Unable to generate summary at this time."


def summaryPage(request, session_id):
    # Retrieve the CallSession and associated AITranscript
    session = get_object_or_404(CallSession, sessionID=session_id)
    transcript = getattr(session, 'transcript', None)  # Safely access the related transcript

    if not transcript:
        messages.error(request, "No transcript found for this session.")
        return redirect('AddCall')  # Redirect to the addCall page if no transcript exists

    # Handle form submission for editing the summary
    if request.method == 'POST':
        edited_summary = request.POST.get('edited_summary')

        if edited_summary:
            # Save the edited summary only if it differs from the current summary
            if edited_summary.strip() != transcript.transcriptSummary.strip():
                transcript.transcriptSummary = edited_summary
                transcript.generatedTimestamp = now()  # Update the timestamp
                transcript.save()

                messages.success(request, "Transcript summary updated successfully.")
            else:
                messages.info(request, "No changes were made to the transcript summary.")

        else:
            messages.error(request, "Summary cannot be empty.")

        return redirect('SummaryPage', session_id=session_id)  # Redirect to refresh the page

    # Render the summary page with the current summary
    context = {
        'session': session,
        'summary': transcript.transcriptSummary,
    }
    return render(request, 'form/call_summary.html', context)
