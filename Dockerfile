FROM python:3.11-slim

# Evita criação de arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho dentro do container
WORKDIR /app

# Dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Atualiza o pip
RUN pip install --upgrade pip

# Copia e instala dependências Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia todo o projeto Django
COPY . /app

# Porta usada pelo Django/Gunicorn
EXPOSE 8000

# Permissão para o entrypoint
RUN chmod +x /app/entrypoint.sh

# EntryPoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando padrão (produção)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]