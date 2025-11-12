"""
WSGI config for Refurbished project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
import dotenv
from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent.parent  # project root
dotenv.load_dotenv(BASE_DIR / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')

application = get_wsgi_application()
