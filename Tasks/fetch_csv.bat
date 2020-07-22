@echo off
title summarize_data
color 0a
start cmd.exe /C "cd /. && cd PythonProjects/COVID && .\env\Scripts\activate && cd covid && python manage.py fetch_csv && deactivate"