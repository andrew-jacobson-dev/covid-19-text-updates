# Generated by Django 3.0.8 on 2020-07-17 12:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('text_signup', '0015_auto_20200717_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='county',
            name='n_state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='text_signup.State'),
        ),
    ]
