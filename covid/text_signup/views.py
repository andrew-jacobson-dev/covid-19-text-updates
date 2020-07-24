from django.shortcuts import render
from django.http import HttpResponseRedirect
from text_signup.forms import TextSignupForm, OptOutStep1Form, OptOutStep2Form
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
        print("here1", textsignup_form.errors)
        if textsignup_form.is_valid():

            email = textsignup_form.cleaned_data['email_address']
            # phone_country_code = textsignup_form.cleaned_data['phone_country_code']
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
                t_phone_country_code="+1",
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


def opt_out_index(request):

    # Create empty form
    opt_out_step_1_form = OptOutStep1Form()
    opt_out_step_2_form = OptOutStep2Form()
    email = ''
    phone_area_code = ''
    phone_local_code = ''
    phone_line_code = ''

    if request.method == 'POST':

        if 'send_code' in request.POST:
            opt_out_step_1_form = OptOutStep1Form(request.POST)
            if opt_out_step_1_form.is_valid():
                email = opt_out_step_1_form.cleaned_data['email_address']
                phone_area_code = opt_out_step_1_form.cleaned_data['phone_area_code']
                phone_local_code = opt_out_step_1_form.cleaned_data['phone_local_code']
                phone_line_code = opt_out_step_1_form.cleaned_data['phone_line_code']
                messages.success(request, 'A code has been sent to your email. Please enter that code below.', extra_tags='send_code')
        elif 'opt_out' in request.POST:
            opt_out_step_2_form = OptOutStep2Form(request.POST)
            if opt_out_step_2_form.is_valid():
                code = opt_out_step_2_form.cleaned_data['opt_out_code']
                messages.success(request, 'You have been successfully removed!', extra_tags='opt_out')

    # Create context
    context = {
        'opt_out_step_1_form': opt_out_step_1_form,
        'opt_out_step_2_form': opt_out_step_2_form,
        'email_address': email,
        'phone_area_code': phone_area_code,
        'phone_local_code': phone_local_code,
        'phone_line_code': phone_line_code
    }

    return render(request, 'opt_out.html', context)

# def opt_out_step_2(request):
#
#     # Create empty form
#     opt_out_form = OptOutForm()
#     email = ''
#     phone_area_code = ''
#     phone_local_code = ''
#     phone_line_code = ''
#
#     if request.method == 'POST':
#
#         opt_out_form = OptOutForm(request.POST)
#
#         if opt_out_form.is_valid():
#             email = opt_out_form.cleaned_data['email_address']
#             phone_area_code = opt_out_form.cleaned_data['phone_area_code']
#             phone_local_code = opt_out_form.cleaned_data['phone_local_code']
#             phone_line_code = opt_out_form.cleaned_data['phone_line_code']
#             messages.success(request, 'You have been successfully removed!')
#
#     # Create context
#     context = {
#         'opt_out_form': opt_out_form,
#         'email_address': email,
#         'phone_area_code': phone_area_code,
#         'phone_local_code': phone_local_code,
#         'phone_line_code': phone_line_code
#     }
#
#     return render(request, 'opt_out.html', context)