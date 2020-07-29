from django.core.management.base import BaseCommand, CommandError
import pandas as panda
from datetime import datetime, timedelta
from data_pull.models import DailyCountyKnownCases, DailyCountyDeaths
from text_signup.models import County
import urllib.error
from urllib.error import HTTPError

class Command(BaseCommand):

    help = 'Fetches the CSVs from USAFacts.org and loads them into the database'

    def handle(self, *args, **options):

        # This function handles cleaning the county names in the CSVs
        # For example, the file incorrectly spells Lac qui Parle County in Minnesota
        def clean_county_name(name):

            if state == 'MO':
                if 'Jackson County' in name:
                    name = 'Jackson County'

            if state == 'VA':
                if name == 'Matthews County':
                    name = 'Mathews County'

            if state == 'MN':
                if name == 'Lac Qui Parle County':
                    name = 'Lac qui Parle County'

            return name


        # URLs where CSVs reside
        known_cases_url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv'
        deaths_url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv'

        # Calculate yesterday's date since it is the name of the column we want to pull
        previous_date_csv = str((datetime.now() - timedelta(1)).strftime('%#m/%#d/%#y'))
        # Calculate yesterday's date in the correct format for the database column
        previous_date_db = str((datetime.now() - timedelta(1)).strftime('%Y-%m-%d'))

        # Define list of columns to pull from CSV
        column_names = ['County Name', 'State', previous_date_csv]

        # Try creating the dataframes from the files
        try:
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

            # All Counties cases
            all_counties_cases = 0

            for index, row in known_cases_dataframe.iterrows():

                # Create variables to hold values from CSV
                county_name = row['County Name']
                state = row['State']
                cases = row[previous_date_csv]

                # Ignore the unallocated row in the file
                if county_name != 'Statewide Unallocated':

                    # Increment the number of rows read
                    known_cases_csv_rows += 1

                    # Clean county name for the few odd county names in the file
                    county_name = clean_county_name(county_name)

                    # If it's the first row in the file, set the previous_state value
                    if known_cases_csv_rows == 1:
                        previous_state = state

                    try:
                        # Lookup county using name and state code from CSV
                        county = County.objects.get(t_county__startswith=county_name, n_state__c_state=state)

                        # Create object for insert
                        cases_row = DailyCountyKnownCases(n_county=county, d_date=previous_date_db, q_cases=cases)

                        # Insert object
                        cases_row.save()
                        known_cases_inserts += 1

                        # All Counties logic
                        # If at the end of processing a state
                        if state != previous_state:

                            # Lookup county using name and state code from CSV
                            all_counties = County.objects.get(t_county__contains="All Counties", n_state__c_state=previous_state)

                            # Create object for insert
                            all_counties_row = DailyCountyKnownCases(n_county=all_counties, d_date=previous_date_db, q_cases=all_counties_cases)

                            # Insert the object
                            all_counties_row.save()
                            known_cases_inserts += 1

                            # Set up variables to continue reading next state
                            all_counties_cases = cases
                            previous_state = state

                        # If still processing the same county
                        else:
                            all_counties_cases += cases

                    except:
                        county_state_value = county_name + " " + state
                        if county_state_value not in missing_counties:
                            missing_counties.append(county_state_value)

            ##########################################################
            # This needs to be done to handle the last row in the file
            ##########################################################

            # Lookup county using name and state code from CSV
            all_counties = County.objects.get(t_county__contains="All Counties", n_state__c_state=previous_state)

            # Create object for insert
            all_counties_row = DailyCountyKnownCases(n_county=all_counties, d_date=previous_date_db, q_cases=all_counties_cases)

            # Insert the object
            all_counties_row.save()
            known_cases_inserts += 1

            ##########################################################

            # If there were any counties missing from the county table lookup, print those out
            if len(missing_counties) != 0:
                self.stdout.write(self.style.ERROR('ERROR - Missing counties: %s' % missing_counties))

            # Print execution message
            self.stdout.write(self.style.SUCCESS('Successfully inserted %s known cases rows for %s' % (known_cases_inserts, previous_date_db)))

            #####################################
            # Processes the CSV for county deaths
            #####################################

            # Used to store any counties that are missing from the counties table
            missing_counties = []

            # All Counties deaths
            all_counties_deaths = 0

            for index, row in deaths_dataframe.iterrows():

                # Create variables to hold values from CSV
                county_name = row['County Name']
                state = row['State']
                deaths = row[previous_date_csv]

                # Ignore the unallocated row in the file
                if county_name != 'Statewide Unallocated':

                    # Increment the number of rows read
                    deaths_csv_rows += 1

                    # Clean county name for the few odd county names in the file
                    county_name = clean_county_name(county_name)

                    # If it's the first row in the file, set the previous_state value
                    if deaths_csv_rows == 1:
                        previous_state = state

                    try:
                        # Lookup county using name and state code from CSV
                        county = County.objects.get(t_county__startswith=county_name, n_state__c_state=state)

                        # Create object for insert
                        cases_row = DailyCountyDeaths(n_county=county, d_date=previous_date_db, q_deaths=deaths)

                        # Insert object
                        cases_row.save()
                        deaths_inserts += 1

                        # All Counties logic
                        # If at the end of processing a state
                        if state != previous_state:

                            # Lookup county using name and state code from CSV
                            all_counties = County.objects.get(t_county__contains="All Counties", n_state__c_state=previous_state)

                            # Create object for insert
                            all_counties_row = DailyCountyDeaths(n_county=all_counties, d_date=previous_date_db, q_deaths=all_counties_deaths)

                            # Insert the object
                            all_counties_row.save()
                            deaths_inserts += 1

                            # Set up variables to continue reading next state
                            all_counties_deaths = deaths
                            previous_state = state

                        # If still processing the same county
                        else:
                            all_counties_deaths += deaths

                    except:
                        county_state_value = county_name + " " + state
                        if county_state_value not in missing_counties:
                            missing_counties.append(county_state_value)

            ##########################################################
            # This needs to be done to handle the last row in the file
            ##########################################################

            # Lookup county using name and state code from CSV
            all_counties = County.objects.get(t_county__contains="All Counties", n_state__c_state=previous_state)

            # Create object for insert
            all_counties_row = DailyCountyDeaths(n_county=all_counties, d_date=previous_date_db, q_deaths=all_counties_deaths)

            # Insert the object
            all_counties_row.save()
            deaths_inserts += 1

            ##########################################################

            # If there were any counties missing from the county table lookup, print those out
            if len(missing_counties) != 0:
                self.stdout.write(self.style.ERROR('ERROR - Missing counties: %s' % missing_counties))

            # Print execution message
            self.stdout.write(self.style.SUCCESS('Successfully inserted %s deaths rows for %s' % (deaths_inserts, previous_date_db)))

        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.stdout.write(self.style.ERROR('File not found at the URL for one or more of the CSVs'))
            else:
                self.stdout.write(self.style.ERROR('Error retrieving CSVs at one of the URLs'))
