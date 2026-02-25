"""
Django settings para el proyecto Ecosistema
Configuración de PRODUCCIÓN en VPS Debian (Hostinger)
"""

import os
from pathlib import Path

# ---------------------------------------------------------
#  RUTAS BASE DEL PROYECTO
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------
#  SEGURIDAD
# ---------------------------------------------------------
SECRET_KEY = "django-insecure-it)h7wo8um6o+%f+p8qduxi0p9)u7x(#zvh5k)_bj*n6wb!=p)"

# EN PRODUCCIÓN SIEMPRE:
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "72.61.134.252",
    "srv1076255.hstgr.cloud",
    "meetingup.cl",
    "www.meetingup.cl",
]

# Dominios confiables para CSRF (HTTPS)
CSRF_TRUSTED_ORIGINS = [
    "https://meetingup.cl",
    "https://www.meetingup.cl",
    "https://72.61.134.252",
]

# URL base pública (para construir enlaces absolutos si lo necesitas)
BASE_URL = "https://meetingup.cl"

# Opcionales pero recomendables si TODO tu sitio va por HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ---------------------------------------------------------
#  APPS INSTALADAS
# ---------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Tus apps
    "usuario",
    "paneladm",
]

# ---------------------------------------------------------
#  MIDDLEWARE
# ---------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Ecosistema.urls"

# ---------------------------------------------------------
#  TEMPLATES
# ---------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "usuario.context_processors.notificaciones_admin",
            ],
        },
    },
]

WSGI_APPLICATION = "Ecosistema.wsgi.application"

# ---------------------------------------------------------
#  BASE DE DATOS (MariaDB en el VPS)
# ---------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ecola",
        "USER": "ecola_user",
        "PASSWORD": "Admin.123",   # la que creaste en MariaDB
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
        },
    }
}

# ---------------------------------------------------------
#  VALIDACIÓN DE CONTRASEÑAS
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------
#  INTERNACIONALIZACIÓN
# ---------------------------------------------------------
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------
#  STATIC & MEDIA (PRODUCCIÓN)
# ---------------------------------------------------------

# Archivos estáticos (CSS, JS, imágenes de diseño)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"      # aquí colecta Django para producción
STATICFILES_DIRS = [
    BASE_DIR / "static",                   # tus archivos estáticos del proyecto
]

# Archivos subidos por usuarios (fotos, QR, etc.)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------
#  CONFIGURACIÓN DE EMAIL
# ---------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # o el servidor SMTP que uses
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')  # configura en variables de entorno
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')  # configura en variables de entorno
DEFAULT_FROM_EMAIL = 'EcosistemaLA <noreply@meetingup.cl>'

# ---------------------------------------------------------
#  CONFIG EXTRA
# ---------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
