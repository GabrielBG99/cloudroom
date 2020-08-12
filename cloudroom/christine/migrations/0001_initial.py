# Generated by Django 3.1 on 2020-08-12 04:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('text', models.TextField()),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChristineResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('command_type', models.IntegerField(choices=[(1, 'Request'), (2, 'Result'), (3, 'Error')])),
                ('text', models.TextField()),
                ('content', models.JSONField(null=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='christine.message')),
            ],
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['created'], name='christine_m_created_968b3e_idx'),
        ),
        migrations.AddIndex(
            model_name='christineresponse',
            index=models.Index(fields=['created'], name='christine_c_created_1b1fb9_idx'),
        ),
    ]
