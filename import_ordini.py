"""
Script one-shot per importare ordini da CSV

Formato CSV (senza intestazione):
data,numero_ordine,fornitore,part_number,descrizione,sn,cliente,mesi_garanzia,quantita,note

Esempio:
2024-01-15,ORD-001,Dell,ABC123,Server Dell,SN12345,Acme Corp,36,1,Note esempio

IMPORTANTE:
- Clienti, Fornitori e Articoli devono GIÀ ESISTERE nel database
- Le righe non importabili verranno segnalate con il motivo
"""

import os
import sys
import django
import csv
from datetime import datetime
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
django.setup()

from orders.models import Ordine, ArticoloOrdine, Cliente, Fornitore, Articolo, SedeCliente
from django.db import transaction


def parse_date(date_str):
    """Parse data in vari formati"""
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def import_ordini_csv(csv_file_path, dry_run=False):
    """Importa ordini da file CSV

    Args:
        csv_file_path: Percorso del file CSV
        dry_run: Se True, simula l'import senza salvare nel DB
    """

    if dry_run:
        print("🔍 MODALITÀ DRY-RUN: Simulazione import senza salvare nel database\n")

    print(f"📥 Inizio importazione da: {csv_file_path}\n")

    # Contatori
    ordini_creati = 0
    articoli_creati = 0
    ordini_aggiornati = 0
    righe_saltate = []
    ordini_processati = {}  # {numero_ordine: ordine_obj}

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            for line_number, row in enumerate(csv_reader, start=1):
                # Salta righe vuote
                if not row or len(row) < 10:
                    if row:  # Solo se la riga ha qualche dato
                        righe_saltate.append({
                            'line': line_number,
                            'data': row,
                            'error': f'Numero campi insufficiente (attesi 10, trovati {len(row)})'
                        })
                    continue

                # Estrai campi
                data_str, numero_ordine, fornitore_nome, part_number, descrizione, sn, cliente_nome, mesi_garanzia_str, quantita_str, note = [x.strip() for x in row]

                errors = []

                # 1. Valida e parse data
                data_ordine = parse_date(data_str)
                if not data_ordine:
                    errors.append(f"Data non valida: '{data_str}'")

                # 2. Valida numero ordine
                if not numero_ordine:
                    errors.append("Numero ordine vuoto")

                # 3. Cerca fornitore
                fornitore = None
                if fornitore_nome:
                    fornitore = Fornitore.objects.filter(nome__iexact=fornitore_nome).first()
                    if not fornitore:
                        errors.append(f"Fornitore '{fornitore_nome}' non trovato")
                else:
                    errors.append("Fornitore vuoto")

                # 4. Cerca articolo
                articolo = None
                if part_number:
                    articolo = Articolo.objects.filter(codice_articolo__iexact=part_number.upper()).first()
                    if not articolo:
                        errors.append(f"Articolo '{part_number}' non trovato")
                else:
                    errors.append("Part number vuoto")

                # 5. Cerca cliente e sede
                cliente = None
                sede_default = None
                cliente_nome_ricerca = cliente_nome  # Memorizza per messaggi errore
                nome_sede_specifica = None

                if cliente_nome:
                    # Prova a parsare formato "CLIENTE - SEDE" (es: "EMPSOL - DC")
                    if ' - ' in cliente_nome:
                        # Formato "CLIENTE - SEDE" rilevato (con trattino)
                        parts = cliente_nome.split(' - ', 1)
                        cliente_nome_solo = parts[0].strip()
                        nome_sede_specifica = parts[1].strip()
                        cliente_nome_ricerca = cliente_nome_solo  # Usa solo la parte cliente per errori

                        # Cerca cliente
                        cliente = Cliente.objects.filter(nome__iexact=cliente_nome_solo).first()
                        if not cliente:
                            # Prova anche con il nome completo come fallback
                            cliente = Cliente.objects.filter(nome__iexact=cliente_nome).first()
                            if cliente:
                                # Era un nome completo con trattino nel nome, non formato "CLIENTE - SEDE"
                                nome_sede_specifica = None
                                cliente_nome_ricerca = cliente_nome
                    else:
                        # Nome semplice senza sede (nessun trattino)
                        cliente = Cliente.objects.filter(nome__iexact=cliente_nome).first()

                    if not cliente:
                        if nome_sede_specifica:
                            errors.append(f"Cliente '{cliente_nome_ricerca}' non trovato (cercato da '{cliente_nome}')")
                        else:
                            errors.append(f"Cliente '{cliente_nome_ricerca}' non trovato")
                    else:
                        # Cerca sede specifica o usa default
                        if nome_sede_specifica:
                            # Cerca sede specifica per nome
                            sede_default = cliente.sedi.filter(nome_sede__iexact=nome_sede_specifica).first()
                            if not sede_default:
                                # Prova ricerca case-insensitive più ampia
                                sede_default = cliente.sedi.filter(nome_sede__icontains=nome_sede_specifica).first()
                            if not sede_default:
                                errors.append(f"Sede '{nome_sede_specifica}' non trovata per cliente '{cliente.nome}'")
                        else:
                            # Prendi la prima sede (o sede principale)
                            sede_default = cliente.sedi.filter(nome_sede__icontains='principale').first() or cliente.sedi.first()
                            if not sede_default:
                                errors.append(f"Nessuna sede trovata per cliente '{cliente.nome}'")
                else:
                    errors.append("Cliente vuoto")

                # 6. Parse mesi garanzia
                mesi_garanzia = 12  # default
                if mesi_garanzia_str:
                    try:
                        mesi_garanzia = int(mesi_garanzia_str)
                        if mesi_garanzia < 0:
                            errors.append(f"Mesi garanzia negativo: {mesi_garanzia_str}")
                    except ValueError:
                        errors.append(f"Mesi garanzia non valido: '{mesi_garanzia_str}'")

                # 7. Parse quantità
                quantita = 1
                if quantita_str:
                    try:
                        quantita = int(quantita_str)
                        if quantita < 1:
                            errors.append(f"Quantità deve essere >= 1: {quantita_str}")
                    except ValueError:
                        errors.append(f"Quantità non valida: '{quantita_str}'")

                # 8. Valida seriale
                if sn and sn != '-':
                    # Verifica univocità seriale
                    existing_sn = ArticoloOrdine.objects.filter(numero_seriale=sn).first()
                    if existing_sn:
                        errors.append(f"Seriale '{sn}' già esistente in ordine {existing_sn.ordine.numero_ordine}")
                    # Se c'è seriale, quantità deve essere 1
                    if quantita != 1:
                        errors.append(f"Con seriale la quantità deve essere 1 (trovata: {quantita})")

                # Se ci sono errori, salta la riga
                if errors:
                    righe_saltate.append({
                        'line': line_number,
                        'data': row,
                        'error': ' | '.join(errors)
                    })
                    continue

                # ✅ TUTTO VALIDO - Procedi con import
                try:
                    if dry_run:
                        # MODALITÀ DRY-RUN: Simula senza salvare
                        if numero_ordine in ordini_processati:
                            print(f"  ↪ [DRY-RUN] Aggiungerebbe articolo a ordine: {numero_ordine}")
                        else:
                            # Verifica se ordine esiste già nel DB
                            ordine_esistente = Ordine.objects.filter(numero_ordine=numero_ordine).first()
                            if ordine_esistente:
                                print(f"  🔄 [DRY-RUN] Ordine {numero_ordine} già esistente, aggiungerebbe articoli")
                                ordini_aggiornati += 1
                            else:
                                print(f"  ✅ [DRY-RUN] Creerebbe ordine: {numero_ordine} - {fornitore.nome} ({data_ordine})")
                                ordini_creati += 1

                            # Segna come processato (simulazione)
                            ordini_processati[numero_ordine] = numero_ordine

                        # Simula creazione articolo
                        from dateutil.relativedelta import relativedelta
                        data_scadenza = data_ordine + relativedelta(months=mesi_garanzia)
                        articoli_creati += 1
                        print(f"    ➕ [DRY-RUN] Aggiungerebbe articolo: {part_number} (SN: {sn if sn else '-'}) x{quantita}")
                        print(f"       Cliente: {cliente.nome} - {sede_default.nome_sede}")
                        print(f"       Garanzia: {mesi_garanzia} mesi (scadenza: {data_scadenza})")
                    else:
                        # MODALITÀ NORMALE: Salva nel database
                        with transaction.atomic():
                            # Crea o recupera ordine
                            ordine = None
                            if numero_ordine in ordini_processati:
                                # Ordine già creato in questo import
                                ordine = ordini_processati[numero_ordine]
                                print(f"  ↪ Aggiungo articolo a ordine esistente: {numero_ordine}")
                            else:
                                # Verifica se ordine esiste già nel DB
                                ordine = Ordine.objects.filter(numero_ordine=numero_ordine).first()
                                if ordine:
                                    print(f"  🔄 Ordine {numero_ordine} già esistente, aggiungo articoli")
                                    ordini_aggiornati += 1
                                else:
                                    # Crea nuovo ordine
                                    ordine = Ordine.objects.create(
                                        numero_ordine=numero_ordine,
                                        fornitore=fornitore,
                                        data_ordine=data_ordine,
                                        tipo_ordine='STANDARD',
                                        sede_default=sede_default,
                                        mesi_garanzia_default=mesi_garanzia,
                                        note=note if note else ''
                                    )
                                    ordini_creati += 1
                                    print(f"  ✅ Ordine creato: {numero_ordine} - {fornitore.nome} ({data_ordine})")

                                ordini_processati[numero_ordine] = ordine

                            # Crea articolo ordine
                            from dateutil.relativedelta import relativedelta
                            data_scadenza = data_ordine + relativedelta(months=mesi_garanzia)

                            articolo_ordine = ArticoloOrdine.objects.create(
                                ordine=ordine,
                                articolo=articolo,
                                numero_seriale=sn if sn and sn != '-' else None,
                                quantita=quantita,
                                sede_cliente=sede_default,
                                mesi_garanzia=mesi_garanzia,
                                data_scadenza_garanzia=data_scadenza,
                                note=note if note else ''
                            )
                            articoli_creati += 1
                            print(f"    ➕ Articolo: {part_number} (SN: {sn if sn else '-'}) x{quantita}")

                except Exception as e:
                    righe_saltate.append({
                        'line': line_number,
                        'data': row,
                        'error': f'Errore durante salvataggio: {str(e)}'
                    })
                    continue

    except FileNotFoundError:
        print(f"❌ ERRORE: File non trovato: {csv_file_path}")
        return
    except Exception as e:
        print(f"❌ ERRORE GENERALE: {str(e)}")
        return

    # Report finale
    print("\n" + "="*80)
    if dry_run:
        print("📊 REPORT SIMULAZIONE (DRY-RUN - Nessuna modifica al database)")
    else:
        print("📊 REPORT IMPORTAZIONE")
    print("="*80)

    if dry_run:
        print(f"✅ Ordini che verrebbero creati: {ordini_creati}")
        print(f"🔄 Ordini che verrebbero aggiornati: {ordini_aggiornati}")
        print(f"➕ Articoli che verrebbero importati: {articoli_creati}")
    else:
        print(f"✅ Ordini creati: {ordini_creati}")
        print(f"🔄 Ordini aggiornati (articoli aggiunti): {ordini_aggiornati}")
        print(f"➕ Articoli importati: {articoli_creati}")

    print(f"❌ Righe saltate: {len(righe_saltate)}")

    if righe_saltate:
        print("\n" + "="*80)
        print("⚠️ RIGHE NON IMPORTATE")
        print("="*80)
        for skip in righe_saltate:
            print(f"\n📍 Riga {skip['line']}:")
            print(f"   Dati: {skip['data']}")
            print(f"   ❌ Errore: {skip['error']}")

    print("\n" + "="*80)
    if dry_run:
        print("✅ SIMULAZIONE COMPLETATA - Nessuna modifica salvata")
        if righe_saltate == 0 or len(righe_saltate) == 0:
            print("\n💡 Tutto OK! Puoi procedere con l'import reale rimuovendo --dry-run")
    else:
        print("✅ IMPORTAZIONE COMPLETATA")
    print("="*80)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("❌ Errore: specificare il percorso del file CSV")
        print("\nUso:")
        print(f"  python {sys.argv[0]} <percorso_file.csv> [--dry-run]")
        print("\nEsempi:")
        print(f"  python {sys.argv[0]} ordini_import.csv --dry-run    # Simula import")
        print(f"  python {sys.argv[0]} ordini_import.csv               # Import reale")
        sys.exit(1)

    csv_file = sys.argv[1]
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv

    if not os.path.exists(csv_file):
        print(f"❌ Errore: File non trovato: {csv_file}")
        sys.exit(1)

    print("="*80)
    if dry_run:
        print("🔍 SIMULAZIONE IMPORT ORDINI DA CSV (DRY-RUN)")
    else:
        print("📦 IMPORT ORDINI DA CSV")
    print("="*80)
    print(f"File: {csv_file}")
    if dry_run:
        print("Modalità: DRY-RUN (nessuna modifica al database)")
    print("\n")

    if not dry_run:
        risposta = input("⚠️  Vuoi procedere con l'importazione REALE? (s/n): ")
        if risposta.lower() != 's':
            print("❌ Importazione annullata")
            sys.exit(0)

    print("\n")
    import_ordini_csv(csv_file, dry_run=dry_run)

