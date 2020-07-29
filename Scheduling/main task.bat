@echo off
title COVID-19 Text Updates Processing
color 0a

:: Fetch CSV every day of the week
start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py fetch_csv && deactivate"
echo Fetched CSVs
echo ........................
echo Starting daily processing
start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py summarize_data Daily && deactivate"
echo ...Summarized data
start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py send_text Daily && deactivate"
echo ...Sent texts
echo Finished daily processing
echo ........................

:: Get the day of the week (name) and day of the month (number) 
for /f "tokens=1-4 delims=/ " %%i in ("%date%") do (
     set day_of_week=%%i
     set day_of_month=%%k
)

:: Determine if it's bi-weekly
if %day_of_week% == Mon set is_bi_weekly=true
if %day_of_week% == Fri set is_bi_weekly=true
if defined is_bi_weekly (
	echo Starting bi-weekly %day_of_week% processing
	start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py summarize_data Bi-Weekly && deactivate"
	echo ...Summarized data		
	start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py send_text Bi-Weekly && deactivate"
	echo ...Sent texts
	echo Finished bi-weekly %day_of_week% processing
	echo ........................
)

if %day_of_week% == Tue (
	echo Staring weekly processing
	start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py summarize_data Weekly && deactivate"
	echo ...Summarized data		
	start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py send_text Weekly && deactivate"
	echo ...Sent texts
	echo Done running weekly stuff
	echo ........................	
)

:: Determine if it's monthly
if %day_of_month% == 1 (
	echo Starting monthly processing
	start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py summarize_data Monthly && deactivate"
	echo ...Summarized data
	start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py send_text Monthly && deactivate"
	echo ...Sent texts
	echo Finished monthly processing
	echo ........................
)

pause	