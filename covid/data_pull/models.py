from django.db import models
from text_signup.models import County, State, Frequency


class DailyCountyKnownCases(models.Model):
    n_county = models.ForeignKey(County, on_delete=models.CASCADE)
    d_date = models.DateField()
    q_cases = models.IntegerField()


class DailyCountyDeaths(models.Model):
    n_county = models.ForeignKey(County, on_delete=models.CASCADE)
    d_date = models.DateField()
    q_deaths = models.IntegerField()


class SummaryByCountyFrequency(models.Model):
    n_county = models.ForeignKey(County, on_delete=models.CASCADE)
    n_frequency = models.ForeignKey(Frequency, on_delete=models.CASCADE)
    d_updated = models.DateField()
    q_cases_change = models.IntegerField()
    q_total_cases = models.IntegerField()
    q_deaths_change = models.IntegerField()
    q_total_deaths = models.IntegerField()


class SummaryByStateFrequency(models.Model):
    n_state = models.ForeignKey(State, on_delete=models.CASCADE)
    n_frequency = models.ForeignKey(Frequency, on_delete=models.CASCADE)
    d_updated = models.DateField()
    q_cases_change = models.IntegerField()
    q_total_cases = models.IntegerField()
    q_deaths_change = models.IntegerField()
    q_total_deaths = models.IntegerField()