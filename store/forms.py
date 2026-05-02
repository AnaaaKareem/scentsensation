from django import forms
from django.contrib.auth.forms import AuthenticationForm
import pycountry


def get_country_choices():
    """Generate country choices from pycountry."""
    return [(c.alpha_2, c.name) for c in pycountry.countries]


def get_us_state_choices():
    return [
        ('', 'Select state'),
        ('AL', 'Alabama'), ('AK', 'Alaska'),
        ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'),
        ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('FL', 'Florida'), ('GA', 'Georgia'),
        ('HI', 'Hawaii'), ('ID', 'Idaho'),
        ('IL', 'Illinois'), ('IN', 'Indiana'),
        ('IA', 'Iowa'), ('KS', 'Kansas'),
        ('KY', 'Kentucky'), ('LA', 'Louisiana'),
        ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'),
        ('MN', 'Minnesota'), ('MS', 'Mississippi'),
        ('MO', 'Missouri'), ('MT', 'Montana'),
        ('NE', 'Nebraska'), ('NV', 'Nevada'),
        ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'), ('NY', 'New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'),
        ('OH', 'Ohio'), ('OK', 'Oklahoma'),
        ('OR', 'Oregon'), ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'), ('SD', 'South Dakota'),
        ('TN', 'Tennessee'), ('TX', 'Texas'),
        ('UT', 'Utah'), ('VT', 'Vermont'),
        ('VA', 'Virginia'), ('WA', 'Washington'),
        ('WV', 'West Virginia'), ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'), ('DC', 'District of Columbia'),
    ]


def get_uk_country_choices():
    return [
        ('ENG', 'England'), ('SCT', 'Scotland'),
        ('WLS', 'Wales'), ('NIR', 'Northern Ireland'),
    ]


class UserRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True)
    middle_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=True)
    email_address = forms.EmailField(required=True)
    DOB = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    phone_numbers = forms.CharField(max_length=15, required=False)
    gender = forms.CharField(label='Gender', widget=forms.RadioSelect(choices=[('Male', 'Male'), ('Female', 'Female')]))
    house = forms.CharField(max_length=25, required=True)
    street_name = forms.CharField(max_length=100, required=True)
    town_city = forms.CharField(max_length=50, required=True)
    county = forms.CharField(max_length=50, required=False)
    postcode = forms.CharField(max_length=10, required=False)
    country = forms.ChoiceField(choices=get_country_choices(), required=True)
    state = forms.ChoiceField(choices=get_us_state_choices(), required=False)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    membership = forms.ChoiceField(choices=[
        ('None', 'None'), ('Standard', 'Standard'),
        ('Premium', 'Premium'), ('Student', 'Student')
    ])

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

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
    country = forms.ChoiceField(choices=get_country_choices(), required=False)
    state = forms.ChoiceField(choices=get_us_state_choices(), required=False)
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