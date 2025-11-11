"""
Script per migrare i dati da articolo CharField a ForeignKey Articolo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
django.setup()

from orders.models import ArticoloOrdine
from django.db import connection

print("="*60)
print("PULIZIA DATI PER MIGRAZIONE ARTICOLO")
print("="*60)

# Conta articoli esistenti
count = ArticoloOrdine.objects.count()
print(f"\nArticoli ordini da rimuovere: {count}")

if count > 0:
    risposta = input("\n⚠️  ATTENZIONE: Questo eliminerà tutti gli articoli ordini esistenti!\nContinuare? (si/no): ")
    
    if risposta.lower() == 'si':
        # Elimina tutti gli articoli ordini
        ArticoloOrdine.objects.all().delete()
        print(f"✓ Eliminati {count} articoli ordini")
        
        # Reset auto-increment
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE orders_articoloordine AUTO_INCREMENT = 1")
        print("✓ Reset contatore ID")
        
        print("\n✅ Pulizia completata!")
        print("\nOra puoi:")
        print("1. Applicare le migrazioni: python manage.py migrate")
        print("2. Popolare il catalogo: python populate_articoli.py")
        print("3. Popolare il database: python populate_db.py")
    else:
        print("\n❌ Operazione annullata")
else:
    print("\n✓ Nessun articolo ordine presente")
    print("\nPuoi procedere con:")
    print("1. python manage.py migrate")
    print("2. python populate_articoli.py")
    print("3. python populate_db.py")

