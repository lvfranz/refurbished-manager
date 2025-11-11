"""
Script per migrare i dati da tempo_risposta_ore (IntegerField) a tempo_risposta (CharField con choices)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
django.setup()

from orders.models import SLA

print("="*60)
print("MIGRAZIONE CAMPO TEMPO_RISPOSTA")
print("="*60)

# Mappa ore → codice choice
MAPPING = {
    1: '1H',
    2: '2H',
    4: '4H',
    8: '8H',
    24: 'NBD',  # 24 ore o più diventa NBD
}

slas = SLA.objects.all()
print(f"\nTrovati {slas.count()} SLA da migrare...")

for sla in slas:
    if hasattr(sla, 'tempo_risposta_ore'):
        ore = sla.tempo_risposta_ore
        
        # Trova il mapping più vicino
        if ore in MAPPING:
            nuovo_valore = MAPPING[ore]
        elif ore >= 24:
            nuovo_valore = 'NBD'
        elif ore >= 8:
            nuovo_valore = '8H'
        elif ore >= 4:
            nuovo_valore = '4H'
        elif ore >= 2:
            nuovo_valore = '2H'
        else:
            nuovo_valore = '1H'
        
        sla.tempo_risposta = nuovo_valore
        sla.save()
        
        print(f"  ✓ {sla.nome}: {ore}h → {nuovo_valore}")
    else:
        print(f"  ⚠ {sla.nome}: campo tempo_risposta_ore non trovato")

print("\n✅ Migrazione completata!")
print("\nOra puoi:")
print("1. Creare una migrazione per rimuovere tempo_risposta_ore")
print("2. Applicare le migrazioni: python manage.py migrate")

