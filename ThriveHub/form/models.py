from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.timezone import now
from  django.conf import settings


# Create your models here.


class Responder(AbstractUser):
    responderID = models.AutoField(primary_key=True)
    mfa_secret = models.CharField(max_length=16, blank=True, null=True)
    mfa_enabled = models.BooleanField(default=False)
    responderName = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    shift = models.CharField(max_length=255)
    password = models.CharField(default="password")
    username = models.CharField(max_length=150, unique=True, default="Responder")

    def __str__(self):
        return self.username


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
        ('Colleague', 'Colleague'),
        ('Family/Friends/Relationships', 'Family/Friends/Relationships'),
        ('Government Offices', 'Government Offices'),
        ('Media', 'Media'),
        ('Medical Professionals', 'Medical Professionals'),
        ('N/A and Refused', 'N/A and Refused'),
        ("NGO's and other Organizations", "NGO's and other Organizations"),
        ('Online', 'Online'),
        ('Other Hotlines', 'Other Hotlines'),
        ('Private Offices/Hospitals', 'Private Offices/Hospitals'),
        ('Referral', 'Referral'),
        ('Repeat Caller', 'Repeat Caller'),
        ('School Personnels', 'School Personnels'),
        ('Seminars/IEC Materials', 'Seminars/IEC Materials'),
    ]

    REASON_CHOICES = [
        ('Abortion', 'Abortion'),
        ('Academic Problem', 'Academic Problem'),
        ('Acute Stress Disorder', 'Acute Stress Disorder'),
        ('ADHD', 'ADHD'),
        ('Alcohol Dependence', 'Alcohol Dependence'),
        ('Anger Management Issue', 'Anger Management Issue'),
        ('Anxiety', 'Anxiety'),
        ('Bipolar and OCD', 'Bipolar and OCD'),
        ('Bullying', 'Bullying'),
        ('Calling for Another Person', 'Calling for Another Person'),
        ('Current Social Issue', 'Current Social Issue'),
        ('Cyberbullying', 'Cyberbullying'),
        ('Depression', 'Depression'),
        ('Domestic Abuse', 'Domestic Abuse'),
        ('Drug Addiction', 'Drug Addiction'),
        ('Emotional Crisis', 'Emotional Crisis'),
        ('Family Problem', 'Family Problem'),
        ('Feelings of Sadness and Loneliness', 'Feelings of Sadness and Loneliness'),
        ('Financial Problem', 'Financial Problem'),
        ('Gambling Problem', 'Gambling Problem'),
        ('Global Developmental Delay', 'Global Developmental Delay'),
        ('Grief', 'Grief'),
        ('Indentity Confusion', 'Indentity Confusion'),
        ('Inquiry', 'Inquiry'),
        ('Interpersonal Conflict', 'Interpersonal Conflict'),
        ('Intimacy Problems', 'Intimacy Problems'),
        ('Legal Advice', 'Legal Advice'),
        ('Marital Problem', 'Marital Problem'),
        ('Medication Concern', 'Medication Concern'),
        ('Mental Health', 'Mental Health'),
        ('Needed Referral', 'Needed Referral'),
        ('Other', 'Other'),
        ('Panic Attack', 'Panic Attack'),
        ('Physical Abuse', 'Physical Abuse'),
        ('Postpartum Depression', 'Postpartum Depression'),
        ('Psychiatric Emergency', 'Psychiatric Emergency'),
        ('Psychosomatic Pain', 'Psychosomatic Pain'),
        ('PTSD', 'PTSD'),
        ('Rape', 'Rape'),
        ('Relationship Problem', 'Relationship Problem'),
        ('Schizophrenia', 'Schizophrenia'),
        ('School', 'School'),
        ('Self-harming and Suicidal Attempt/Crisis', 'Self-harming and Suicidal Attempt/Crisis'),
        ('Sexual Harassment and Sexual Abuse', 'Sexual Harassment and Sexual Abuse'),
        ('Suicidal Crisis', 'Suicidal Crisis'),
        ('Suicidal Ideation', 'Suicidal Ideation'),
        ('Symptoms of Insomnia', 'Symptoms of Insomnia'),
        ('Trauma', 'Trauma'),
        ('Work Problem', 'Work Problem'),
    ]

    INTERVENTION_CHOICES = [
        ('Breathing Technique', 'Breathing Technique'),
        ('Empathetic Listening', 'Empathetic Listening'),
        ('Empty Chair Technique', 'Empty Chair Technique'),
        ('PsychEducation', 'PsychEducation'),
        ('Referred to a Mental Health Professional', 'Referred to a Mental Health Professional'),
        ('Referred to the Authority', 'Referred to the Authority'),
        ('Referred to the nearest Emergency Unit', 'Referred to the nearest Emergency Unit'),
        ('Safety Planning', 'Safety Planning'),
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
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='call_sessions', default=1)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='drafts')
    form_data = models.JSONField()  # Stores form data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft for {self.user.username} at {self.created_at}"