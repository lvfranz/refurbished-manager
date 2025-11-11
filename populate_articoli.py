"""
Script per popolare il catalogo articoli con esempi
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
django.setup()

from orders.models import Articolo

print("="*60)
print("POPOLAMENTO CATALOGO ARTICOLI")
print("="*60)

# Lista articoli di esempio
articoli_data = [
    # Dell
    {
        'codice_articolo': 'DELL-PRE-3660',
        'nome': 'Dell Precision 3660 Tower',
        'descrizione': 'Workstation Tower - Intel Core i7-12700, 32GB RAM DDR4, 512GB SSD NVMe, NVIDIA T400 4GB',
        'categoria': 'Workstation',
        'costruttore': 'Dell',
    },
    {
        'codice_articolo': 'DELL-LAT-5430',
        'nome': 'Dell Latitude 5430',
        'descrizione': 'Laptop Business - Intel Core i5-1245U, 16GB RAM, 256GB SSD, 14" FHD',
        'categoria': 'Laptop',
        'costruttore': 'Dell',
    },
    {
        'codice_articolo': 'DELL-MON-P2422H',
        'nome': 'Dell Monitor P2422H',
        'descrizione': 'Monitor 24 pollici Full HD 1920x1080, IPS, HDMI, DisplayPort, USB Hub',
        'categoria': 'Monitor',
        'costruttore': 'Dell',
    },
    {
        'codice_articolo': 'DELL-OPT-7090',
        'nome': 'Dell OptiPlex 7090 SFF',
        'descrizione': 'Desktop Small Form Factor - Intel Core i5-11500, 16GB RAM, 256GB SSD',
        'categoria': 'Desktop',
        'costruttore': 'Dell',
    },
    
    # HP
    {
        'codice_articolo': 'HP-ELITE-840G9',
        'nome': 'HP EliteBook 840 G9',
        'descrizione': 'Laptop Premium - Intel Core i5-1245U, 16GB RAM, 256GB SSD, 14" FHD Touch',
        'categoria': 'Laptop',
        'costruttore': 'HP',
    },
    {
        'codice_articolo': 'HP-Z2-G9',
        'nome': 'HP Z2 G9 Tower',
        'descrizione': 'Workstation - Intel Core i7-12700K, 32GB RAM, 1TB SSD, NVIDIA RTX A2000',
        'categoria': 'Workstation',
        'costruttore': 'HP',
    },
    {
        'codice_articolo': 'HP-ELITE-800G9',
        'nome': 'HP EliteDesk 800 G9',
        'descrizione': 'Desktop Mini - Intel Core i5-12500, 16GB RAM, 512GB SSD',
        'categoria': 'Desktop',
        'costruttore': 'HP',
    },
    {
        'codice_articolo': 'HP-E24-G5',
        'nome': 'HP E24 G5 FHD Monitor',
        'descrizione': 'Monitor 23.8" Full HD, IPS, HDMI, DisplayPort, VGA',
        'categoria': 'Monitor',
        'costruttore': 'HP',
    },
    
    # Lenovo
    {
        'codice_articolo': 'LEN-P16S-G2',
        'nome': 'Lenovo ThinkPad P16s Gen 2',
        'descrizione': 'Mobile Workstation - Intel Core i7-1370P, 32GB RAM, 1TB SSD, NVIDIA T550',
        'categoria': 'Laptop',
        'costruttore': 'Lenovo',
    },
    {
        'codice_articolo': 'LEN-M90T-G3',
        'nome': 'Lenovo ThinkCentre M90t Gen 3',
        'descrizione': 'Desktop Tower - Intel Core i7-12700, 16GB RAM, 512GB SSD',
        'categoria': 'Desktop',
        'costruttore': 'Lenovo',
    },
    {
        'codice_articolo': 'LEN-P3-TWR',
        'nome': 'Lenovo ThinkStation P3 Tower',
        'descrizione': 'Workstation - Intel Core i9-13900K, 64GB RAM, 2TB SSD, NVIDIA RTX A4000',
        'categoria': 'Workstation',
        'costruttore': 'Lenovo',
    },
    {
        'codice_articolo': 'LEN-L24E-30',
        'nome': 'Lenovo L24e-30',
        'descrizione': 'Monitor 23.8" Full HD, VA Panel, HDMI, VGA, FreeSync',
        'categoria': 'Monitor',
        'costruttore': 'Lenovo',
    },
    
    # Accessori
    {
        'codice_articolo': 'ACC-KB-WIRELESS',
        'nome': 'Tastiera Wireless Professionale',
        'descrizione': 'Tastiera wireless full-size, layout italiano, batteria ricaricabile',
        'categoria': 'Accessori',
        'costruttore': 'Generic',
    },
    {
        'codice_articolo': 'ACC-MOUSE-WIRELESS',
        'nome': 'Mouse Wireless Ergonomico',
        'descrizione': 'Mouse wireless ergonomico, 1600 DPI, 5 pulsanti programmabili',
        'categoria': 'Accessori',
        'costruttore': 'Generic',
    },
    {
        'codice_articolo': 'ACC-DOCK-USB-C',
        'nome': 'Docking Station USB-C',
        'descrizione': 'Docking Station USB-C con 2x HDMI, 4x USB 3.0, Ethernet, Power Delivery 100W',
        'categoria': 'Accessori',
        'costruttore': 'Generic',
    },
    
    # Estensioni Garanzia
    {
        'codice_articolo': 'GAR-DELL-2Y',
        'nome': 'Estensione Garanzia Dell 2 anni',
        'descrizione': 'Estensione garanzia Dell da 1 a 3 anni totali, NBD On-Site',
        'categoria': 'Garanzia',
        'costruttore': 'Dell',
    },
    {
        'codice_articolo': 'GAR-HP-3Y',
        'nome': 'Estensione Garanzia HP 3 anni',
        'descrizione': 'Estensione garanzia HP da 1 a 4 anni totali, NBD On-Site',
        'categoria': 'Garanzia',
        'costruttore': 'HP',
    },
    {
        'codice_articolo': 'GAR-LEN-5Y',
        'nome': 'Estensione Garanzia Lenovo 5 anni',
        'descrizione': 'Estensione garanzia Lenovo da 1 a 6 anni totali, 24x7 4h On-Site',
        'categoria': 'Garanzia',
        'costruttore': 'Lenovo',
    },
]

print(f"\nCreazione {len(articoli_data)} articoli nel catalogo...")

created = 0
updated = 0

for data in articoli_data:
    articolo, created_flag = Articolo.objects.update_or_create(
        codice_articolo=data['codice_articolo'],
        defaults=data
    )
    
    if created_flag:
        created += 1
        print(f"  ✓ Creato: {articolo.codice_articolo} - {articolo.nome}")
    else:
        updated += 1
        print(f"  ↻ Aggiornato: {articolo.codice_articolo} - {articolo.nome}")

print("\n" + "="*60)
print("RIEPILOGO CATALOGO ARTICOLI")
print("="*60)
print(f"Articoli creati: {created}")
print(f"Articoli aggiornati: {updated}")
print(f"Totale articoli: {Articolo.objects.count()}")

# Statistiche per categoria
print("\nArticoli per categoria:")
from django.db.models import Count
categorie = Articolo.objects.values('categoria').annotate(count=Count('id')).order_by('-count')
for cat in categorie:
    print(f"  - {cat['categoria']}: {cat['count']}")

print("\nArticoli per costruttore:")
costruttori = Articolo.objects.values('costruttore').annotate(count=Count('id')).order_by('-count')
for cost in costruttori:
    print(f"  - {cost['costruttore']}: {cost['count']}")

print("\n✅ Catalogo articoli popolato con successo!")
print("\nPuoi ora:")
print("1. Vedere gli articoli in: http://127.0.0.1:8000/admin/orders/articolo/")
print("2. Creare ordini selezionando articoli dal catalogo")
print("3. Aggiungere note personalizzate per ogni articolo nell'ordine")

