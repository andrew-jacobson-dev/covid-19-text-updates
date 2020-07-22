from django import forms
from text_signup.models import State, County, Frequency, RecipientSelection


class TextSignupForm(forms.Form):

    email_address = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your email address"
        })
    )

    phone_area_code = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "XXX"
        })
    )

    phone_local_code = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "XXX"
        })
    )

    phone_line_code = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "XXXX"
        })
    )

    state = forms.ModelChoiceField(
        queryset=State.objects.order_by('t_state'),
        empty_label="Select a state",
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )

    county = forms.ModelChoiceField(
        queryset=County.objects.order_by('t_county'),
        empty_label="Select a county",
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )

    frequency = forms.ModelChoiceField(
        queryset=Frequency.objects.order_by('n_order'),
        empty_label="Select your desired text frequency",
        widget=forms.Select(attrs={
            # "class": "form-check form-check-inline"
            "class": "form-control"
        })
    )

    consent = forms.BooleanField()