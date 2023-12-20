# forms.py
from django import forms
from .models import Address
from django.core.exceptions import ValidationError
import re

# class AddressForm(forms.ModelForm):
#     name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     pincode = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     locality = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     city = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     state = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
#     class Meta:
#         model = Address
#         fields = ['name', 'phone', 'pincode', 'locality', 'address', 'city', 'state']
        
#     def clean_phone(self):  
#         phone = self.cleaned_data.get('phone')
#         if not re.match(r'^[6-9]\d{9}$', phone):  # Indian mobile number format
#             raise forms.ValidationError('Invalid phone number format. Example: 9876543210')
#         return phone

#     def clean_pincode(self):
#         pincode = self.cleaned_data.get('pincode')
#         if not re.match(r'^\d{6}$', pincode):
#             raise forms.ValidationError('Invalid pincode format. Example: 123456')
#         return pincode