from django import forms
from text_signup.models import State, County, Frequency, Location, Recipient
from smart_selects.form_fields import ChainedModelChoiceField
from django.forms import Select


class TextSignupForm(forms.Form):

    email_address = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
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

    frequency = forms.ModelChoiceField(
        queryset=Frequency.objects.order_by('n_order'),
        empty_label="Select text frequency",
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )

    consent = forms.BooleanField()


class LocationForm(forms.ModelForm):

    class Meta:
        model = Location
        fields = ['n_state', 'n_county']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })


class OptOutStep1Form(forms.Form):

    email_address = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
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