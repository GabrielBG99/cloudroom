from django.contrib import admin
from boards.models import Board


class BoardAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'status',
        'allowed',
    ]


admin.site.register(Board, BoardAdmin)