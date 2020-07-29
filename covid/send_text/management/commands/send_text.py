import os
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
from text_signup.models import Recipient, RecipientSelection, Frequency
from data_pull.models import DailyCountyKnownCases, DailyCountyDeaths, SummaryByCountyFrequency
from twilio.rest import Client


class Command(BaseCommand):

    help = 'Sends text messages to the registered recipients'

    # This function adds all of the values from the Frequency table as arguments for the command
    def add_arguments(self, parser):

        parser.add_argument('frequency', nargs='+')

        # Retrieve list of possible frequencies (Daily, Weekly, etc.)
        frequencies = Frequency.objects.all()

        # Iterate through frequencies and add them as possible arguments
        for frequency in frequencies:
            argument = '--' + frequency.t_frequency
            parser.add_argument(
                argument,
                action='store_true',
                dest='frequency',
                help="Enter " + "'" + frequency.t_frequency + "'" + " to send texts to " + frequency.t_frequency + " recipients",
                default=False,
            )

    # This function is the primary handler for the command
    def handle(self, *args, **options):

        # Retrieve option from command
        option = options.get('frequency')
        option = option[0]

        # Text messages counters
        text_messages_sent = 0
        text_messages_not_sent = 0

        try:
            frequency_lookup = Frequency.objects.get(t_frequency=option)

            # Retrieve recipients (along with the county and state table values) for the desired frequency
            recipients = RecipientSelection.objects.select_related('n_recipient').select_related('n_county').select_related('n_county__n_state').filter(n_frequency=frequency_lookup)

            # Retrieve rows from summary table for the desired frequency
            summary_rows_by_frequency = SummaryByCountyFrequency.objects.filter(n_frequency=frequency_lookup)

            # Create empty dictionary to store all needed rows
            distinct_counties_dict = {}

            # Iterate through recipients and build dictionary of the rows from SummaryByCountyFrequency.
            # The point is to avoid looking up the same county multiple times and instead store the needed counties
            # once in a dictionary.
            for recipient in recipients:

                # Should return 1 row per county since it was filtered to frequency already
                distinct_county = summary_rows_by_frequency.get(n_county=recipient.n_county)

                # If the county is not already in the dictionary, add it
                if distinct_county not in distinct_counties_dict.values():
                    distinct_counties_dict[distinct_county.n_county] = distinct_county

            # Retrieve environment variables for Twilio API
            account_sid = os.environ.get('django_covid_twilio_ACCOUNT_SID')
            auth_token = os.environ.get('django_covid_twilio_AUTH_TOKEN')
            from_number = os.environ.get('django_covid_twilio_FROM_NUMBER')

            # Iterate through recipient list and send text messages
            for recipient in recipients:

                # Create the TO number from recipient data
                to_number = recipient.n_recipient.t_phone_country_code + recipient.n_recipient.t_phone_area_code + recipient.n_recipient.t_phone_local_code + recipient.n_recipient.t_phone_line_code

                # Lookup the recipient's county data in the previously created dictionary
                county_summary_data = distinct_counties_dict.get(recipient.n_county)

                # Create the message content
                text_message_body = \
                    "Here is your {} COVID-19 text update for {} in {}: \n \n{} new known cases since your last update. " \
                    "{} total known cases. \n \n{} deaths since your last update. {} total deaths. \n \n" \
                    "Want to opt out of future texts? Visit www.covid19textupdates.com/optout".format(
                    option.lower(),
                    recipient.n_county.t_county,
                    recipient.n_county.n_state.t_state,
                    county_summary_data.q_cases_change,
                    county_summary_data.q_total_cases,
                    county_summary_data.q_deaths_change,
                    county_summary_data.q_total_deaths)

                try:
                    # Create Client object
                    client = Client(account_sid, auth_token)
                    to_number = "+4915224460314"
                    # Create and send message
                    client.api.account.messages.create(
                        to=to_number,
                        from_=from_number,
                        body=text_message_body
                    )
                    print("Sending", option.lower(), "text to", to_number, "for", recipient.n_county.t_county, "in", recipient.n_county.n_state.t_state)
                    text_messages_sent += 1
                except:
                    print("ERROR sending", option.lower(), "text to", to_number, "for", recipient.n_county.t_county, "in", recipient.n_county.n_state.t_state)
                    text_messages_not_sent += 1


        except:
            self.stdout.write(self.style.ERROR('Please try a different option. "%s" is invalid.' % option))


        self.stdout.write(self.style.SUCCESS('%s %s text messages were sent successfully.' % (text_messages_sent, option.lower())))