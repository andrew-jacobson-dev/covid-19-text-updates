from django import forms
from text_signup.models import State, County, Frequency


class TextSignupForm(forms.Form):

    email_address = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Email address"
        })
    )

    phone_country_code = forms.CharField(
        max_length=4,
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+1",
            "initial": "+1"
        })
    )

    phone_area_code = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "111"
        })
    )

    phone_local_code = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "111"
        })
    )

    phone_line_code = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "1111"
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
        empty_label="Select text frequency",
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )

    consent = forms.BooleanField()


class OptOutStep1Form(forms.Form):

    email_address = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Email address"
        })
    )

    phone_country_code = forms.CharField(
        max_length=4,
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+1"
        })
    )

    phone_area_code = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "111"
        })
    )

    phone_local_code = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "111"
        })
    )

    phone_line_code = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "1111"
        })
    )


class OptOutStep2Form(forms.Form):

    opt_out_code = forms.CharField(
        max_length=8,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Code"
        })
    )

    confirm = forms.BooleanField()