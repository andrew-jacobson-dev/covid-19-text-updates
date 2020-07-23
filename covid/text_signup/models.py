from django.db import models
from smart_selects.db_fields import ChainedForeignKey


# Create your models here.
class State(models.Model):
    c_state = models.CharField(max_length=2)
    t_state = models.CharField(max_length=20)

    def __str__(self):
        return self.t_state


class County(models.Model):
    n_state = models.ForeignKey(State, on_delete=models.CASCADE)
    # n_state = ChainedForeignKey(State, chained_field='n_state', chained_model_field='id', show_all=False)
    t_county = models.CharField(max_length=35)

    def __str__(self):
        return self.t_county


class Frequency(models.Model):
    n_order = models.SmallIntegerField()
    t_frequency = models.CharField(max_length=15)

    def __str__(self):
        return self.t_frequency


class Recipient(models.Model):
    t_email_address = models.CharField(max_length=256, unique=True)
    t_phone_country_code = models.CharField(max_length=4, help_text="Leading + sign, followed by the country code for the number")
    t_phone_area_code = models.CharField(max_length=3, help_text="Area code or first 3 digits of phone number")
    t_phone_local_code = models.CharField(max_length=3, help_text="Local code or second 3 digits of phone number")
    t_phone_line_code = models.CharField(max_length=4, help_text="Line code or last 4 digits of phone number")
    i_consent = models.BooleanField()

    def __str__(self):
        return self.t_email_address


class RecipientSelection(models.Model):
    n_recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    n_county = models.ForeignKey(County, on_delete=models.CASCADE)
    n_frequency = models.ForeignKey(Frequency, on_delete=models.CASCADE)