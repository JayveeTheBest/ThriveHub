from django.db import models

# Create your models here.


class Caller(models.Model):
    callerID = models.AutoField(primary_key=True)
    callerName = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    civilStatus = models.CharField(max_length=255, null=True, blank=True)
    infoSource = models.CharField(max_length=255, null=True, blank=True)
    callerType = models.CharField(max_length=255)

    def __str__(self):
        return self.callerName


class CallSession(models.Model):
    sessionID = models.AutoField(primary_key=True)
    caller = models.ForeignKey(Caller, on_delete=models.CASCADE, related_name='sessions')
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
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


class Responder(models.Model):
    responderID = models.AutoField(primary_key=True)
    responderName = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    shift = models.CharField(max_length=255)

    def __str__(self):
        return self.responderName


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


class Patient(models.Model):
    patientID = models.AutoField(primary_key=True)


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