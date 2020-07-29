from django.core.management.base import BaseCommand, CommandError
import pandas as panda
from datetime import datetime, timedelta
from data_pull.models import DailyCountyKnownCases, DailyCountyDeaths, SummaryByCountyFrequency
from django.db.models import Window, Subquery, Q, Value, IntegerField
from django.db.models.functions import Lag
from text_signup.models import Frequency


class Command(BaseCommand):

    help = 'Extracts data from transactional tables and fills the summary tables for a specified frequency'

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
                help="Enter " + "'" + frequency.t_frequency + "'" + " to summarize " + frequency.t_frequency + " data",
                default=False,
            )

    # This function is the primary handler for the command
    def handle(self, *args, **options):

        # Retrieve option from command
        option = options.get('frequency')
        option = option[0]

        # See if option is valid
        try:
            frequency_lookup = Frequency.objects.get(t_frequency=option)

            # Empty the Summary table for the specified frequency
            SummaryByCountyFrequency.objects.filter(n_frequency=frequency_lookup).delete()

            # Will always look at yesterday's date for retrieving information
            end_date = datetime.now().date() - timedelta(1)

            # Calculate how far back to pull data for based on the command option
            if option == 'Daily':
                start_date = datetime.now().date() - timedelta(2)

            if option == 'Bi-Weekly':
                day_of_week = datetime.now().weekday()
                # If it's Monday
                if day_of_week == 0:
                    # Look back to Friday
                    start_date = datetime.now().date() - timedelta(3)
                # Else when the job runs on Friday
                else:
                    # Look back to Monday
                    start_date = datetime.now().date() - timedelta(4)

            if option == 'Weekly':
                start_date = datetime.now().date() - timedelta(8)

            if option == 'Monthly':
                day_of_month = datetime.now().date().day
                start_date = (datetime.now().date() - timedelta(day_of_month)) + timedelta(1)

            # Retrieve rows from DailyCountyKnownCases where the date is the start date or the end date
            # Also, using the lag function to get the previous row's value for cases
            known_cases = DailyCountyKnownCases.objects.annotate(
                q_cases_lag=Window(
                    expression=Lag('q_cases', offset=1, default=0),
                    order_by=('n_county', 'd_date')),
            ).filter(Q(d_date=start_date) | Q(d_date=end_date))

            # Define variable to keep track of number of inserts
            summary_row_inserts = 0

            # Iterate through the results
            for known_case in known_cases:

                # Only want to look at the row that corresponds to yesterday's date since it has the lag value we need
                if known_case.d_date == end_date:

                    # Create and fill variables for SummaryByCountyFrequency columns
                    summary_n_county = known_case.n_county
                    summary_n_frequency = frequency_lookup
                    summary_d_updated = datetime.now().date()
                    summary_q_cases_change = known_case.q_cases - known_case.q_cases_lag
                    summary_q_total_cases = known_case.q_cases
                    summary_q_deaths_change = 0
                    summary_q_total_deaths = 0

                    # Create SummaryByCountyFrequency object with previously created variables
                    summary_row_insert = SummaryByCountyFrequency(
                        n_county=summary_n_county,
                        n_frequency=summary_n_frequency,
                        d_updated=summary_d_updated,
                        q_cases_change=summary_q_cases_change,
                        q_total_cases=summary_q_total_cases,
                        q_deaths_change=summary_q_deaths_change,
                        q_total_deaths=summary_q_total_deaths
                    )

                    # Insert SummaryByCountyFrequency object
                    summary_row_insert.save()

                    # Increment insert counter
                    summary_row_inserts += 1

            self.stdout.write(self.style.SUCCESS('Inserted %s %s known cases summary rows' % (summary_row_inserts, option.lower())))

            ###################################################
            # Update death data on SummaryByCountyFrequency
            ###################################################

            summary_row_updates = 0

            # Retrieve rows from DailyCountyDeaths where the date is the start date or the end date
            # Also, using the lag function to get the previous row's value for cases
            deaths = DailyCountyDeaths.objects.annotate(
                q_deaths_lag=Window(
                    expression=Lag('q_deaths', offset=1, default=0),
                    order_by=('n_county', 'd_date')
                ),
            ).filter(Q(d_date=start_date) | Q(d_date=end_date))

            # Iterate through the results
            for death in deaths:

                # Only want to look at the row that corresponds to yesterday's date since it has the lag value we need
                if death.d_date == end_date:

                    # Create and fill variables for SummaryByCountyFrequency columns that we want to update
                    summary_q_deaths_change = death.q_deaths - death.q_deaths_lag
                    summary_q_total_deaths = death.q_deaths

                    # Update values by county and frequency
                    SummaryByCountyFrequency.objects.filter(n_county=death.n_county, n_frequency=frequency_lookup).update(
                        q_deaths_change=summary_q_deaths_change,
                        q_total_deaths=summary_q_total_deaths
                    )

                    # Increment updates counter
                    summary_row_updates += 1

            self.stdout.write(self.style.SUCCESS('Updated %s summary rows' % summary_row_updates))

        # If the specified option was not in the Frequency table
        except:
            self.stdout.write(self.style.ERROR('Please try a different option. "%s" is invalid.' % option))
