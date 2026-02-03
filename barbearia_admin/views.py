import logging
import json
import re
from datetime import datetime, date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError 
from django.db.models import Count
from django_ratelimit.decorators import ratelimit
from .models import Disponibilidade, Agendamento
from .utils import enviar_notificacao_whatsapp

# O logger precisa do import logging acima para funcionar
logger = logging.getLogger(__name__)


# Tela inicial onde o cliente escolhe a data
def tela_agendamento(request):
    from django.utils import timezone

    hoje = timezone.localdate()

    horarios_hoje = list(
        Disponibilidade.objects.filter(data=hoje)
        .values_list("horario", flat=True)
    )

    datas_disponiveis = (
        Disponibilidade.objects
        .values('data')
        .annotate(total=Count('id'))
        .filter(total__gt=0)
        .values_list('data', flat=True)
    )

    import json
    # Converte datas para string JSON
    datas_formatadas = json.dumps([d.strftime("%Y-%m-%d") for d in datas_disponiveis])

    return render(request, "ver_calendario.html", {
        "datas_disponiveis": datas_formatadas,
        "horarios_hoje": json.dumps([str(h) for h in horarios_hoje])  
    })


def ver_disponibilidade(request):
    # Pega a data escolhida pelo usuário
    data_selecionada = request.GET.get('data')

    if not data_selecionada:
        return render(request, 'ver_calendario.html')

    # Busca todos os horários cadastrados para o dia
    disponibilidades = Disponibilidade.objects.filter(data=data_selecionada)

    # Lista de horários existentes
    horarios_totais = [d.horario for d in disponibilidades]

    # Busca horários já agendados
    agendados = Agendamento.objects.filter(
        data=data_selecionada
    ).values_list("horario", flat=True)

    # Filtra os horários que ainda estão disponíveis
    horarios_livres = [
        h.strftime("%H:%M") for h in horarios_totais if h not in agendados
    ]

    return render(
        request,
        'ver_disponibilidade.html',
        {
            'data_selecionada': data_selecionada,
            'horarios_livres': horarios_livres
        }
    )


# Tela de confirmação do agendamento
def confirmar_agendamento(request):
    data = request.GET.get("data")
    horario = request.GET.get("horario")
    if not data or not horario:
        return HttpResponse("Erro: data ou horário inválidos.", status=400)
    return render(request, "confirmar_agendamento.html", {"data": data, "horario": horario})



# Finaliza o agendamento, com limite de 3 tentativas por dia

#@ratelimit(key='ip', rate='3/d', block=True)
def finalizar_agendamento(request):
    if request.method != "POST":
        return HttpResponse("Método inválido.", status=405)

    nome = request.POST.get("nome")
    telefone = request.POST.get("telefone")
    data_str = request.POST.get("data")
    horario_str = request.POST.get("horario") # Recebido como string '09:00'

    # 1. Validação básica de campos
    if not all([nome, telefone, data_str, horario_str]):
        return HttpResponse("Campos obrigatórios ausentes.", status=400)

    try:
        # 2. Tratamento da Data (Suporta ISO ou BR)
        try:
            data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            data_obj = datetime.strptime(data_str, "%d/%m/%Y").date()

        # 3. Tratamento do Horário (Converte string '09:00' para objeto time)
        # Isso evita erro de comparação no banco de dados
        horario_obj = datetime.strptime(horario_str, "%H:%M").time()

        # 4. Operação no Banco de Dados (Usando transação atômica se possível)
        # Buscamos a disponibilidade primeiro
        disp = Disponibilidade.objects.filter(data=data_obj, horario=horario_obj).first()
        
        if not disp:
            return HttpResponse(f"O horário {horario_str} não está cadastrado para este dia.", status=404)

        if not disp.disponivel:
            return HttpResponse("Desculpe, este horário acabou de ser preenchido por outra pessoa.", status=409)

        # 5. Criar o Agendamento
        Agendamento.objects.create(
            nome=nome,
            telefone=telefone,
            data=data_obj,
            horario=horario_obj
        )
        
        # 6. Marcar como indisponível
        disp.disponivel = False
        disp.save()

        # Preparar data para o zap
        data_formatada_br = data_obj.strftime("%d/%m/%Y")
        
        # 7. Envios de WhatsApp (Dentro de try/except para não quebrar o sucesso do cliente)
        try:
            # Notificação para o Cliente
            enviar_notificacao_whatsapp(nome, telefone, data_formatada_br, horario_str)
            # Notificação para o Barbeiro (Número fixo)
            enviar_notificacao_whatsapp(nome, "5583996854693", data_formatada_br, horario_str)
        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
            # Não retornamos erro aqui, pois o agendamento no banco já foi um sucesso!

        return render(request, "sucesso.html", {
            "nome": nome,
            "data": data_formatada_br,
            "horario": horario_str
        })

    except IntegrityError:
        logger.warning(f"Tentativa de agendamento duplicado: {nome} - {data_str}")
        return HttpResponse("Você já possui um agendamento para este horário.", status=409)
    except Exception as e:
        logger.error(f"ERRO CRÍTICO NO AGENDAMENTO: {str(e)}")
        # Em produção, mostramos uma mensagem amigável, mas logamos o erro real
        return HttpResponse(f"Ocorreu um erro interno. Por favor, tente novamente. (Erro: {str(e)})", status=500)

# Painel administrativo que mostra horários, agendados e livres

from datetime import datetime
import re

def painel_adm(request, data=None):
    try:
        if data:
            hoje = datetime.strptime(data, "%Y-%m-%d").date()
        else:
            hoje_str = request.GET.get("data")
            if hoje_str:
                hoje = datetime.strptime(hoje_str, "%Y-%m-%d").date()
            else:
                hoje = datetime.today().date()

        # Busca disponibilidades do dia
        horarios = Disponibilidade.objects.filter(data=hoje).order_by("horario")
        agora = datetime.now()

        # Busca agendamentos do dia
        agendamentos = Agendamento.objects.filter(data=hoje)
        # Criamos o dicionário mapeando o horário ao objeto Agendamento
        agendados_dict = {ag.horario: ag for ag in agendamentos}

        for h in horarios:
            # Verifica se o horário já passou
            h.passou = datetime.combine(h.data, h.horario) < agora
            
            # Pega o agendamento correspondente
            ag = agendados_dict.get(h.horario)
            
            if ag:
                # Pegamos os dados direto do Agendamento, pois seu Model é assim
                h.cliente_nome = ag.nome 
                # Remove espaços, parênteses e traços do telefone
                h.cliente_telefone = re.sub(r'\D', '', str(ag.telefone))
            else:
                h.cliente_nome = None
                h.cliente_telefone = None

        total_horarios = horarios.count()
        total_agendados = len(agendamentos)

        return render(request, "admin/painel_adm.html", {
            "hoje": hoje,
            "horarios": horarios,
            "total_horarios": total_horarios,
            "total_agendados": total_agendados,
            "total_livres": total_horarios - total_agendados
        })
    except Exception as e:
        print(f"Erro no Painel ADM: {e}")
        raise e
        

# Remove um horário específico
def remover_horario(request, id):
    # Busca e apaga um horário
    horario = get_object_or_404(Disponibilidade, id=id)
    dia = horario.data
    horario.delete()

    return redirect(f"/agendamentos/painel_adm/?dia={dia}")


# Gera automaticamente todos os horários de um dia

def gerar_disponibilidades(request):
    dia = request.GET.get("dia")

    inicio = datetime.strptime("08:00", "%H:%M")
    fim = datetime.strptime("20:00", "%H:%M")

    atual = inicio
    while atual <= fim:
        Disponibilidade.objects.get_or_create(
            data=dia,
            horario=atual.time()
        )
        atual += timedelta(minutes=30)

    return redirect(f"/agendamentos/painel_adm/?dia={dia}")

def remover_horario(request, id):
    Disponibilidade.objects.filter(id=id).delete()
    return redirect(request.META.get("HTTP_REFERER", "painel_adm"))


def ver_disponibilidade(request):
    data_str = request.GET.get("data")
    if not data_str:
        return render(request, "ver_calendario.html")

    # Converte para date
    data_obj = date.fromisoformat(data_str)

    # Todos os horários cadastrados para a data
    disponibilidades = Disponibilidade.objects.filter(data=data_obj).order_by("horario")

    # Horários já agendados
    agendados = Agendamento.objects.filter(data=data_obj).values_list("horario", flat=True)

    agora = datetime.now()
    horarios_livres = []

    for h in disponibilidades:
        # Remove horários já agendados
        if h.horario in agendados:
            continue

        # Se for hoje, remove horários que já passaram
        if data_obj == agora.date() and datetime.combine(h.data, h.horario) <= agora:
            continue

        # Formata em HH:MM
        horarios_livres.append(h.horario.strftime("%H:%M"))

    return render(request, "ver_disponibilidade.html", {
        "data_selecionada": data_obj,
        "horarios_livres": horarios_livres
    })


def ver_horarios(request):
    data_str = request.GET.get('data')
    
    try:
        # Tenta converter a data se ela existir
        hoje = date.fromisoformat(data_str) if data_str else date.today()
    except (ValueError, TypeError):
        # Se der erro no formato, volta para a data de hoje em vez de dar Erro 500
        hoje = date.today()

    horarios = Disponibilidade.objects.filter(data=hoje).order_by("horario")
    agendamentos_qs = Agendamento.objects.filter(data=hoje)
    agendados_dict = {ag.horario: ag.nome for ag in agendamentos_qs}

    agora = datetime.now()

    for h in horarios:
        # Combina data e hora para comparar com o momento atual exato
        dt_horario = datetime.combine(h.data, h.horario)
        
        if dt_horario < agora:
            h.status = "passado"
            h.nome_cliente = ""
        elif h.horario in agendados_dict:
            h.status = "agendado"
            h.nome_cliente = agendados_dict[h.horario]
        else:
            h.status = "livre"
            h.nome_cliente = ""

    context = {
        'hoje': hoje,
        'horarios': horarios,
        'total_horarios': horarios.count(),
        'total_agendados': len(agendados_dict),
        'total_livres': horarios.count() - len(agendados_dict),
    }

    return render(request, 'ver_horarios.html', context)