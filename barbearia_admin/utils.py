import requests
import re
from django.conf import settings

def limpar_e_formatar_numero(telefone_sujo):
    # Remove tudo que não é número
    apenas_numeros = re.sub(r'\D', '', telefone_sujo)
    # Garante o código do Brasil (55)
    if not apenas_numeros.startswith('55'):
        apenas_numeros = '55' + apenas_numeros
    return apenas_numeros

def enviar_notificacao_whatsapp(nome, telefone, data, horario):
    numero_limpo = limpar_e_formatar_numero(telefone)
    
    # Essas variáveis vamos configurar no settings.py depois
    url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE_NAME}"
    
    payload = {
        "number": numero_limpo,
        "text": f"Olá *{nome}*! ✂️\nSeu agendamento foi confirmado para o dia {data} às {horario}. Te esperamos!"
    }
    
    headers = {
        "Content-Type": "application/json",
        "apikey": settings.EVOLUTION_API_KEY
    }

    try:
        # O timeout é importante para o seu site não travar se a API estiver fora do ar
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Erro ao enviar WhatsApp: {e}")
        return False