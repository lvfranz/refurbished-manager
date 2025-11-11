"""
Script per creare un superuser automaticamente (solo per sviluppo)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Controlla se esiste già un superuser
if User.objects.filter(is_superuser=True).exists():
    print("✓ Un superuser esiste già!")
    superuser = User.objects.filter(is_superuser=True).first()
    print(f"  Username: {superuser.username}")
    print(f"  Email: {superuser.email or '(non impostata)'}")
else:
    print("Creazione superuser di default...")
    User.objects.create_superuser(
        username='admin',
        email='admin@refurbished.local',
        password='admin123'
    )
    print("✓ Superuser creato!")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n⚠️  IMPORTANTE: Cambia la password in produzione!")

print("\n" + "="*50)
print("Puoi ora accedere a:")
print("  http://127.0.0.1:8000/")
print("  http://127.0.0.1:8000/admin/")
print("="*50)

