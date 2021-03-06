import json
from abc import ABC
from contextlib import suppress
from random import shuffle
import pytest
from django.db.transaction import TransactionManagementError
from ..models import Board, Pin
from ..serializers.periodic_behavior import CreatePeriodicPinBehaviorSerializer


class BaseMicrocontrollerTest(ABC):
    @pytest.fixture
    def board_data(self, faker):
        def generate_data(**overwrite):
            secret = list(''.join(faker.address().split()))
            shuffle(secret)

            data = {
                'name': f'Test #{faker.unique.random_int(max=10000)}',
                'secret': ''.join(secret),
                'status': Board.Status.ACTIVATED,
            }
            data.update(overwrite)
            return data

        return generate_data

    @pytest.fixture
    def board(self, db, board_data):
        data = board_data()
        board = Board.objects.create(**data)

        yield board, data

        with suppress(TransactionManagementError):
            board.delete()

    @pytest.fixture
    def pin_data(self, faker, board):
        def generate_data(is_digital=True, **override):
            value = 'ON' if is_digital else str(faker.random_int(max=1023))

            data = {
                'board': board[0].pk,
                'number': faker.unique.random_int(max=55),
                'name': f'Test #{faker.unique.random_int(max=10000)}',
                'value': value,
                'is_digital': is_digital,
                'description': 'Test Pin',
            }
            data.update(override)
            return data

        return generate_data

    @pytest.fixture
    def pin(self, db, pin_data):
        data = pin_data()
        pin = Pin.objects.create(**{
            **data,
            'board': Board.objects.get(pk=data['board']),
        })

        yield pin, data

        with suppress(TransactionManagementError):
            pin.delete()

    @pytest.fixture
    def periodic_pin_data(self, faker, pin):
        def generate_data(task: str = '', **kwargs):
            task = task or 'microcontrollers.tasks.change_pin_value'
            kwargs = kwargs or {'pin_id': pin[0].pk, 'value': 'ON'}
            data = {
                'pin': pin[0].pk,
                'task': {
                    'name': 'test',
                    'task': task,
                    'kwargs': json.dumps(kwargs),
                    'enabled': True,
                    'crontab': {}
                }
            }
            return data

        return generate_data

    @pytest.fixture
    def periodic_pin(self, db, periodic_pin_data):
        data = periodic_pin_data()
        serializer = CreatePeriodicPinBehaviorSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        periodic_pin = serializer.instance

        yield periodic_pin, data

        with suppress(TransactionManagementError):
            periodic_pin.delete()
