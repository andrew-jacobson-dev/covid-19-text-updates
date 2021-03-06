# Generated by Django 3.0.8 on 2020-07-27 09:39

from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('text_signup', '0022_auto_20200724_2007'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_county', smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='n_state', chained_model_field='n_state', on_delete=django.db.models.deletion.CASCADE, to='text_signup.County')),
                ('n_state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='text_signup.State')),
            ],
        ),
    ]
