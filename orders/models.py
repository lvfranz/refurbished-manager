from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class Articolo(models.Model):
    """Catalogo articoli con descrizioni predefinite"""
    codice_articolo = models.CharField(max_length=100, unique=True, verbose_name="Codice Articolo")
    descrizione = models.TextField(verbose_name="Descrizione")
    categoria = models.CharField(max_length=100, blank=True, verbose_name="Categoria")
    costruttore = models.CharField(max_length=100, blank=True, verbose_name="Costruttore")
    attivo = models.BooleanField(default=True, verbose_name="Attivo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Articolo"
        verbose_name_plural = "Articoli"
        ordering = ['codice_articolo']

    def __str__(self):
        # Mostra codice + inizio descrizione nel dropdown
        desc_short = self.descrizione[:60] + '...' if len(self.descrizione) > 60 else self.descrizione
        return f"{self.codice_articolo} - {desc_short}"


class Cliente(models.Model):
    """Cliente con nome e sedi associate"""
    nome = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clienti"
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Verifica sempre che il cliente abbia almeno una sede
        # Crea "Sede Principale" se non esistono sedi
        if not self.sedi.exists():
            from orders.models import SedeCliente
            SedeCliente.objects.create(
                cliente=self,
                nome_sede="Sede Principale",
                indirizzo=""
            )


class SedeCliente(models.Model):
    """Sede del cliente con indirizzo"""
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='sedi')
    nome_sede = models.CharField(max_length=200)
    indirizzo = models.TextField(blank=True)  # Non obbligatorio
    citta = models.CharField(max_length=100, blank=True)
    cap = models.CharField(max_length=10, blank=True)
    provincia = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sede Cliente"
        verbose_name_plural = "Sedi Clienti"
        ordering = ['cliente__nome', 'nome_sede']

    def __str__(self):
        return f"{self.cliente.nome} - {self.nome_sede}"


class Fornitore(models.Model):
    """Fornitore con riferimento commerciale"""
    nome = models.CharField(max_length=200, unique=True)
    commerciale_riferimento = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fornitore"
        verbose_name_plural = "Fornitori"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class SLA(models.Model):
    """SLA predefiniti per i service contract"""
    DISPONIBILITA_CHOICES = [
        ('8X5', '8x5 (Lun-Ven, 8:00-18:00)'),
        ('9X5', '9x5 (Lun-Ven, 8:00-17:00)'),
        ('12X5', '12x5 (Lun-Ven, 8:00-20:00)'),
        ('24X7', '24x7 (24 ore su 24, 7 giorni su 7)'),
        ('NBD', 'NBD (Next Business Day)'),
    ]

    TIPO_INTERVENTO_CHOICES = [
        ('SOLO_MATERIALE', 'Solo Materiale'),
        ('ON_SITE', 'Intervento On-Site'),
        ('REMOTO', 'Intervento Remoto'),
        ('ON_SITE_REMOTO', 'On-Site + Remoto'),
    ]

    TEMPO_RISPOSTA_CHOICES = [
        ('1H', '1 ora'),
        ('2H', '2 ore'),
        ('4H', '4 ore'),
        ('8H', '8 ore'),
        ('24H', '24 ore'),
        ('NBD', 'NBD (Next Business Day)'),
    ]

    nome = models.CharField(max_length=100, unique=True)
    descrizione = models.TextField(blank=True)

    # Disponibilità copertura
    disponibilita_copertura = models.CharField(
        max_length=10,
        choices=DISPONIBILITA_CHOICES,
        default='8X5',
        help_text="Disponibilità della copertura"
    )

    # Tempo di risposta - ora può essere anche NBD
    tempo_risposta = models.CharField(
        max_length=10,
        choices=TEMPO_RISPOSTA_CHOICES,
        default='8H',
        help_text="Tempo di risposta"
    )

    # Tipo di intervento
    tipo_intervento = models.CharField(
        max_length=20,
        choices=TIPO_INTERVENTO_CHOICES,
        default='SOLO_MATERIALE',
        help_text="Tipo di intervento previsto"
    )

    class Meta:
        verbose_name = "SLA"
        verbose_name_plural = "SLA"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.get_disponibilita_copertura_display()} - {self.get_tipo_intervento_display()}"


class ServiceContract(models.Model):
    """Service Contract per gli articoli"""
    numero_contratto = models.CharField(max_length=100, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='service_contracts')
    sla = models.ForeignKey(SLA, on_delete=models.PROTECT, related_name='contracts')
    data_inizio = models.DateField()
    data_fine = models.DateField()
    note = models.TextField(blank=True)
    attivo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service Contract"
        verbose_name_plural = "Service Contracts"
        ordering = ['-data_inizio']

    def __str__(self):
        return f"{self.numero_contratto} - {self.cliente.nome}"

    def is_valid(self):
        """Verifica se il contratto è valido"""
        return self.attivo and self.data_inizio <= timezone.now().date() <= self.data_fine


class RinnovoServiceContract(models.Model):
    """Rinnovo di un service contract"""
    contract_originale = models.ForeignKey(
        ServiceContract,
        on_delete=models.CASCADE,
        related_name='rinnovi'
    )
    contract_nuovo = models.ForeignKey(
        ServiceContract,
        on_delete=models.CASCADE,
        related_name='rinnovo_di'
    )
    data_rinnovo = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = "Rinnovo Service Contract"
        verbose_name_plural = "Rinnovi Service Contracts"

    def __str__(self):
        return f"Rinnovo: {self.contract_originale.numero_contratto} → {self.contract_nuovo.numero_contratto}"


class Ordine(models.Model):
    """Ordine fornitore"""
    TIPO_ORDINE_CHOICES = [
        ('STANDARD', 'Ordine Standard'),
        ('RMA', 'RMA'),
        ('RINNOVO_GARANZIA', 'Rinnovo Garanzia'),
    ]

    numero_ordine = models.CharField(max_length=100, unique=True)
    richiesta_offerta = models.ForeignKey(
        'RichiestaOfferta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Offerta di Riferimento",
        help_text="Seleziona offerta approvata",
        limit_choices_to={'stato__in': ['APPROVATA', 'CONVERTITA']}
    )
    fornitore = models.ForeignKey(Fornitore, on_delete=models.PROTECT, related_name='ordini')
    data_ordine = models.DateField()
    tipo_ordine = models.CharField(max_length=20, choices=TIPO_ORDINE_CHOICES, default='STANDARD')
    sede_default = models.ForeignKey(
        'SedeCliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sede Default",
        help_text="⚠️ OBBLIGATORIO per ordini Standard. Per RMA/Rinnovo viene ereditato dall'ordine di riferimento."
    )
    mesi_garanzia_default = models.IntegerField(default=12, help_text="Mesi di garanzia di default per gli articoli di questo ordine", verbose_name="Garanzia Default (mesi)")
    pdf_ordine = models.FileField(upload_to='ordini_pdf/', blank=True, null=True, verbose_name="PDF Ordine", help_text="Upload del documento PDF dell'ordine")
    note = models.TextField(blank=True)

    # Relazioni per ordini speciali
    ordine_originale_rma = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordini_rma'
    )
    ordine_materiale_collegato = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordini_estensione_garanzia'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ordine"
        verbose_name_plural = "Ordini"
        ordering = ['-data_ordine']

    def __str__(self):
        return f"{self.numero_ordine} - {self.fornitore.nome} ({self.data_ordine})"

    def get_cliente(self):
        """Ritorna il cliente associato tramite sede_default"""
        if self.sede_default:
            return self.sede_default.cliente
        return None


class ArticoloOrdine(models.Model):
    """Articolo all'interno di un ordine"""
    ordine = models.ForeignKey(Ordine, on_delete=models.CASCADE, related_name='articoli')

    # Articolo dal catalogo
    articolo = models.ForeignKey(
        Articolo,
        on_delete=models.PROTECT,
        related_name='ordini',
        verbose_name="Articolo"
    )

    # Note personalizzate per questo specifico articolo nell'ordine
    note = models.TextField(
        blank=True,
        verbose_name="Note",
        help_text="Note personalizzate per questo articolo nell'ordine"
    )

    # Numero seriale - UNIVOCO in tutto il sistema
    numero_seriale = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Numero Seriale",
        help_text="Numero seriale univoco (se presente, quantità = 1)"
    )

    quantita = models.IntegerField(default=1, verbose_name="Quantità")

    # Assegnazione a cliente/sede
    sede_cliente = models.ForeignKey(
        SedeCliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articoli'
    )

    # Garanzia
    mesi_garanzia = models.IntegerField(default=12, help_text="Mesi di garanzia")
    data_scadenza_garanzia = models.DateField(null=True, blank=True)

    # Service Contract (alternativo alla garanzia)
    service_contract = models.ForeignKey(
        ServiceContract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articoli'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Articolo Ordine"
        verbose_name_plural = "Articoli Ordini"
        ordering = ['-ordine__data_ordine', 'articolo']

    def __str__(self):
        serial = f" (SN: {self.numero_seriale})" if self.numero_seriale else ""
        return f"{self.articolo.codice_articolo}{serial} - {self.ordine.numero_ordine}"

    def clean(self):
        """Validazione: se c'è seriale, quantità deve essere 1 e seriale deve essere univoco"""
        if self.numero_seriale and self.quantita != 1:
            raise ValidationError({
                'quantita': 'Se è presente il numero seriale, la quantità deve essere 1'
            })

        # Verifica univocità seriale (se presente)
        if self.numero_seriale:
            qs = ArticoloOrdine.objects.filter(numero_seriale=self.numero_seriale)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({
                    'numero_seriale': f'Il numero seriale "{self.numero_seriale}" è già utilizzato in un altro ordine'
                })

        # Validazione coerenza Service Contract con cliente
        if self.service_contract:
            # Determina il cliente di riferimento
            cliente_ref = None
            if self.sede_cliente and self.sede_cliente.cliente:
                cliente_ref = self.sede_cliente.cliente
            elif self.ordine and getattr(self.ordine, 'sede_default', None):
                cliente_ref = self.ordine.sede_default.cliente
            if cliente_ref and self.service_contract.cliente_id != cliente_ref.id:
                raise ValidationError({
                    'service_contract': 'Il service contract selezionato non appartiene al cliente associato all\'articolo/ordine.'
                })

    def save(self, *args, **kwargs):
        # Se c'è seriale, forza quantità a 1
        if self.numero_seriale:
            self.quantita = 1

        is_new = self.pk is None

        if is_new and self.ordine:
            # Applica SEMPRE sede_default se presente e sede_cliente non è già impostata
            if self.ordine.sede_default and not self.sede_cliente_id:
                self.sede_cliente = self.ordine.sede_default

            # Applica SEMPRE mesi_garanzia_default se è ancora il valore di default
            if self.ordine.mesi_garanzia_default and self.mesi_garanzia == 12:
                self.mesi_garanzia = self.ordine.mesi_garanzia_default

        # Calcola data scadenza garanzia (solo se non c'è service contract)
        if not self.service_contract and self.ordine and self.ordine.data_ordine and self.mesi_garanzia:
            if not self.data_scadenza_garanzia:
                self.data_scadenza_garanzia = self.ordine.data_ordine + relativedelta(months=self.mesi_garanzia)

        self.full_clean()
        super().save(*args, **kwargs)

    def get_estensioni_garanzia(self):
        """
        Trova tutti gli ordini di rinnovo garanzia collegati all'ordine di questo articolo.
        Ritorna lista di tuple (ordine_rinnovo, mesi_estensione) ordinate per data.
        """
        if not self.ordine:
            return []

        # Trova tutti gli ordini di rinnovo garanzia che hanno questo ordine come materiale collegato
        ordini_rinnovo = Ordine.objects.filter(
            tipo_ordine='RINNOVO_GARANZIA',
            ordine_materiale_collegato=self.ordine
        ).order_by('data_ordine')

        return [(o, o.mesi_garanzia_default or 0) for o in ordini_rinnovo if o.mesi_garanzia_default]

    def get_data_scadenza_garanzia_estesa(self):
        """
        Calcola la data di scadenza garanzia considerando tutte le estensioni.
        Questo è il metodo da usare per visualizzare la scadenza reale.
        """
        if self.service_contract:
            # Se c'è un service contract, usa quello
            return None

        if not self.data_scadenza_garanzia:
            return None

        # Parti dalla scadenza base
        scadenza = self.data_scadenza_garanzia

        # Aggiungi tutte le estensioni
        estensioni = self.get_estensioni_garanzia()
        for ordine_rinnovo, mesi_estensione in estensioni:
            scadenza = scadenza + relativedelta(months=mesi_estensione)

        return scadenza

    def get_mesi_garanzia_totali(self):
        """
        Calcola i mesi totali di garanzia considerando tutte le estensioni.
        """
        mesi_base = self.mesi_garanzia

        # Aggiungi tutte le estensioni
        estensioni = self.get_estensioni_garanzia()
        for ordine_rinnovo, mesi_estensione in estensioni:
            mesi_base += mesi_estensione

        return mesi_base

    def is_in_garanzia(self):
        """Verifica se l'articolo è in garanzia (considerando le estensioni)"""
        if self.service_contract:
            return self.service_contract.is_valid()

        scadenza_estesa = self.get_data_scadenza_garanzia_estesa()
        if scadenza_estesa:
            return timezone.now().date() <= scadenza_estesa

        return False

    def puo_aprire_rma(self, force=False):
        """Verifica se è possibile aprire un RMA"""
        if force:
            return True
        return self.is_in_garanzia()


class RMA(models.Model):
    """RMA per articoli in garanzia"""
    STATO_CHOICES = [
        ('APERTO', 'Aperto'),
        ('IN_LAVORAZIONE', 'In Lavorazione'),
        ('CHIUSO', 'Chiuso'),
        ('ANNULLATO', 'Annullato'),
    ]

    numero_rma = models.CharField(max_length=100, unique=True)
    articolo_originale = models.ForeignKey(
        ArticoloOrdine,
        on_delete=models.CASCADE,
        related_name='rma_aperti'
    )
    data_apertura = models.DateField(auto_now_add=True)
    motivo = models.TextField()
    stato = models.CharField(max_length=20, choices=STATO_CHOICES, default='APERTO')
    override_garanzia = models.BooleanField(
        default=False,
        help_text="Forza apertura RMA anche se fuori garanzia"
    )

    # Ordine fornitore creato per l'RMA
    ordine_fornitore = models.ForeignKey(
        Ordine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rma'
    )

    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RMA"
        verbose_name_plural = "RMA"
        ordering = ['-data_apertura']

    def __str__(self):
        return f"RMA {self.numero_rma} - {self.articolo_originale.articolo}"

    def clean(self):
        """Validazione: verifica se può aprire RMA"""
        if not self.override_garanzia and not self.articolo_originale.is_in_garanzia():
            raise ValidationError({
                'articolo_originale': 'L\'articolo non è in garanzia. Attivare override per forzare.'
            })


class RichiestaOfferta(models.Model):
    """Richiesta offerta in formato testuale inserita dal commerciale"""
    TIPO_RICHIESTA_CHOICES = [
        ('MATERIALE', 'Materiale/Prodotti'),
        ('RINNOVO_GARANZIA', 'Rinnovo Garanzia'),
        ('SERVICE_CONTRACT', 'Service Contract'),
    ]

    STATO_CHOICES = [
        ('BOZZA', 'Bozza'),
        ('IN_LAVORAZIONE', 'In Lavorazione'),
        ('INVIATA', 'Inviata al Cliente'),
        ('APPROVATA', 'Approvata'),
        ('RIFIUTATA', 'Rifiutata'),
        ('CONVERTITA', 'Convertita in Ordine'),
    ]

    numero_richiesta = models.CharField(max_length=100, unique=True, verbose_name="Numero Richiesta", blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='richieste_offerta')
    tipo_richiesta = models.CharField(max_length=20, choices=TIPO_RICHIESTA_CHOICES, default='MATERIALE')
    richiesta_testuale = models.TextField(verbose_name="Richiesta del Cliente", help_text="Descrizione testuale della richiesta")
    stato = models.CharField(max_length=20, choices=STATO_CHOICES, default='BOZZA')

    # Per rinnovi garanzia/service contract
    scadenza_attuale = models.DateField(null=True, blank=True, verbose_name="Scadenza Attuale")

    # Riferimenti
    ordine_convertito = models.ForeignKey(
        'Ordine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='richiesta_origine',
        verbose_name="Ordine Convertito"
    )

    commerciale = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='richieste_offerta'
    )

    note = models.TextField(blank=True)
    data_richiesta = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Richiesta Offerta"
        verbose_name_plural = "Richieste Offerta"
        ordering = ['-data_richiesta']

    def __str__(self):
        return f"{self.numero_richiesta} - {self.cliente.nome}"

    def save(self, *args, **kwargs):
        """Auto-genera numero richiesta formato OFF-DATA-PROGRESSIVO"""
        if not self.numero_richiesta:
            from datetime import date
            oggi = date.today()
            data_str = oggi.strftime('%Y%m%d')

            # Trova ultimo numero progressivo del giorno
            ultimo = RichiestaOfferta.objects.filter(
                numero_richiesta__startswith=f'OFF-{data_str}-'
            ).order_by('-numero_richiesta').first()

            if ultimo:
                # Estrai progressivo dall'ultimo numero
                try:
                    ultimo_prog = int(ultimo.numero_richiesta.split('-')[-1])
                    progressivo = ultimo_prog + 1
                except:
                    progressivo = 1
            else:
                progressivo = 1

            self.numero_richiesta = f'OFF-{data_str}-{progressivo:03d}'

        super().save(*args, **kwargs)

    def can_convert(self):
        """Verifica se può essere convertita in ordine"""
        return self.stato == 'APPROVATA' and not self.ordine_convertito


class RigaOfferta(models.Model):
    """Riga di offerta con articolo, prezzo e note"""
    richiesta = models.ForeignKey(RichiestaOfferta, on_delete=models.CASCADE, related_name='righe')
    articolo = models.ForeignKey(Articolo, on_delete=models.PROTECT, null=True, blank=True)
    descrizione = models.CharField(max_length=500, verbose_name="Descrizione")
    quantita = models.IntegerField(default=1)
    prezzo_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prezzo Unitario €")

    # Per rinnovi garanzia/service contract
    mesi_durata = models.IntegerField(null=True, blank=True, verbose_name="Mesi Durata")

    note = models.TextField(blank=True)

    class Meta:
        verbose_name = "Riga Offerta"
        verbose_name_plural = "Righe Offerta"

    def __str__(self):
        return f"{self.descrizione} - €{self.prezzo_unitario}"

    @property
    def totale(self):
        return self.quantita * self.prezzo_unitario
