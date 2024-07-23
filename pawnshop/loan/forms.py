from django import forms
from loan.models import Pledge, Person, OtherContract, VehicleInspection, BlackList
from django.utils import timezone

from datetime import timedelta

class PledgeForm(forms.ModelForm):
    class Meta:
        model = Pledge
        fields = [
            'article',
            'type',
            'description',
            'loan_date',
            'rescue_date',
            'loan',
            'interest',
            'estimated_value',
            'image',
        ]
        widgets = {
            'article': forms.TextInput(attrs={
                'class' : 'form-control col-md-7',
                'required': 'required',
            }),
            'type': forms.Select(choices=[
                ('vehicles', 'Vehicles'),
                ('others', 'Others')
            ], attrs={
                'class' : 'form-control col-md-7',
                'required': 'required',
            }),
            'description': forms.TextInput(attrs={
                'class' : 'form-control col-md-7',
                'required': 'required',
            }),
            'loan_date': forms.DateInput(attrs={
                'class' : 'form-control col-md-7',
                'required': 'required',
                'type' : 'date',
            }),
            'rescue_date': forms.DateInput(attrs={
                'class' : 'form-control col-md-7',
                'required': 'required',
                'type' : 'date'
            }),
            'loan': forms.NumberInput(attrs={
                'class' : 'form-control col-md-7',
                'required': 'required',
            }),
            'interest': forms.NumberInput(attrs={
                'class' : 'form-control col-md-7',
                'required': 'required',
            }),
            'estimated_value': forms.NumberInput(attrs={
                'class' : 'form-control col-md-7',
                'required': 'required',
            }),
            'image' : forms.ClearableFileInput(attrs={
                'class' : 'form-control col-md-7',
                'required': False,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_day = timezone.now().date()
        one_moth_later = current_day + timedelta(days=31)

        # Set initial values for loan_date and rescue_date
        self.fields['loan_date'].initial = current_day
        self.fields['rescue_date'].initial =  one_moth_later
        self.fields['interest'].initial = 10


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            'ci',
            'name',
            'last_name',
            'address',
            'phone_number',
        ]
        widgets = {
            'ci' : forms.TextInput(attrs={
                'class' : 'form-control',
                'required' : 'required',
            }),
            'name' : forms.TextInput(attrs={
                'class' : 'form-control',
                'required' : 'required',
            }),
            'last_name' : forms.TextInput(attrs={
                'class' : 'form-control',
                'required' : 'required',
            }),
            'address' : forms.TextInput(attrs={
                'class' : 'form-control',
                'required' : 'required',
            }),
            'phone_number' : forms.NumberInput(attrs={
                'class' : 'form-control',
                'required' : 'required',
            }),
        }
        
class PersonFormWithLoan(PersonForm):
    go_loan = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-control col-md-7',
            'placeholder': 'Extra field'
        })
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set initial values for loan_date and rescue_date
        #ßßßself.fields['ci'].initial = 'asd'
    def clean_go_loan(self):
        data = self.cleaned_data['go_loan']
        # Add your validation logic here
        if not data:
            raise forms.ValidationError("This field is required.")
        return data

class OtherContractForm(forms.ModelForm):
     class Meta:
        model = OtherContract
        fields = [
            'currency',
            'initial_date',
            'end_date',
        ]
        widgets = {
            'currency': forms.TextInput(attrs={
                'class': 'form-control col-md-7',
                'required': 'required',
            }),
            'initial_date': forms.DateInput(attrs={
                'class': 'form-control col-md-7',
                'required': 'required',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control col-md-7',
                'required': 'required',
            }),
        }

class VehicleInspectionForm(forms.ModelForm):
    class Meta:
        model = VehicleInspection
        fields = [
            'plate',
            'crpva',
            'clase',
            'color',
            'model',
            'marca',
            'type',
            'chassis',
            'motor',
            'motor_status',
            'bodywork_status',
            'taxes',
            'infractions',
        ]
        widgets={
            'plate':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required'
            }),
            'crpva':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required',
            }),
            'clase':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required',
            }),
            'color':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required',
            }),
            'model':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required',
            }),
            'marca':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required',
            }),
            'type':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required',
            }),
            'chassis':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required'
            }),
            'motor':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required'
            }),
            'motor_status':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required'
            }),
            'bodywork_status':forms.TextInput(attrs={
                'class':'form-control col-md-7',
                'required':'required'
            }),
            'taxes':forms.NumberInput(attrs={
                'class':'form-control col-md-7',
                'required':'required'
            }),
            'infractions':forms.NumberInput(attrs={
                'class':'form-control col-md-7',
                'required':'required'
            }),
        }

class BlackListForm(forms.ModelForm):
    
    client = forms.ModelChoiceField(queryset=Person.objects.none(), empty_label="Select a person")

    class Meta:
        model = BlackList
        fields = [
            'client',
            'reason',
        ]
        widgets ={
            'client': forms.Select(attrs={
                'class': 'form-control col-md-7',
                'required': 'required',
            }),
            'reason': forms.Textarea(attrs={
                'class':'form-control col-md-7',
                'required':'required',
                'placeholder': 'Reason for Blacklisting',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        people_queryset = kwargs.pop('people_queryset', None)
        super().__init__(*args, **kwargs)
        if people_queryset is not None:
            self.fields['client'].queryset = people_queryset