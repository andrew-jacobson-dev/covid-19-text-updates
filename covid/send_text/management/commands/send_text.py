import os
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
from text_signup.models import Recipient, RecipientSelection, Frequency
from data_pull.models import DailyCountyKnownCases, DailyCountyDeaths, SummaryByCountyFrequency
from twilio.rest import Client


class Command(BaseCommand):

    help = 'Sends text messages to the registered recipients'

    def add_arguments(self, parser):

        parser.add_argument('frequency', nargs='+')

        # Retrieve list of possible frequencies (Daily, Weekly, etc.)
        Frequencies = Frequency.objects.all()

        # Iterate through frequencies and add them as possible arguments
        for frequency in Frequencies:
            argument = '--' + frequency.t_frequency
            parser.add_argument(
                argument,
                action='store_true',
                dest='frequency',
                help=argument + ' frequency',
                default=False,
            )

    def handle(self, *args, **options):

        # Retrieve option from command
        option = options.get('frequency')
        option = option[0]

        # See if option is valid
        frequency_lookup = Frequency.objects.get(t_frequency=option)

        # If the frequency was found, continue on
        if frequency_lookup:

            # Retrieve recipients with the desired frequency
            recipients = RecipientSelection.objects.select_related('n_recipient').select_related('n_county').filter(n_frequency=frequency_lookup)

            # Retrieve rows from summary table
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

            # Text messages sent counter
            text_messages_sent = 0

            # Iterate through recipient list and send text messages
            for recipient in recipients:

                # Create the TO number from recipient data
                to_number = recipient.n_recipient.t_phone_country_code + recipient.n_recipient.t_phone_area_code + recipient.n_recipient.t_phone_local_code + recipient.n_recipient.t_phone_line_code

                # Lookup the recipient's county data in the previously created dictionary
                county_summary_data = distinct_counties_dict.get(recipient.n_county)

                # Create the message content
                text_message_body = \
                    "Here is your {} COVID-19 text update for {}: \n \n{} new known cases since your last update. " \
                    "{} total known cases. \n \n{} deaths since your last update. {} total deaths. \n \n" \
                    "Want to opt out of future texts? Visit www.covid19textupdates.com/optout".format(
                    option.lower(),
                    recipient.n_county.t_county,
                    county_summary_data.q_cases_change,
                    county_summary_data.q_total_cases,
                    county_summary_data.q_deaths_change,
                    county_summary_data.q_total_deaths)

                print(text_message_body)
                # Create Client object
                # client = Client(account_sid, auth_token)

                # # Create and send message
                # client.api.account.messages.create(
                #     to=to_number,
                #     from_=from_number,
                #     body=text_message_body
                # )

                text_messages_sent += 1

        else:
            self.stdout.write(self.style.ERROR('Please try a different option. "%s" is invalid.' % option))

        self.stdout.write(self.style.SUCCESS('%s %s text messages were sent successfully.' % (text_messages_sent, option.lower())))