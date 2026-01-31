import os
from pathlib import Path
import dj_database_url  # Importante: Adicione 'dj-database-url' no seu requirements.txt

# Caminho base
BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURANÇA
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-vm%8=esubp9d*n3d$90gjf*lrqf_(887i6xvr0*zsq##%p70t*")

# No Render, DEBUG deve ser False. Em desenvolvimento local, True.
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["gestao-barber-testes.onrender.com", "localhost", "127.0.0.1"]

# APPS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "barbearia_admin",
    "clientes_admin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Gerencia arquivos estáticos no Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# BANCO DE DADOS (Configurado para Render PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'), # Pegará a URL do banco do Render automaticamente
        conn_max_age=600
    )
}

# Caso o DATABASE_URL não exista (local), volta para SQLite
if not DATABASES['default']:
    DATABASES['default'] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

# Validação de Senha
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internacionalização
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Fortaleza"
USE_I18N = True
USE_TZ = True

# Arquivos Estáticos e Media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://gestao-barber-testes.onrender.com",
    "http://localhost:8000"
]

# CONFIGURAÇÕES DA EVOLUTION API (Lendo do Render Environment)
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://sua-url-api.onrender.com")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "barbearia")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "SuaChaveSecreta")