# Generated by Django 3.0.8 on 2020-07-24 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('text_signup', '0021_auto_20200723_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipient',
            name='i_opt_out_sent',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipient',
            name='n_opt_out',
            field=models.CharField(default='dfdfdfdf', max_length=8),
            preserve_default=False,
        ),
    ]
