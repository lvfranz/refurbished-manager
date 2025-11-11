"""
Script per verificare e creare sedi mancanti per clienti esistenti
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
django.setup()

from orders.models import Cliente, SedeCliente

print("="*60)
print("VERIFICA E CREAZIONE SEDI MANCANTI")
print("="*60)

# Trova tutti i clienti
clienti = Cliente.objects.all()
print(f"\nTrovati {clienti.count()} clienti totali")

# Verifica quali non hanno sedi
clienti_senza_sedi = []
for cliente in clienti:
    if not cliente.sedi.exists():
        clienti_senza_sedi.append(cliente)

if clienti_senza_sedi:
    print(f"\n⚠️  Trovati {len(clienti_senza_sedi)} clienti SENZA sedi:")
    for cliente in clienti_senza_sedi:
        print(f"   - {cliente.nome} (ID: {cliente.pk})")

    risposta = input("\nCreare automaticamente 'Sede Principale' per questi clienti? (si/no): ")

    if risposta.lower() == 'si':
        print("\nCreazione sedi in corso...")
        created = 0
        for cliente in clienti_senza_sedi:
            SedeCliente.objects.create(
                cliente=cliente,
                nome_sede="Sede Principale",
                indirizzo=""
            )
            print(f"   ✓ Creata 'Sede Principale' per: {cliente.nome}")
            created += 1

        print(f"\n✅ Create {created} sedi!")
    else:
        print("\n❌ Operazione annullata")
else:
    print("\n✅ Tutti i clienti hanno almeno una sede!")

print("\n" + "="*60)
print("RIEPILOGO FINALE")
print("="*60)

# Statistiche finali
for cliente in Cliente.objects.all():
    num_sedi = cliente.sedi.count()
    print(f"{cliente.nome}: {num_sedi} sede/i")

print("\n✅ Verifica completata!")
print("\nDa ora in poi:")
print("- Ogni nuovo cliente avrà automaticamente 'Sede Principale'")
print("- Quando salvi un cliente esistente senza sedi, verrà creata automaticamente")

