from django.shortcuts import render
from django.http import HttpResponseRedirect
from text_signup.forms import TextSignupForm, OptOutStep1Form, OptOutStep2Form
from django.core.mail import send_mail
from smtplib import SMTPException
from django.conf import settings
from django.contrib import messages
from text_signup.models import Recipient, RecipientSelection, County, Frequency
from django.db import IntegrityError
from text_signup.methods.text_signup_methods import generate_opt_out_code


# Create your views here.
def text_signup_index(request):

    # Create empty form
    textsignup_form = TextSignupForm()

    if request.method == 'POST':

        textsignup_form = TextSignupForm(request.POST)

        if textsignup_form.is_valid():

            email = textsignup_form.cleaned_data['email_address']
            phone_country_code = "+1"
            phone_area_code = textsignup_form.cleaned_data['phone_area_code']
            phone_local_code = textsignup_form.cleaned_data['phone_local_code']
            phone_line_code = textsignup_form.cleaned_data['phone_line_code']
            state = textsignup_form.cleaned_data['state']
            county = textsignup_form.cleaned_data['county']
            frequency = textsignup_form.cleaned_data['frequency']
            consent = textsignup_form.cleaned_data['consent']

            # Populate opt out fields
            opt_out_code = generate_opt_out_code()
            opt_out_sent = False

            # Create new Recipient object
            new_recipient = Recipient(
                t_email_address=email,
                t_phone_country_code=phone_country_code,
                t_phone_area_code=phone_area_code,
                t_phone_local_code=phone_local_code,
                t_phone_line_code=phone_line_code,
                i_consent=consent,
                n_opt_out=opt_out_code,
                i_opt_out_sent=opt_out_sent
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
                    messages.error(request, 'An error occurred saving your information!')

                # If that completed, then we can say that everything was successful
                # so send an email
                message_subject = "Welcome to the COVID-19 Text Updates Program"
                message_content = "Thank you for subscribing to the COVID-19 Text Updates Program. \n\nYou will begin receiving {} updates for {}, {}. \n\nChanged your mind? Visit covid19textupdates.com/optout to opt out of the program.".format(str(frequency).lower(), county, state)

                try:
                    # Send email using send_mail function
                    send_mail(message_subject,
                              message_content,
                              settings.EMAIL_HOST_USER,
                              [email],
                              fail_silently=False)

                    # Success message
                    messages.success(request, 'A welcome email was to sent you.')
                except SMTPException as e:
                    # Here is where we should send a message to the admin saying the email failed
                    # and it needs to be sent
                    print(e)
                    print('Email failure:', email, message_subject, message_content)

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
    opt_out_code = ''
    confirm = False

    if request.method == 'POST':

        if 'send_code' in request.POST:

            opt_out_step_1_form = OptOutStep1Form(request.POST)

            if opt_out_step_1_form.is_valid():

                email = opt_out_step_1_form.cleaned_data['email_address']
                phone_area_code = opt_out_step_1_form.cleaned_data['phone_area_code']
                phone_local_code = opt_out_step_1_form.cleaned_data['phone_local_code']
                phone_line_code = opt_out_step_1_form.cleaned_data['phone_line_code']

                # Try looking up the user
                try:

                    recipient = Recipient.objects.get(t_email_address=email, t_phone_area_code=phone_area_code,
                                                      t_phone_local_code=phone_local_code, t_phone_line_code=phone_line_code)

                    # Try sending the opt code in an email
                    try:

                        # Send email using send_mail function
                        message_subject = "Opting out of the COVID-19 Text Updates Program"
                        message_content = "Please enter the following code: {}".format(recipient.n_opt_out)

                        send_mail(message_subject,
                                  message_content,
                                  settings.EMAIL_HOST_USER,
                                  [email],
                                  fail_silently=False)

                        messages.success(request, 'A code has been sent to your email. Please enter that code below.',
                                         extra_tags='send_code')

                        # Try updating the recipient's opt out fields
                        try:
                            # Update opt out fields
                            # new_opt_out_code = generate_opt_out_code()
                            new_opt_out_sent = True

                            # Update recipient
                            Recipient.objects.filter(pk=recipient.id).update(i_opt_out_sent=new_opt_out_sent)

                        # If there is a problem updating, print exception (ideally alert the admin)
                        except Exception as e:
                            print(e)
                    except:
                        messages.error(request, 'An error occurred while sending you the email.', extra_tags='send_code')

                # If the user doesn't exist
                except Recipient.DoesNotExist:
                    messages.error(request, 'Sorry, no users were found with that information.', extra_tags='send_code')

        elif 'opt_out' in request.POST:

            opt_out_step_2_form = OptOutStep2Form(request.POST)

            if opt_out_step_2_form.is_valid():

                opt_out_code = opt_out_step_2_form.cleaned_data['opt_out_code']

                try:
                    # Not ideal, but look up recipient based on opt out code and whether that code was sent already
                    recipient = Recipient.objects.get(n_opt_out=opt_out_code, i_opt_out_sent=True)

                    # If their input matches their code
                    if recipient.n_opt_out == opt_out_code:

                        # Try deleting the user
                        try:
                            recipient.delete()
                            messages.success(request, 'You have been successfully removed!', extra_tags='opt_out')
                        except:
                            messages.error(request, 'An error occurred while removing you from the system.', extra_tags='opt_out')
                        finally:
                            return HttpResponseRedirect('/optout')

                except Recipient.DoesNotExist:
                    messages.error(request, "Hmm, that code doesn't appear to be correct. Try again?", extra_tags='opt_out')


    # Create context
    context = {
        'opt_out_step_1_form': opt_out_step_1_form,
        'opt_out_step_2_form': opt_out_step_2_form,
        'email_address': email,
        'phone_area_code': phone_area_code,
        'phone_local_code': phone_local_code,
        'phone_line_code': phone_line_code,
        'opt_out_code': opt_out_code,
        'confirm': confirm
    }

    return render(request, 'opt_out.html', context)