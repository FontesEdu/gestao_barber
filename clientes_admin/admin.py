from django.contrib import admin
from .models import *

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "foto")

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):

    def categorias_list(self, obj):
        return ", ".join([cat.nome for cat in obj.categorias.all()])

    categorias_list.short_description = "Categorias"

    list_display = ("nome", "descricao" ,"preco", "imagem", "tempo_estimado", "categorias_list")
