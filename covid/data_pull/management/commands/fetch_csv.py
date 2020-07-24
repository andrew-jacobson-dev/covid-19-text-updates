from django.core.management.base import BaseCommand, CommandError
import pandas as panda
from datetime import datetime, timedelta
from data_pull.models import DailyCountyKnownCases, DailyCountyDeaths
from text_signup.models import County


class Command(BaseCommand):

    help = 'Fetches the CSVs from USAFacts.org and loads them into the database'

    def handle(self, *args, **options):

        # URLs where CSVs reside
        known_cases_url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv'
        deaths_url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv'

        # Calculate yesterday's date since it is the name of the column we want to pull
        previous_date_csv = str((datetime.now() - timedelta(2)).strftime('%#m/%#d/%#y'))
        # Calculate yesterday's date in the correct format for the database column
        previous_date_db = str((datetime.now() - timedelta(2)).strftime('%Y-%m-%d'))

        # Define list of columns to pull from CSV
        column_names = ['County Name', 'State', previous_date_csv]

        # Create dataframes by reading CSVs for the specified columns
        known_cases_dataframe = panda.read_csv(known_cases_url, usecols=column_names)
        deaths_dataframe = panda.read_csv(deaths_url, usecols=column_names)

        # Insert counters used for evaluating success of reading CSVs
        known_cases_csv_rows = 0
        deaths_csv_rows = 0
        known_cases_inserts = 0
        deaths_inserts = 0

        ###################################################
        # Processes the CSV for county cases
        ###################################################

        # Used to store any counties that are missing from the counties table
        missing_counties = []

        for index, row in known_cases_dataframe.iterrows():

            county_name = row['County Name']
            state = row['State']
            cases = row[previous_date_csv]

            if county_name != 'Statewide Unallocated':

                known_cases_csv_rows += 1

                if state == 'MO':
                    if 'Jackson County' in county_name:
                        county_name = 'Jackson County'

                if state == 'VA':
                    if county_name == 'Matthews County':
                        county_name = 'Mathews County'

                if state == 'MN':
                    if county_name == 'Lac Qui Parle County':
                        county_name = 'Lac qui Parle County'

                try:
                    # Lookup county using name and state code from CSV
                    county = County.objects.get(t_county__startswith=county_name, n_state__c_state=state)

                    # Create object for insert
                    cases_row = DailyCountyKnownCases(n_county=county, d_date=previous_date_db, q_cases=cases)

                    # Insert object
                    cases_row.save()

                    known_cases_inserts += 1
                except:
                    county_state_value = county_name + " " + state
                    if county_state_value not in missing_counties:
                        missing_counties.append(county_state_value)

        if len(missing_counties) != 0:
            self.stdout.write(self.style.ERROR('ERROR - Missing counties: %s' % missing_counties))

        self.stdout.write(self.style.SUCCESS('Successfully inserted %s/%s known cases rows for %s' % (known_cases_inserts, known_cases_csv_rows, previous_date_db)))

        ###################################################
        # Processes the CSV for county deaths
        ###################################################

        # Used to store any counties that are missing from the counties table
        missing_counties = []

        for index, row in deaths_dataframe.iterrows():

            county_name = row['County Name']
            state = row['State']
            deaths = row[previous_date_csv]

            if county_name != 'Statewide Unallocated':

                deaths_csv_rows += 1

                if state == 'MO':
                    if 'Jackson County' in county_name:
                        county_name = 'Jackson County'

                if state == 'VA':
                    if county_name == 'Matthews County':
                        county_name = 'Mathews County'

                if state == 'MN':
                    if county_name == 'Lac Qui Parle County':
                        county_name = 'Lac qui Parle County'

                try:
                    # Lookup county using name and state code from CSV
                    county = County.objects.get(t_county__startswith=county_name, n_state__c_state=state)

                    # Create object for insert
                    cases_row = DailyCountyDeaths(n_county=county, d_date=previous_date_db, q_deaths=deaths)

                    # Insert object
                    cases_row.save()

                    deaths_inserts += 1
                except:
                    county_state_value = county_name + " " + state
                    if county_state_value not in missing_counties:
                        missing_counties.append(county_state_value)

        if len(missing_counties) != 0:
            self.stdout.write(self.style.ERROR('ERROR - Missing counties: %s' % missing_counties))

        self.stdout.write(self.style.SUCCESS('Successfully inserted %s/%s deaths rows for %s' % (deaths_inserts, deaths_csv_rows, previous_date_db)))





