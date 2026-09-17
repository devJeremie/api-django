"""
Configuration ASGI pour le projet api.

Expose l'appelable ASGI dans une variable de module nommée ``application``.

Pour plus d'informations sur ce fichier, voir
https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

application = get_asgi_application()
