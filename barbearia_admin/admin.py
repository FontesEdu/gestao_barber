from datetime import date, datetime, timedelta
from django import forms
from django.shortcuts import redirect, render
from django.contrib import admin
from .models import *

class GerarDisponibilidadeForm(forms.Form):
    data_fim = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )
    intervalo = forms.IntegerField(initial=30)

    horarios_manha_inicio = forms.TimeField(required=False)
    horarios_manha_fim = forms.TimeField(required=False)

    horarios_tarde_inicio = forms.TimeField(required=False)
    horarios_tarde_fim = forms.TimeField(required=False)

    incluir_sabado = forms.BooleanField(
        required=False, initial=True, 
        label="Gerar horários aos sábados?"
    )
    incluir_domingo = forms.BooleanField(
        required=False, initial=True, 
        label="Gerar horários aos domingos?"
    )


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "data", "horario")
    list_filter = ("data", "horario")
    search_fields = ("nome", "telefone")


@admin.register(Disponibilidade)
class DisponibilidadeAdmin(admin.ModelAdmin):
    change_list_template = "admin/disponibilidade_change_list.html"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()

        custom = [
            path("gerar/", self.admin_site.admin_view(self.gerar_disponibilidades)),
        ]
        return custom + urls

    def gerar_disponibilidades(self, request):
        if request.method == "POST":
            form = GerarDisponibilidadeForm(request.POST)
            if form.is_valid():

                data_inicio = date.today()
                data_fim = form.cleaned_data["data_fim"]
                intervalo = form.cleaned_data["intervalo"]

                incluir_sabado = form.cleaned_data["incluir_sabado"]
                incluir_domingo = form.cleaned_data["incluir_domingo"]

                ranges = []

                if form.cleaned_data["horarios_manha_inicio"] and form.cleaned_data["horarios_manha_fim"]:
                    ranges.append((
                        form.cleaned_data["horarios_manha_inicio"],
                        form.cleaned_data["horarios_manha_fim"]
                    ))

                if form.cleaned_data["horarios_tarde_inicio"] and form.cleaned_data["horarios_tarde_fim"]:
                    ranges.append((
                        form.cleaned_data["horarios_tarde_inicio"],
                        form.cleaned_data["horarios_tarde_fim"]
                    ))

                dia = data_inicio
                while dia <= data_fim:

                    # pula sábado
                    if dia.weekday() == 5 and not incluir_sabado:
                        dia += timedelta(days=1)
                        continue

                    # pula domingo
                    if dia.weekday() == 6 and not incluir_domingo:
                        dia += timedelta(days=1)
                        continue

                    for inicio, fim in ranges:
                        atual = datetime.combine(dia, inicio)
                        limite = datetime.combine(dia, fim)

                        while atual <= limite:
                            Disponibilidade.objects.get_or_create(
                                data=dia,
                                horario=atual.time()
                            )
                            atual += timedelta(minutes=intervalo)

                    dia += timedelta(days=1)

                self.message_user(request, "Horários gerados com sucesso!")
                return redirect("../")

        else:
            form = GerarDisponibilidadeForm()

        return render(request, "admin/gerar_disponibilidade.html", {"form": form})

    