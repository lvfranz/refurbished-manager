"""
Script per creare utenti di test con diversi livelli di permessi
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
django.setup()

from django.contrib.auth.models import User

print("="*60)
print("CREAZIONE UTENTI DI TEST")
print("="*60)

# Crea utente normale (NON staff)
username_normale = 'utente'
if User.objects.filter(username=username_normale).exists():
    print(f"\n⚠️  Utente '{username_normale}' esiste già")
    user_normale = User.objects.get(username=username_normale)
else:
    user_normale = User.objects.create_user(
        username=username_normale,
        password='utente123',
        email='utente@test.com',
        is_staff=False,
        is_superuser=False
    )
    print(f"\n✅ Utente normale creato!")
    print(f"   Username: {username_normale}")
    print(f"   Password: utente123")

print(f"\n   Permessi:")
print(f"   - is_staff: {user_normale.is_staff}")
print(f"   - is_superuser: {user_normale.is_superuser}")
print(f"   - Vede 'Amministrazione': {'NO' if not user_normale.is_staff else 'SI'}")

# Crea utente staff (ma non superuser)
username_staff = 'staff'
if User.objects.filter(username=username_staff).exists():
    print(f"\n⚠️  Utente '{username_staff}' esiste già")
    user_staff = User.objects.get(username=username_staff)
else:
    user_staff = User.objects.create_user(
        username=username_staff,
        password='staff123',
        email='staff@test.com',
        is_staff=True,
        is_superuser=False
    )
    print(f"\n✅ Utente staff creato!")
    print(f"   Username: {username_staff}")
    print(f"   Password: staff123")

print(f"\n   Permessi:")
print(f"   - is_staff: {user_staff.is_staff}")
print(f"   - is_superuser: {user_staff.is_superuser}")
print(f"   - Vede 'Amministrazione': {'SI' if user_staff.is_staff else 'NO'}")

# Mostra superuser esistente
superuser = User.objects.filter(is_superuser=True).first()
if superuser:
    print(f"\n✅ Superuser esistente:")
    print(f"   Username: {superuser.username}")
    print(f"   Email: {superuser.email or '(non impostata)'}")
    print(f"\n   Permessi:")
    print(f"   - is_staff: {superuser.is_staff}")
    print(f"   - is_superuser: {superuser.is_superuser}")
    print(f"   - Vede 'Amministrazione': SI")

print("\n" + "="*60)
print("RIEPILOGO UTENTI DI TEST")
print("="*60)

print(f"\n1. UTENTE NORMALE")
print(f"   Username: utente")
print(f"   Password: utente123")
print(f"   ❌ NON vede il link 'Amministrazione'")
print(f"   ❌ NON può accedere all'admin Django")
print(f"   ✅ Può usare Dashboard, Ricerca, Scadenze")

print(f"\n2. UTENTE STAFF")
print(f"   Username: staff")
print(f"   Password: staff123")
print(f"   ✅ VEDE il link 'Amministrazione'")
print(f"   ✅ PUÒ accedere all'admin Django")
print(f"   ✅ Può usare Dashboard, Ricerca, Scadenze")
print(f"   ⚠️  Permessi limitati nell'admin (configurabili)")

if superuser:
    print(f"\n3. SUPERUSER")
    print(f"   Username: {superuser.username}")
    print(f"   ✅ VEDE il link 'Amministrazione'")
    print(f"   ✅ PUÒ accedere all'admin Django")
    print(f"   ✅ Può usare Dashboard, Ricerca, Scadenze")
    print(f"   ✅ Accesso completo a tutto")

print("\n" + "="*60)
print("TEST CONSIGLIATI")
print("="*60)
print("\n1. Fai logout dal tuo account corrente")
print("2. Login come 'utente' (password: utente123)")
print("3. Verifica che NON vedi 'Amministrazione' nel menu")
print("4. Logout e login come 'staff' (password: staff123)")
print("5. Verifica che VEDI 'Amministrazione' nel menu")
print("\n" + "="*60)

