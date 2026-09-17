"""
Paramètres Django pour le projet api.

Généré par 'django-admin startproject' avec Django 6.1.1.

Pour plus d'informations sur ce fichier, voir
https://docs.djangoproject.com/en/6.1/topics/settings/

Pour la liste complète des paramètres et leurs valeurs, voir
https://docs.djangoproject.com/en/6.1/ref/settings/
"""

import os
from pathlib import Path

# Construit les chemins à l'intérieur du projet comme ceci : BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Paramètres de développement rapide - ne convient pas à la production
# Voir https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# AVERTISSEMENT DE SÉCURITÉ : gardez secrète la clé secrète utilisée en production !
SECRET_KEY = 'django-insecure-#v&an0o$at!cap=suc!j)rvsn-29&1)841uj7=w4viid(5$tht'

# AVERTISSEMENT DE SÉCURITÉ : ne pas activer le mode debug en production !
DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.application'


# Base de données
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

# DATABASES = {  modele de base
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
# MySQL, configuré via des variables d'environnement pour que ce même settings.py
# fonctionne à la fois en Docker (valeurs venant de .env : HOST=db, PORT=3306) et
# en local (revient à une instance MySQL sur 127.0.0.1:3306 — aucun .env requis en local).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'api-rest-django'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}


# Validation des mots de passe
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalisation
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Fichiers statiques (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'


# E-mail
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    # Note : UserViewSet.list() construit sa Response à la main et n'appelle
    # jamais paginate_queryset(), donc ce paramètre n'a aucun effet sur /users/
    # aujourd'hui — il ne s'applique qu'aux vues qui passent par la gestion
    # générique de liste de DRF.
    "DEFAULT_PAGINATION_CLASS":
    "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE":10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # JWT pour les vrais clients API (bouton Authorize de Swagger, clients
    # mobile/front-end). SessionAuthentication est ce qui permet au flux
    # /api-auth/login/ (basé sur cookie) de l'API navigable d'authentifier
    # réellement les requêtes — sans cela, une connexion par session réussie
    # renvoie quand même 401 sur chaque endpoint.
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    # Valeur par défaut globale ; UserViewSet la surcharge par action via get_permissions().
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Django USers REST API",
    "DESCRIPTION": "REST API for managing users in a Django application",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,  
}
