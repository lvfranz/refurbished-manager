"""
Script helper per creare cliente EMPSOL con sedi
Eseguire UNA VOLTA prima dell'import ordini
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
django.setup()

from orders.models import Cliente, SedeCliente

def crea_cliente_empsol():
    """Crea cliente EMPSOL con sedi DC, Milano, Roma"""
    
    print("="*80)
    print("🏢 CREAZIONE CLIENTE EMPSOL CON SEDI")
    print("="*80)
    
    # Verifica se esiste già
    cliente_esistente = Cliente.objects.filter(nome__iexact='EMPSOL').first()
    if cliente_esistente:
        print(f"⚠️  Cliente EMPSOL già esistente (ID: {cliente_esistente.id})")
        print(f"   Sedi attuali: {cliente_esistente.sedi.count()}")
        
        risposta = input("\n❓ Vuoi aggiungere sedi mancanti? (s/n): ")
        if risposta.lower() != 's':
            print("❌ Operazione annullata")
            return
        
        cliente = cliente_esistente
    else:
        # Crea cliente
        cliente = Cliente.objects.create(nome='EMPSOL')
        print(f"✅ Cliente EMPSOL creato (ID: {cliente.id})")
    
    # Sedi da creare
    sedi_da_creare = [
        {'nome': 'DC', 'citta': '', 'indirizzo': ''},
        {'nome': 'Milano', 'citta': 'Milano', 'indirizzo': ''},
        {'nome': 'Roma', 'citta': 'Roma', 'indirizzo': ''},
        {'nome': 'Sede Principale', 'citta': '', 'indirizzo': ''},
    ]
    
    sedi_create = 0
    sedi_esistenti = 0
    
    for sede_info in sedi_da_creare:
        nome = sede_info['nome']
        
        # Verifica se esiste già
        sede_esistente = cliente.sedi.filter(nome_sede__iexact=nome).first()
        if sede_esistente:
            print(f"   ↪ Sede '{nome}' già esistente")
            sedi_esistenti += 1
        else:
            # Crea sede
            SedeCliente.objects.create(
                cliente=cliente,
                nome_sede=nome,
                citta=sede_info['citta'],
                indirizzo=sede_info['indirizzo']
            )
            print(f"   ✅ Sede '{nome}' creata")
            sedi_create += 1
    
    print("\n" + "="*80)
    print("📊 RIEPILOGO")
    print("="*80)
    print(f"Cliente: {cliente.nome}")
    print(f"Sedi totali: {cliente.sedi.count()}")
    print(f"Sedi create ora: {sedi_create}")
    print(f"Sedi già esistenti: {sedi_esistenti}")
    print("\n📋 Elenco sedi:")
    for sede in cliente.sedi.all():
        print(f"   - {sede.nome_sede}")
    
    print("\n" + "="*80)
    print("✅ OPERAZIONE COMPLETATA")
    print("="*80)
    print("\n💡 Ora puoi eseguire l'import ordini con:")
    print("   python import_ordini.py ordini_test_trattino.csv --dry-run")


if __name__ == '__main__':
    crea_cliente_empsol()

