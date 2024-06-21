from django import forms
from loan.models import RechargePersonalBox, Box

class RechargeBoxForm(forms.ModelForm):
    class Meta:
        model = RechargePersonalBox
        fields = ['receiver',]
        
class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ['description', 'amount'] 
