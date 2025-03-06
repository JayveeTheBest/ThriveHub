from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# Create your models here.


class Responder(models.Model):
    responderID = models.AutoField(primary_key=True)
    responderName = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    shift = models.CharField(max_length=255)

    def __str__(self):
        return self.responderName


class Caller(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('LGBTQ++', 'LGBTQ++'),
        ('N/A', 'N/A'),
    ]

    STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Single (Living in)', 'Single (Living in)'),
        ('Married', 'Married'),
        ('Separated', 'Separated'),
        ('Widowed', 'Widowed'),
        ('N/A', 'N/A'),
    ]

    SOURCE_CHOICES = [
        ('Online', 'Online'),
        ('Media', 'Media'),
        ('Family/Friend', 'Family/Friend'),
        ('Colleague', 'Colleague'),
        ('Referral', 'Referral'),
    ]

    REASON_CHOICES = [
        ('Mental Health', 'Mental Health'),
        ('Marital', 'Marital'),
        ('School', 'School'),
        ('Financial', 'Financial'),
        ('Suicidal Crisis', 'Suicidal Crisis'),
        ('Calling for another person', 'Calling for another person'),
    ]

    INTERVENTION_CHOICES = [
        ('PsychEducation', 'PsychEducation'),
        ('Referral', 'Referral'),
        ('Empathetic Listening', 'Empathetic Listening'),
        ('Breathing Technique', 'Breathing Technique'),
    ]

    RISK_CHOICES = [
        ('Low Risk', 'Low Risk'),
        ('Moderate Risk', 'Moderate Risk'),
        ('High Risk', 'High Risk'),
    ]

    callerID = models.AutoField(primary_key=True)
    callerName = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True, choices=GENDER_CHOICES)
    civilStatus = models.CharField(max_length=255, null=True, blank=True, choices=STATUS_CHOICES, )
    age = models.CharField(max_length=2, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    infoSource = models.CharField(max_length=255, null=True, blank=True, choices=SOURCE_CHOICES)
    reason = models.CharField(max_length=255, null=True, blank=True, choices=REASON_CHOICES)
    intervention = models.CharField(max_length=255, null=True, blank=True, choices=INTERVENTION_CHOICES)
    riskAssessment = models.CharField(max_length=255, null=True, blank=True, choices=RISK_CHOICES)

    patient = models.ForeignKey('Patient', null=True, blank=True, on_delete=models.SET_NULL, related_name='callers')
    representative = models.ForeignKey('Representative', null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name='representative')

    def __str__(self):
        return f"{self.callerID}: {self.callerName}"


class CallSession(models.Model):
    sessionID = models.AutoField(primary_key=True)
    caller = models.ForeignKey(Caller, on_delete=models.CASCADE, related_name='sessions')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='call_sessions', default=1)
    startTime = models.TimeField(null=True, blank=True)
    endTime = models.TimeField(null=True, blank=True)
    callDate = models.DateField(default=now)
    outcome = models.CharField(max_length=255)
    notes = models.TextField()

    def __str__(self):
        return f"{self.sessionID}: {self.caller}"


class MHealthData(models.Model):
    mhealthID = models.AutoField(primary_key=True)
    crisisType = models.CharField(max_length=255)
    suicidalityRisk = models.CharField(max_length=255)
    selfHarmingMethod = models.CharField(max_length=255)
    call_session = models.OneToOneField(CallSession, on_delete=models.CASCADE, related_name='mhealth_data')


class CallerHistory(models.Model):
    callerhistoryID = models.AutoField(primary_key=True)
    endTime = models.DateTimeField()
    notes = models.CharField(max_length=255)
    outcome = models.CharField(max_length=255)
    responder = models.ForeignKey(Responder, on_delete=models.CASCADE)
    mhealthData = models.ForeignKey(MHealthData, on_delete=models.CASCADE)


class AITranscript(models.Model):
    transcriptID = models.AutoField(primary_key=True)
    call_session = models.OneToOneField(CallSession, on_delete=models.CASCADE, related_name='transcript')
    transcriptSummary = models.CharField(max_length=255)
    generatedTimestamp = models.DateTimeField()
    transcriptFeedback = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.transcriptID}: {self.call_session}"


class Patient(models.Model):
    patientID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Representative(models.Model):
    representativeID = models.AutoField(primary_key=True)
    organization = models.CharField(max_length=255)
    patientRelationship = models.CharField(max_length=255)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='representatives')


class Reports(models.Model):
    reportID = models.AutoField(primary_key=True)
    dateGenerated = models.DateField()
    reportType = models.CharField(max_length=255)
    responder = models.ForeignKey(Responder, on_delete=models.CASCADE, related_name='reports')


class ReferralContact(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class Draft(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drafts')
    form_data = models.JSONField()  # Stores form data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft for {self.user.username} at {self.created_at}"