# Generated by Django 3.0.5 on 2020-04-10 05:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0010_auto_20200309_2336'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodicPin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn_on_at', models.TimeField(blank=True, null=True)),
                ('turn_off_at', models.TimeField(blank=True, null=True)),
                ('pin', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='board.Pin')),
            ],
        ),
    ]
