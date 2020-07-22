from django.shortcuts import render
from django.http import HttpResponseRedirect
from text_signup.forms import TextSignupForm
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from text_signup.models import Recipient, RecipientSelection, County, Frequency
from django.db import IntegrityError


# Create your views here.
def text_signup_index(request):

    # Create empty form
    textsignup_form = TextSignupForm()

    if request.method == 'POST':
        textsignup_form = TextSignupForm(request.POST)

        if textsignup_form.is_valid():

            email = textsignup_form.cleaned_data['email_address']
            phone_area_code = textsignup_form.cleaned_data['phone_area_code']
            phone_local_code = textsignup_form.cleaned_data['phone_local_code']
            phone_line_code = textsignup_form.cleaned_data['phone_line_code']
            state = textsignup_form.cleaned_data['state']
            county = textsignup_form.cleaned_data['county']
            frequency = textsignup_form.cleaned_data['frequency']
            consent = textsignup_form.cleaned_data['consent']

            # Create new Recipient object
            new_recipient = Recipient(
                t_email_address=email,
                t_phone_area_code=phone_area_code,
                t_phone_local_code=phone_local_code,
                t_phone_line_code=phone_line_code,
                i_consent=consent
            )

            # Attempt to save the new Recipient object
            try:
                new_recipient.save()
                messages.success(request, 'Thank you for registering! We have successfully received your request.')

                # Lookup county and frequency
                new_recipient_county = County.objects.get(t_county=county, n_state__t_state=state)
                new_recipient_frequency = Frequency.objects.get(t_frequency=frequency)

                # Create new RecipientSelection object
                new_recipient_selection = RecipientSelection(
                    n_recipient=new_recipient,
                    n_county=new_recipient_county,
                    n_frequency=new_recipient_frequency
                )

                # Attempt to save the new RecipientSelection object
                try:
                    new_recipient_selection.save()
                except:
                    messages.error(request, 'An error occurred!')

            except IntegrityError:
                messages.error(request, 'Email address has already been registered!')
            finally:
                return HttpResponseRedirect('/')

    # Create context
    context = {
        'textsignup_form': textsignup_form,
    }

    # Return request with context
    return render(request, 'text_signup.html', context)