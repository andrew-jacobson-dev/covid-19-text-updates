# Generated by Django 3.0.8 on 2020-07-11 19:48

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('text_signup', '0011_auto_20200711_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='county',
            name='n_state',
            field=smart_selects.db_fields.GroupedForeignKey(group_field='id', on_delete=django.db.models.deletion.CASCADE, to='text_signup.State'),
        ),
    ]
