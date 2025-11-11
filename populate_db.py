"""
Script per popolare il database con dati di esempio
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
django.setup()

from orders.models import *
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

print("Popolamento database con dati di esempio...")

# Crea SLA
print("\nCreazione SLA...")
sla_basic = SLA.objects.create(
    nome="Basic 8x5 - Solo Materiale",
    descrizione="SLA Base 8x5 con solo invio materiale",
    disponibilita_copertura='8X5',
    tempo_risposta='8H',
    tipo_intervento='SOLO_MATERIALE'
)
sla_advanced = SLA.objects.create(
    nome="Advanced 24x7 - Remoto",
    descrizione="SLA Avanzato con supporto remoto 24x7",
    disponibilita_copertura='24X7',
    tempo_risposta='4H',
    tipo_intervento='REMOTO'
)
sla_premium = SLA.objects.create(
    nome="Premium 24x7 - On-Site",
    descrizione="SLA Premium con intervento on-site 24x7",
    disponibilita_copertura='24X7',
    tempo_risposta='2H',
    tipo_intervento='ON_SITE'
)
sla_nbd = SLA.objects.create(
    nome="NBD On-Site+Remoto",
    descrizione="Next Business Day con supporto on-site e remoto",
    disponibilita_copertura='NBD',
    tempo_risposta='NBD',
    tipo_intervento='ON_SITE_REMOTO'
)
sla_ultra = SLA.objects.create(
    nome="Ultra Premium 1h",
    descrizione="Risposta entro 1 ora, copertura 24x7",
    disponibilita_copertura='24X7',
    tempo_risposta='1H',
    tipo_intervento='ON_SITE_REMOTO'
)
print(f"✓ Creati {SLA.objects.count()} SLA")

# Crea Fornitori
print("\nCreazione Fornitori...")
fornitore1 = Fornitore.objects.create(
    nome="Dell Technologies",
    commerciale_riferimento="Mario Rossi",
    email="mario.rossi@dell.com",
    telefono="+39 02 1234567"
)
fornitore2 = Fornitore.objects.create(
    nome="HP Inc.",
    commerciale_riferimento="Laura Bianchi",
    email="laura.bianchi@hp.com",
    telefono="+39 02 7654321"
)
fornitore3 = Fornitore.objects.create(
    nome="Lenovo",
    commerciale_riferimento="Giuseppe Verdi",
    email="giuseppe.verdi@lenovo.com",
    telefono="+39 02 9876543"
)
print(f"✓ Creati {Fornitore.objects.count()} fornitori")

# Crea Clienti
print("\nCreazione Clienti...")
cliente1 = Cliente.objects.create(nome="Acme Corporation S.p.A.")
SedeCliente.objects.create(
    cliente=cliente1,
    nome_sede="Sede Principale",
    indirizzo="Via Roma 123",
    citta="Milano",
    cap="20100",
    provincia="MI"
)
SedeCliente.objects.create(
    cliente=cliente1,
    nome_sede="Filiale Nord",
    indirizzo="Corso Italia 45",
    citta="Torino",
    cap="10100",
    provincia="TO"
)

cliente2 = Cliente.objects.create(nome="TechSolutions S.r.l.")
SedeCliente.objects.create(
    cliente=cliente2,
    nome_sede="Headquarters",
    indirizzo="Viale Europa 78",
    citta="Roma",
    cap="00100",
    provincia="RM"
)

cliente3 = Cliente.objects.create(nome="Global Systems Italia")
SedeCliente.objects.create(
    cliente=cliente3,
    nome_sede="Ufficio Centrale",
    indirizzo="Piazza Garibaldi 12",
    citta="Bologna",
    cap="40100",
    provincia="BO"
)
print(f"✓ Creati {Cliente.objects.count()} clienti con {SedeCliente.objects.count()} sedi")

# Crea Service Contracts
print("\nCreazione Service Contracts...")
sc1 = ServiceContract.objects.create(
    numero_contratto="SC-2024-001",
    cliente=cliente1,
    sla=sla_premium,
    data_inizio=date.today() - timedelta(days=90),
    data_fine=date.today() + timedelta(days=275),
    attivo=True,
    note="Contratto Premium per sede principale"
)
sc2 = ServiceContract.objects.create(
    numero_contratto="SC-2024-002",
    cliente=cliente2,
    sla=sla_advanced,
    data_inizio=date.today() - timedelta(days=60),
    data_fine=date.today() + timedelta(days=20),  # In scadenza tra 20 giorni
    attivo=True,
    note="Contratto in scadenza - da rinnovare"
)
print(f"✓ Creati {ServiceContract.objects.count()} service contracts")

# Prima popola il catalogo articoli
print("\nPopolamento catalogo articoli...")
import subprocess
subprocess.run(['python', 'populate_articoli.py'], check=False)

# Ricarica gli articoli
from orders.models import Articolo
articoli_catalogo = {a.codice_articolo: a for a in Articolo.objects.all()}

# Crea Ordini
print("\nCreazione Ordini...")
sedi = list(SedeCliente.objects.all())

if not articoli_catalogo:
    print("  ⚠️  ATTENZIONE: Nessun articolo nel catalogo!")
    print("  Esegui prima: python populate_articoli.py")
    import sys
    sys.exit(1)

# Ordine 1 - Dell
ordine1 = Ordine.objects.create(
    numero_ordine="ORD-2024-001",
    fornitore=fornitore1,
    data_ordine=date.today() - timedelta(days=180),
    tipo_ordine='STANDARD',
    note="Ordine iniziale workstation"
)

if 'DELL-PRE-3660' in articoli_catalogo:
    ArticoloOrdine.objects.create(
        ordine=ordine1,
        articolo=articoli_catalogo['DELL-PRE-3660'],
        numero_seriale="SN-DELL-PRE-001",
        quantita=1,
        sede_cliente=sedi[0],
        mesi_garanzia=36,
        note="Configurazione custom: RAM upgraded a 32GB"
    )

if 'DELL-MON-P2422H' in articoli_catalogo:
    ArticoloOrdine.objects.create(
        ordine=ordine1,
        articolo=articoli_catalogo['DELL-MON-P2422H'],
        numero_seriale="SN-DELL-MON-001",
        quantita=1,
        sede_cliente=sedi[0],
        mesi_garanzia=24
    )

# Ordine 2 - HP
ordine2 = Ordine.objects.create(
    numero_ordine="ORD-2024-002",
    fornitore=fornitore2,
    data_ordine=date.today() - timedelta(days=150),
    tipo_ordine='STANDARD'
)

if 'HP-ELITE-840G9' in articoli_catalogo:
    ArticoloOrdine.objects.create(
        ordine=ordine2,
        articolo=articoli_catalogo['HP-ELITE-840G9'],
        numero_seriale="SN-HP-ELITE-001",
        quantita=1,
        sede_cliente=sedi[1],
        mesi_garanzia=12,
        note="Richiesta tastiera layout US"
    )

# Ordine 3 - Lenovo con Service Contract
ordine3 = Ordine.objects.create(
    numero_ordine="ORD-2024-003",
    fornitore=fornitore3,
    data_ordine=date.today() - timedelta(days=120),
    tipo_ordine='STANDARD'
)

if 'LEN-M90T-G3' in articoli_catalogo:
    ArticoloOrdine.objects.create(
        ordine=ordine3,
        articolo=articoli_catalogo['LEN-M90T-G3'],
        numero_seriale="SN-LEN-M90T-001",
        quantita=1,
        sede_cliente=sedi[2],
        service_contract=sc1,  # Associato a service contract
        note="Con service contract Premium 24x7"
    )

# Ordine 4 - Dell con articolo in scadenza garanzia
ordine4 = Ordine.objects.create(
    numero_ordine="ORD-2024-004",
    fornitore=fornitore1,
    data_ordine=date.today() - timedelta(days=350),  # Quasi un anno fa
    tipo_ordine='STANDARD'
)

art_scadenza = None
if 'DELL-LAT-5430' in articoli_catalogo:
    art_scadenza = ArticoloOrdine.objects.create(
        ordine=ordine4,
        articolo=articoli_catalogo['DELL-LAT-5430'],
        numero_seriale="SN-DELL-LAT-002",
        quantita=1,
        sede_cliente=sedi[0],
        mesi_garanzia=12,  # In scadenza tra poco
        note="Garanzia in scadenza - possibile rinnovo"
    )

# Ordine 5 - Articoli senza seriale
ordine5 = Ordine.objects.create(
    numero_ordine="ORD-2024-005",
    fornitore=fornitore2,
    data_ordine=date.today() - timedelta(days=30),
    tipo_ordine='STANDARD'
)

if 'ACC-KB-WIRELESS' in articoli_catalogo:
    ArticoloOrdine.objects.create(
        ordine=ordine5,
        articolo=articoli_catalogo['ACC-KB-WIRELESS'],
        numero_seriale=None,  # Senza seriale
        quantita=5,
        sede_cliente=sedi[2],
        mesi_garanzia=12
    )

if 'ACC-MOUSE-WIRELESS' in articoli_catalogo:
    ArticoloOrdine.objects.create(
        ordine=ordine5,
        articolo=articoli_catalogo['ACC-MOUSE-WIRELESS'],
        numero_seriale=None,
        quantita=5,
        sede_cliente=sedi[2],
        mesi_garanzia=12
    )

print(f"✓ Creati {Ordine.objects.count()} ordini con {ArticoloOrdine.objects.count()} articoli")

# Crea un RMA
print("\nCreazione RMA...")
if art_scadenza:
    rma1 = RMA.objects.create(
        numero_rma="RMA-2024-001",
        articolo_originale=art_scadenza,
        motivo="Schermo difettoso - pixel morti",
        stato='APERTO',
        override_garanzia=False
    )

    # Crea ordine fornitore collegato all'RMA
    ordine_rma = Ordine.objects.create(
        numero_ordine="ORD-RMA-2024-001",
        fornitore=fornitore1,
        data_ordine=date.today(),
        tipo_ordine='RMA',
        ordine_originale_rma=ordine4,
        note=f"Ordine RMA per {rma1.numero_rma}"
    )

    rma1.ordine_fornitore = ordine_rma
    rma1.save()

    print(f"✓ Creati {RMA.objects.count()} RMA")
else:
    print("⚠️  RMA non creato (articolo di scadenza non presente)")

# Crea ordine di rinnovo garanzia
print("\nCreazione Ordine Rinnovo Garanzia...")
ordine_estensione = Ordine.objects.create(
    numero_ordine="ORD-2024-EXT-001",
    fornitore=fornitore1,
    data_ordine=date.today() - timedelta(days=5),
    tipo_ordine='RINNOVO_GARANZIA',
    ordine_materiale_collegato=ordine1
)

if 'GAR-DELL-2Y' in articoli_catalogo:
    ArticoloOrdine.objects.create(
        ordine=ordine_estensione,
        articolo=articoli_catalogo['GAR-DELL-2Y'],
        numero_seriale=None,
        quantita=1,
        sede_cliente=sedi[0],
        mesi_garanzia=24,
        note="Estensione per Dell Precision 3660 SN-DELL-PRE-001"
    )

print("✓ Creato ordine rinnovo garanzia")

print("\n" + "="*50)
print("RIEPILOGO DATI CREATI:")
print("="*50)
print(f"SLA: {SLA.objects.count()}")
print(f"Fornitori: {Fornitore.objects.count()}")
print(f"Clienti: {Cliente.objects.count()}")
print(f"Sedi Clienti: {SedeCliente.objects.count()}")
print(f"Service Contracts: {ServiceContract.objects.count()}")
print(f"Ordini: {Ordine.objects.count()}")
print(f"Articoli: {ArticoloOrdine.objects.count()}")
print(f"RMA: {RMA.objects.count()}")
print("="*50)
print("\n✅ Database popolato con successo!")
print("\nPuoi ora accedere all'admin Django per gestire i dati.")
print("Per creare un superuser: python manage.py createsuperuser")

