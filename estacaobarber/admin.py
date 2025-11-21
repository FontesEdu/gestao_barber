from django.contrib import admin
from .models import *


@admin.register(Corte)
class CortesAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "imagem")