from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    middle_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=True)
    email_address = forms.EmailField(required=True)
    DOB = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    phone_numbers = forms.CharField(max_length=15, required=False)
    gender = forms.CharField(label= 'Gender', widget= forms.RadioSelect(choices=[('Male', 'Male'), ('Female', 'Female')]))
    house = forms.CharField(max_length=25, required=True)
    street_name = forms.CharField(max_length=100, required=True)
    town_city = forms.CharField(max_length=50, required=True)
    county = forms.CharField(max_length=50, required=True)
    postcode = forms.CharField(max_length=10, required=True)
    country = forms.ChoiceField(choices=[('England', 'England'), ('Scotland', 'Scotland')
                                         ,('Wales', 'Wales'), ('Northern Ireland', 'Northern Ireland')], required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    membership = forms.ChoiceField(choices=[('None', 'None'), ('Standard', 'Standard'),
                                            ('Premium','Premium'), ('Student', 'Student')])

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        label="Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'example@example.com'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': '********'})
    )

class UserUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=False)
    middle_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email_address = forms.EmailField(required=False)
    DOB = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    phone_numbers = forms.CharField(max_length=15, required=False)
    gender = forms.CharField(widget=forms.RadioSelect(choices=[('Male', 'Male'), ('Female', 'Female')]), required=False)
    house = forms.CharField(max_length=25, required=False)
    street_name = forms.CharField(max_length=100, required=False)
    town_city = forms.CharField(max_length=50, required=False)
    county = forms.CharField(max_length=50, required=False)
    postcode = forms.CharField(max_length=10, required=False)
    country = forms.ChoiceField(
        choices=[
            ('England', 'England'),
            ('Scotland', 'Scotland'),
            ('Wales', 'Wales'),
            ('Northern Ireland', 'Northern Ireland')
        ],
        required=False
    )
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    membership = forms.ChoiceField(
        choices=[
            ('None', 'None'),
            ('Standard', 'Standard'),
            ('Premium', 'Premium'),
            ('Student', 'Student')
        ],
        required=False
    )