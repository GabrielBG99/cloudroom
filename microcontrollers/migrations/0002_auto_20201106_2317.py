# Generated by Django 3.1.3 on 2020-11-07 02:17

from django.db import migrations, models
import microcontrollers.validators


class Migration(migrations.Migration):

    dependencies = [
        ('microcontrollers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pin',
            name='value',
            field=models.CharField(max_length=4, validators=[microcontrollers.validators.validate_pin_value]),
        ),
    ]