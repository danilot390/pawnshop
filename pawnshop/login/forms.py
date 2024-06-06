from django import forms
from loan.models import User, Person

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['ci', 'name', 'last_name', 'address', 'phone_number']

class NewUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','password']

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = []

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['autocomplete'] = 'New password'
        self.fields['password'].help_text = "May you leave it blank, if you don't want to change the password."