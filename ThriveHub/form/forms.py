from django import forms
from .models import Caller, CallSession, MHealthData, ReferralContact, Patient, Representative


class AddCall(forms.ModelForm):
    class Meta:
        model = Caller
        fields = [
            'callerName', 'gender', 'civilStatus', 'age', 'location',
            'infoSource', 'reason', 'intervention', 'riskAssessment',
        ]
        widgets = {
            'callerName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Caller Name'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Select Gender')] + Caller.GENDER_CHOICES),
            'civilStatus': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Select Civil Status')] + Caller.STATUS_CHOICES),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Age', 'min': 1}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Location'}),
            'infoSource': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Select Information Source')] + Caller.SOURCE_CHOICES),
            'reason': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Select Reason')] + Caller.REASON_CHOICES),
            'intervention': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Select Intervention')] + Caller.INTERVENTION_CHOICES),
            'riskAssessment': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Select Risk Assessment')] + Caller.RISK_CHOICES),
        }


class AddCallSession(forms.ModelForm):
    class Meta:
        model = CallSession
        fields = ['startTime', 'endTime', 'outcome', 'notes']
        widgets = {
            'startTime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'endTime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'outcome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Outcome'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter Notes'}),
        }


class AddPatientForm(forms.ModelForm):
    name = forms.CharField(
        required=False,  # Make it optional
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Patient Name'})
    )

    class Meta:
        model = Patient
        fields = ['name']


class AddRepresentativeForm(forms.ModelForm):
    organization = forms.CharField(
        required=False,  # Make it optional
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Organization'})
    )

    patientRelationship = forms.CharField(
        required=False,  # Make it optional
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Relationship'})
    )

    class Meta:
        model = Representative
        fields = ['organization', 'patientRelationship']


class AddMHealthData(forms.ModelForm):
    class Meta:
        model = MHealthData
        fields = ['crisisType',
                  'suicidalityRisk',
                  'selfHarmingMethod']
        widgets = {
            'crisisType': forms.Select(attrs={'class': 'form-control'}),
            'suicidalityRisk': forms.Select(attrs={'class': 'form-control'}),
            'selfHarmingMethod': forms.Select(attrs={'class': 'form-control'})
        }


class ReferralContactForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')])
    location = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15, required=False)
    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['location'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = ReferralContact
        fields = ['name', 'gender', 'location', 'phone', 'email']
