# Generated by Django 3.1 on 2020-08-11 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20200807_0054'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='correiosinfo',
            constraint=models.UniqueConstraint(fields=('order', 'date', 'place', 'status'), name='status'),
        ),
    ]
