"""
Management command per inviare notifiche di scadenza garanzie
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from orders.models import ArticoloOrdine, ServiceContract


class Command(BaseCommand):
    help = 'Invia email di notifica per scadenze garanzie e service contract'

    def add_arguments(self, parser):
        parser.add_argument(
            '--giorni',
            type=int,
            default=30,
            help='Numero giorni prima della scadenza per inviare notifica (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula invio senza inviare realmente le email'
        )

    def handle(self, *args, **options):
        giorni = options['giorni']
        dry_run = options['dry_run']

        oggi = timezone.now().date()
        data_limite = oggi + timedelta(days=giorni)

        self.stdout.write(self.style.SUCCESS(f'Controllo scadenze fino al {data_limite}'))

        # Trova articoli in scadenza
        articoli_scadenza = ArticoloOrdine.objects.filter(
            data_scadenza_garanzia__lte=data_limite,
            data_scadenza_garanzia__gte=oggi,
            service_contract__isnull=True  # Solo con garanzia standard
        ).select_related('articolo', 'ordine', 'sede_cliente__cliente')

        # Trova service contract in scadenza
        contracts_scadenza = ServiceContract.objects.filter(
            data_fine__lte=data_limite,
            data_fine__gte=oggi,
            attivo=True
        ).select_related('cliente', 'sla')

        self.stdout.write(f'Trovati {articoli_scadenza.count()} articoli in scadenza')
        self.stdout.write(f'Trovati {contracts_scadenza.count()} service contract in scadenza')

        # Raggruppa per cliente
        notifiche = {}

        for articolo in articoli_scadenza:
            if articolo.sede_cliente:
                cliente_nome = articolo.sede_cliente.cliente.nome
                if cliente_nome not in notifiche:
                    notifiche[cliente_nome] = {
                        'articoli': [],
                        'contracts': []
                    }
                notifiche[cliente_nome]['articoli'].append(articolo)

        for contract in contracts_scadenza:
            cliente_nome = contract.cliente.nome
            if cliente_nome not in notifiche:
                notifiche[cliente_nome] = {
                    'articoli': [],
                    'contracts': []
                }
            notifiche[cliente_nome]['contracts'].append(contract)

        # Invia email
        email_inviate = 0
        for cliente, dati in notifiche.items():
            if self.invia_email_scadenze(cliente, dati, dry_run):
                email_inviate += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] {email_inviate} email sarebbero state inviate'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ {email_inviate} email inviate con successo'))

    def invia_email_scadenze(self, cliente_nome, dati, dry_run=False):
        """Invia email di notifica scadenze"""

        # Costruisci messaggio
        subject = f'Notifica Scadenze Garanzie - {cliente_nome}'

        message = f"""
Gentile Cliente {cliente_nome},

Con la presente vi informiamo che le seguenti garanzie/contratti sono in scadenza:

"""

        if dati['articoli']:
            message += "ARTICOLI IN SCADENZA GARANZIA:\n"
            message += "="*50 + "\n"
            for art in dati['articoli']:
                message += f"""
Articolo: {art.articolo.codice_articolo}
Seriale: {art.numero_seriale or 'N/A'}
Ordine: {art.ordine.numero_ordine}
Scadenza: {art.data_scadenza_garanzia.strftime('%d/%m/%Y')}
Sede: {art.sede_cliente.nome_sede if art.sede_cliente else 'N/A'}

"""

        if dati['contracts']:
            message += "\nSERVICE CONTRACT IN SCADENZA:\n"
            message += "="*50 + "\n"
            for contract in dati['contracts']:
                message += f"""
Contratto: {contract.numero_contratto}
SLA: {contract.sla.nome}
Scadenza: {contract.data_fine.strftime('%d/%m/%Y')}

"""

        message += """
Vi preghiamo di contattarci per il rinnovo o per eventuali chiarimenti.

Cordiali saluti,
Team Gestionale Refurbished
"""

        if dry_run:
            self.stdout.write(f'\n[DRY RUN] Email per {cliente_nome}:')
            self.stdout.write(f'Subject: {subject}')
            self.stdout.write(f'Articoli: {len(dati["articoli"])}')
            self.stdout.write(f'Contracts: {len(dati["contracts"])}')
            return True

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # TODO: usare email cliente
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Email inviata a {cliente_nome}'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Errore invio email a {cliente_nome}: {e}'))
            return False

