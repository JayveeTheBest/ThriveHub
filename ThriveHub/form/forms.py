from django import forms
from .models import Caller, CallSession, MHealthData, ReferralContact


class AddCall(forms.ModelForm):
    class Meta:
        model = Caller
        fields = ['callerName',
                  'gender',
                  'civilStatus',
                  'age',
                  'location',
                  'infoSource',
                  'reason',
                  'intervention',
                  'riskAssessment']
        widgets = {
            'callerName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Caller Name'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'civilStatus': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Age'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Location'}),
            'infoSource': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'intervention': forms.Select(attrs={'class': 'form-control'}),
            'riskAssessment': forms.Select(attrs={'class': 'form-control'})
        }


class AddCallSession(forms.ModelForm):
    class Meta:
        model = CallSession
        fields = ['startTime',
                  'endTime',
                  'outcome',
                  'notes']
        widgets = {
            'startTime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'endTime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'outcome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Outcome'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Notes'}),
        }


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
