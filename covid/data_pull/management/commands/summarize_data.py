from django.core.management.base import BaseCommand, CommandError
import pandas as panda
from datetime import datetime, timedelta
from data_pull.models import DailyCountyKnownCases, SummaryByCountyFrequency
from django.db.models import Window, Subquery
from django.db.models.functions import Lag
from text_signup.models import Frequency


class Command(BaseCommand):

    help = 'Extracts data from transactional tables and fills the summary tables'

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

            if option == 'Daily':

                start_date = datetime.now().date() - timedelta(1)
                end_date = datetime.now().date() - timedelta(2)

                # DailyCountyKnownCases
                # known_cases_data_start = DailyCountyKnownCases.objects.filter(d_date=start_date)
                # known_cases_data_end = DailyCountyKnownCases.objects.filter(d_date=end_date)

                known_cases = DailyCountyKnownCases.objects.annotate(lag=Window(
                    expression=Lag('q_cases', offset=1, default=0),
                    order_by=('n_county', 'd_date')
                )).filter(d_date__range=[end_date, start_date], n_county_id=1559)

                for known_case in known_cases:

                    if known_case.d_date == start_date:

                        summary_n_county = known_case.n_county
                        summary_n_frequency = frequency_lookup
                        summary_d_updated = datetime.now().date()
                        summary_q_cases_change = known_case.q_cases - known_case.lag
                        summary_q_total_cases = known_case.q_cases

                        summary_row_insert = SummaryByCountyFrequency(
                            n_county=summary_n_county,
                            n_frequency=summary_n_frequency,
                            d_updated=summary_d_updated,
                            q_cases_change=summary_q_cases_change,
                            q_total_cases=summary_q_total_cases
                        )

                        summary_row_insert.save()