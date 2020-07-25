import argon2
from django.db import models
from django.core.validators import MinLengthValidator
from django_celery_beat.models import PeriodicTask

from .validators import validate_pin_value, validate_digital_pin


class Board(models.Model):
    class Status(models.IntegerChoices):
        DEACTIVATED = 1
        ACTIVATED = 2
        BLOCKED = 3

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=15, unique=True)
    status = models.IntegerField(choices=Status.choices)
    password = models.TextField(validators=[MinLengthValidator(12)])

    def save(self, *args, **kwargs):
        if not self.pk:
            ph = argon2.PasswordHasher()
            self.password = ph.hash(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Board ID: #{self.pk} - {self.name}'

    class Meta:
        indexes = [
            models.Index(fields=['created']),
            models.Index(fields=['updated']),
            models.Index(fields=['status']),
        ]

class Pin(models.Model):
    class Mode(models.IntegerChoices):
        INPUT = 1
        OUTPUT = 2

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    periodic_behaviors = models.ManyToManyField(PeriodicTask)

    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    value = models.CharField(max_length=3, validators=[validate_pin_value])
    mode = models.IntegerField(choices=Mode.choices, default=Mode.OUTPUT)
    is_digital = models.BooleanField(default=True)
    description = models.CharField(max_length=512, null=True, blank=True)

    def operation_info(self):
        return {'number': self.number, 'value': self.value, 'mode': self.mode}

    def save(self, *args, **kwargs):
        if self.is_digital: validate_digital_pin(value=self.value)
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['created']),
            models.Index(fields=['updated']),
            models.Index(fields=['number']),
            models.Index(fields=['value']),
            models.Index(fields=['is_digital']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['number', 'board'], 
                name='pin_constraint'
            )
        ]
