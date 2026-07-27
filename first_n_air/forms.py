from django import forms
from .models import *
# from django import treaties
from django.contrib.auth.models import User

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control rounded-0 border-secondary-subtle'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control rounded-0 border-secondary-subtle'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control rounded-0 border-secondary-subtle'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded-0 border-secondary-subtle'}),
        }

class ChoicesForm(forms.ModelForm):
    class Meta:
        model=Buy
        exclude = ['product']
        fields = '__all__'
    
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Register
        fields = '__all__'
        exclode = ['message']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Register
        fields = '__all__'
        exclude = ['password','last_name','phone']