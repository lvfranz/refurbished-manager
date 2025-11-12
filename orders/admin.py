from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.utils.html import format_html
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone
from .models import (
    Articolo, Cliente, SedeCliente, Fornitore, SLA, ServiceContract,
    RinnovoServiceContract, Ordine, ArticoloOrdine, RMA,
    RichiestaOfferta, RigaOfferta
)
from django.forms.models import BaseInlineFormSet


@admin.register(Articolo)
class ArticoloAdmin(admin.ModelAdmin):
    list_display = ['codice_articolo', 'get_descrizione_short', 'categoria', 'costruttore', 'attivo']
    list_filter = ['attivo', 'categoria', 'costruttore']
    search_fields = ['codice_articolo', 'descrizione', 'categoria', 'costruttore']
    list_editable = ['attivo']
    ordering = ['categoria', 'codice_articolo']
    change_list_template = 'admin/orders/articolo/change_list.html'
    actions = ['imposta_brand_categoria', 'elimina_selezionati']

    def get_actions(self, request):
        """Rimuove l'azione delete predefinita di Django per usare solo la nostra personalizzata"""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_descrizione_short(self, obj):
        return obj.descrizione[:50] + '...' if len(obj.descrizione) > 50 else obj.descrizione
    get_descrizione_short.short_description = 'Descrizione'

    fieldsets = (
        ('Informazioni Principali', {
            'fields': ('codice_articolo', 'costruttore', 'categoria')
        }),
        ('Descrizione', {
            'fields': ('descrizione',)
        }),
        ('Stato', {
            'fields': ('attivo',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='articolo_import_csv'),
        ]
        return custom_urls + urls

    def import_csv_view(self, request):
        """Vista per importare articoli da CSV"""
        from orders.forms import ImportArticoliCSVForm
        from orders.models import Articolo

        if request.method == 'POST':
            form = ImportArticoliCSVForm(request.POST, request.FILES)
            if form.is_valid():
                articoli_to_create, errors = form.process_csv()
                sovrascrivi = form.cleaned_data.get('sovrascrivi', False)

                # Crea/Aggiorna gli articoli
                created_count = 0
                updated_count = 0
                skipped_count = 0
                error_details = []

                for articolo_data in articoli_to_create:
                    line_number = articolo_data.pop('line_number')

                    # Verifica se esiste già
                    existing = Articolo.objects.filter(codice_articolo=articolo_data['codice_articolo']).first()

                    if existing:
                        if sovrascrivi:
                            # Aggiorna l'articolo esistente
                            for key, value in articolo_data.items():
                                setattr(existing, key, value)
                            existing.save()
                            updated_count += 1
                        else:
                            # Salta
                            skipped_count += 1
                            error_details.append(f"Riga {line_number}: Articolo {articolo_data['codice_articolo']} già esistente")
                            continue
                    else:
                        # Crea nuovo articolo
                        Articolo.objects.create(**articolo_data)
                        created_count += 1

                # Messaggi di feedback
                if created_count > 0:
                    self.message_user(request, f'✅ {created_count} articoli creati con successo!', level='success')

                if updated_count > 0:
                    self.message_user(request, f'🔄 {updated_count} articoli aggiornati!', level='success')

                if skipped_count > 0:
                    self.message_user(request, f'⚠️ {skipped_count} articoli saltati (già esistenti)', level='warning')

                if errors:
                    for error in errors:
                        self.message_user(request, f'❌ {error}', level='error')

                if error_details:
                    for detail in error_details[:10]:  # Mostra max 10 errori
                        self.message_user(request, detail, level='warning')

                return redirect('admin:orders_articolo_changelist')
        else:
            form = ImportArticoliCSVForm()

        context = {
            **self.admin_site.each_context(request),
            'title': 'Importa Articoli da CSV',
            'form': form,
            'opts': self.model._meta,
        }

        return render(request, 'admin/orders/articolo/import_csv.html', context)

    def imposta_brand_categoria(self, request, queryset):
        """Azione per impostare brand e categoria agli articoli selezionati"""
        from django import forms

        class BrandCategoriaForm(forms.Form):
            costruttore = forms.CharField(
                required=False,
                max_length=100,
                label='Costruttore/Brand',
                help_text='Lascia vuoto per non modificare'
            )
            categoria = forms.CharField(
                required=False,
                max_length=100,
                label='Categoria',
                help_text='Lascia vuoto per non modificare'
            )

        if 'apply' in request.POST:
            form = BrandCategoriaForm(request.POST)
            if form.is_valid():
                costruttore = form.cleaned_data['costruttore']
                categoria = form.cleaned_data['categoria']

                updated_count = 0
                for articolo in queryset:
                    if costruttore:
                        articolo.costruttore = costruttore
                    if categoria:
                        articolo.categoria = categoria
                    if costruttore or categoria:
                        articolo.save()
                        updated_count += 1

                self.message_user(request, f'✅ {updated_count} articoli aggiornati con successo!')
                return redirect('admin:orders_articolo_changelist')
        else:
            form = BrandCategoriaForm()

        context = {
            **self.admin_site.each_context(request),
            'title': f'Imposta Brand e Categoria per {queryset.count()} articoli',
            'queryset': queryset,
            'form': form,
            'opts': self.model._meta,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        }

        return render(request, 'admin/orders/articolo/imposta_brand_categoria.html', context)

    imposta_brand_categoria.short_description = "🏷️ Imposta Brand/Categoria agli articoli selezionati"

    def elimina_selezionati(self, request, queryset):
        """Azione personalizzata per eliminare articoli con conferma"""
        if request.POST.get('post'):
            count = queryset.count()
            queryset.delete()
            self.message_user(request, f'🗑️ {count} articoli eliminati con successo!')
            return redirect('admin:orders_articolo_changelist')

        context = {
            **self.admin_site.each_context(request),
            'title': f'Conferma eliminazione di {queryset.count()} articoli',
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        }

        return render(request, 'admin/orders/articolo/conferma_eliminazione.html', context)

    elimina_selezionati.short_description = "🗑️ Elimina articoli selezionati"


class SedeClienteInline(admin.TabularInline):
    model = SedeCliente
    extra = 1


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'numero_sedi', 'created_at']
    search_fields = ['nome']
    inlines = [SedeClienteInline]

    def numero_sedi(self, obj):
        return obj.sedi.count()
    numero_sedi.short_description = 'Numero Sedi'


@admin.register(SedeCliente)
class SedeClienteAdmin(admin.ModelAdmin):
    list_display = ['nome_sede', 'cliente', 'citta', 'provincia']
    list_filter = ['cliente', 'provincia']
    search_fields = ['nome_sede', 'cliente__nome', 'indirizzo', 'citta']
    autocomplete_fields = ['cliente']


@admin.register(Fornitore)
class FornitoreAdmin(admin.ModelAdmin):
    list_display = ['nome', 'commerciale_riferimento', 'email', 'telefono']
    search_fields = ['nome', 'commerciale_riferimento']


@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ['nome', 'disponibilita_copertura', 'tempo_risposta', 'tipo_intervento']
    list_filter = ['disponibilita_copertura', 'tempo_risposta', 'tipo_intervento']
    search_fields = ['nome', 'descrizione']


class RinnovoServiceContractInline(admin.TabularInline):
    model = RinnovoServiceContract
    fk_name = 'contract_originale'
    extra = 0


class DissociateInlineFormSet(BaseInlineFormSet):
    """When DELETE is checked in the ServiceContract inline, just unlink the article from the contract instead of deleting the row."""

    def save_existing(self, form, instance, commit=True):
        """Override per dissociare invece di eliminare"""
        if form.cleaned_data.get('DELETE'):
            # Rimuovi il service contract invece di eliminare l'articolo
            instance.service_contract = None
            if commit:
                instance.save()
            # Ritorna l'istanza per prevenire l'eliminazione
            return instance
        return super().save_existing(form, instance, commit=commit)

    def save(self, commit=True):
        """Override save per gestire correttamente le eliminazioni e dissociazioni"""
        # Inizializza gli attributi che Django admin si aspetta
        self.new_objects = []
        self.changed_objects = []
        self.deleted_objects = []

        saved_instances = []

        # Gestisci i form esistenti
        for form in self.initial_forms:
            if not form.has_changed():
                continue

            if form.cleaned_data.get('DELETE'):
                # Dissociazione: rimuovi solo il service_contract
                obj = form.instance
                obj.service_contract = None
                if commit:
                    obj.save()
                # Aggiungi a changed_objects (non deleted) perché l'oggetto non viene eliminato
                self.changed_objects.append((obj, ['service_contract']))
                saved_instances.append(obj)
            else:
                # Salva normalmente
                obj = form.save(commit=commit)
                self.changed_objects.append((obj, form.changed_data))
                saved_instances.append(obj)

        # Gestisci i nuovi form (non dovrebbero essercene in questo inline read-only)
        for form in self.extra_forms:
            if form.has_changed():
                obj = form.save(commit=commit)
                self.new_objects.append(obj)
                saved_instances.append(obj)

        return saved_instances


class ArticoliServiceContractInline(admin.TabularInline):
    """Mostra articoli associati al service contract"""
    model = ArticoloOrdine
    fk_name = 'service_contract'
    extra = 0
    fields = ['mostra_articolo', 'numero_seriale', 'ordine', 'sede_cliente', 'data_scadenza_garanzia']
    readonly_fields = ['mostra_articolo', 'numero_seriale', 'ordine', 'sede_cliente', 'data_scadenza_garanzia']
    can_delete = True
    formset = DissociateInlineFormSet
    verbose_name = "Articolo nel Contratto"
    verbose_name_plural = "Articoli nel Contratto"

    def mostra_articolo(self, obj):
        """Mostra solo codice e descrizione dell'articolo senza duplicati"""
        if obj and obj.articolo:
            return format_html(
                '<strong style="color: #fff;">{}</strong><br>'
                '<span style="color: #aaa; font-size: 12px;">{}</span>',
                obj.articolo.codice_articolo,
                obj.articolo.descrizione[:80] + '...' if len(obj.articolo.descrizione) > 80 else obj.articolo.descrizione
            )
        return '-'
    mostra_articolo.short_description = 'Articolo'

    def has_add_permission(self, request, obj=None):
        # Non permettere aggiunta diretta, si usa l'azione "Aggiungi a Service Contract"
        return False



@admin.register(ServiceContract)
class ServiceContractAdmin(admin.ModelAdmin):
    list_display = ['numero_contratto', 'cliente', 'sla', 'data_inizio', 'data_fine', 'stato_attivo', 'is_valid', 'numero_articoli']
    list_filter = ['attivo', 'sla', 'cliente']
    search_fields = ['numero_contratto', 'cliente__nome']
    date_hierarchy = 'data_inizio'
    inlines = [ArticoliServiceContractInline, RinnovoServiceContractInline]

    class Media:
        css = {
            'all': ('admin/css/servicecontract_dark_theme.css',)
        }

    def numero_articoli(self, obj):
        return obj.articoli.count()
    numero_articoli.short_description = 'N. Articoli'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:sc_id>/aggiungi-articoli/',
                self.admin_site.admin_view(self.aggiungi_articoli_view),
                name='servicecontract_aggiungi_articoli'
            ),
        ]
        return custom_urls + urls

    def aggiungi_articoli_view(self, request, sc_id):
        """Vista per aggiungere articoli disponibili al service contract"""
        from django import forms

        sc = ServiceContract.objects.get(pk=sc_id)

        # Trova articoli disponibili del cliente senza service contract
        articoli_disponibili = ArticoloOrdine.objects.filter(
            sede_cliente__cliente=sc.cliente,
            service_contract__isnull=True
        ).select_related('articolo', 'ordine', 'sede_cliente')

        class AggiungiArticoliForm(forms.Form):
            articoli = forms.ModelMultipleChoiceField(
                queryset=articoli_disponibili,
                widget=forms.CheckboxSelectMultiple,
                label='Seleziona articoli da aggiungere',
                required=False
            )

        if request.method == 'POST':
            form = AggiungiArticoliForm(request.POST)
            if form.is_valid():
                articoli_selezionati = form.cleaned_data['articoli']
                count = articoli_selezionati.update(service_contract=sc)
                self.message_user(request, f'{count} articoli aggiunti al service contract {sc.numero_contratto}')
                return redirect('admin:orders_servicecontract_change', sc_id)
        else:
            form = AggiungiArticoliForm()

        context = {
            **self.admin_site.each_context(request),
            'title': f'Aggiungi Articoli a {sc.numero_contratto}',
            'form': form,
            'sc': sc,
            'articoli_disponibili': articoli_disponibili,
            'opts': self.model._meta,
        }

        return render(request, 'admin/aggiungi_articoli_servicecontract.html', context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        # Aggiungi informazioni per aggiungere articoli
        sc = ServiceContract.objects.get(pk=object_id)
        articoli_disponibili = ArticoloOrdine.objects.filter(
            sede_cliente__cliente=sc.cliente,
            service_contract__isnull=True
        ).select_related('articolo', 'ordine', 'sede_cliente')

        extra_context['articoli_disponibili'] = articoli_disponibili
        extra_context['has_articoli_disponibili'] = articoli_disponibili.exists()
        extra_context['cliente_nome'] = sc.cliente.nome
        extra_context['sc_id'] = object_id

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def stato_attivo(self, obj):
        if obj.attivo:
            return format_html('<span style="color: green;">✓ Attivo</span>')
        return format_html('<span style="color: red;">✗ Non Attivo</span>')
    stato_attivo.short_description = 'Stato'

    def is_valid(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Valido</span>')
        return format_html('<span style="color: orange;">⚠ Non Valido</span>')
    is_valid.short_description = 'Validità'


@admin.register(RinnovoServiceContract)
class RinnovoServiceContractAdmin(admin.ModelAdmin):
    list_display = ['contract_originale', 'contract_nuovo', 'data_rinnovo']
    search_fields = ['contract_originale__numero_contratto', 'contract_nuovo__numero_contratto']



class ArticoloOrdineInline(admin.StackedInline):  # Uso StackedInline per fieldsets
    model = ArticoloOrdine
    extra = 1
    autocomplete_fields = ['articolo', 'sede_cliente']
    readonly_fields = ['mostra_service_contract']  # Service contract read-only, gestito solo da azioni dedicate

    class Media:
        css = {
            'all': ('admin/css/service_contract_readonly.css',)
        }

    def mostra_service_contract(self, obj):
        """Mostra service contract con messaggio informativo"""
        if obj.service_contract:
            return format_html(
                '<div style="padding: 10px; background-color: #e8f5e9; border: 2px solid #4caf50; border-radius: 6px;">'
                '<strong style="color: #2e7d32;">🔒 {}</strong><br>'
                '<small style="color: #666;">Per rimuovere: Admin → Articoli Ordine → seleziona → "Rimuovi da Service Contract"</small>'
                '</div>',
                obj.service_contract.numero_contratto
            )
        return format_html(
            '<div style="padding: 8px; background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 4px; color: #666;">'
            'Nessun Service Contract<br>'
            '<small>Aggiungibile dal Service Contract stesso</small>'
            '</div>'
        )
    mostra_service_contract.short_description = 'Service Contract'

    # Organizzo i campi in sezioni
    fieldsets = (
        (None, {
            'fields': (
                'articolo',
                ('numero_seriale', 'quantita'),
                'mostra_service_contract',
                'note',
            )
        }),
        ('Dettagli (precompilati automaticamente)', {
            'fields': ('sede_cliente', 'mesi_garanzia'),
            'classes': ('collapse',),
            'description': 'Questi campi sono precompilati dai default dell\'ordine. Modificali solo se necessario.'
        }),
    )

    classes = ['collapse']  # Ogni articolo è collapsabile

    def get_formset(self, request, obj=None, **kwargs):
        """Configura iniziali e queryset dei campi in base ai default dell'ordine o alla scelta in form."""
        formset_class = super().get_formset(request, obj, **kwargs)

        # Rileva sede_default e mesi default da ordine esistente
        sede_default = None
        mesi_default = None
        cliente = None

        if obj:  # change view con ordine esistente
            sede_default = getattr(obj, 'sede_default', None)
            mesi_default = getattr(obj, 'mesi_garanzia_default', None)
            if sede_default:
                cliente = sede_default.cliente

        # Salva i default in variabili accessibili alla classe
        _sede_default = sede_default
        _mesi_default = mesi_default

        # Crea una classe formset personalizzata che applica i default
        class CustomFormSet(formset_class):
            def _construct_form(self, i, **kwargs):
                """Override per applicare i default a OGNI form quando viene costruito"""
                # Imposta i default in kwargs['initial'] prima di costruire il form
                if 'initial' not in kwargs:
                    kwargs['initial'] = {}

                # Applica i default solo se il form è nuovo (non ha instance o instance.pk è None)
                defaults_to_apply = {}
                if _sede_default:
                    defaults_to_apply['sede_cliente'] = _sede_default
                if _mesi_default:
                    defaults_to_apply['mesi_garanzia'] = _mesi_default

                # Merge con initial esistente
                kwargs['initial'].update(defaults_to_apply)

                form = super()._construct_form(i, **kwargs)

                # Applica anche direttamente ai campi del form per sicurezza
                if not form.instance.pk:
                    if _sede_default and 'sede_cliente' in form.fields:
                        form.fields['sede_cliente'].initial = _sede_default
                    if _mesi_default and 'mesi_garanzia' in form.fields:
                        form.fields['mesi_garanzia'].initial = _mesi_default

                return form

            def get_form_kwargs(self, index):
                """Fornisce kwargs per ogni form inclusi i default"""
                kwargs = super().get_form_kwargs(index)
                if 'initial' not in kwargs:
                    kwargs['initial'] = {}
                if _sede_default:
                    kwargs['initial']['sede_cliente'] = _sede_default
                if _mesi_default:
                    kwargs['initial']['mesi_garanzia'] = _mesi_default
                return kwargs

        # Filtra i service contract: solo quelli del cliente rilevato e attivi
        from .models import ServiceContract
        # Verifica se il campo service_contract esiste nel form (potrebbe essere read-only)
        if 'service_contract' in CustomFormSet.form.base_fields:
            if cliente is not None:
                CustomFormSet.form.base_fields['service_contract'].queryset = ServiceContract.objects.filter(
                    cliente=cliente,
                    attivo=True
                )
            else:
                CustomFormSet.form.base_fields['service_contract'].queryset = ServiceContract.objects.none()
                CustomFormSet.form.base_fields['service_contract'].help_text = (
                    "Imposta prima la 'Sede Default' dell'ordine e salva per poter selezionare il Service Contract del cliente.")

        return CustomFormSet

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "service_contract":
            # Ottieni l'ordine se stiamo modificando
            if request.resolver_match and 'object_id' in request.resolver_match.kwargs:
                ordine_id = request.resolver_match.kwargs['object_id']
                try:
                    ordine = Ordine.objects.get(pk=ordine_id)
                    if ordine.sede_default:
                        kwargs["queryset"] = ServiceContract.objects.filter(
                            cliente=ordine.sede_default.cliente,
                            attivo=True
                        )
                except Ordine.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Ordine)
class OrdineAdmin(admin.ModelAdmin):
    form = None  # Sarà impostato in get_form
    list_display = ['numero_ordine', 'fornitore', 'data_ordine', 'tipo_ordine_badge', 'mesi_garanzia_default', 'created_at']
    list_filter = ['tipo_ordine', 'fornitore', 'data_ordine']
    search_fields = ['numero_ordine', 'fornitore__nome', 'note']
    date_hierarchy = 'data_ordine'

    def get_form(self, request, obj=None, **kwargs):
        """Usa il form personalizzato con validazione condizionale"""
        from orders.forms import OrdineForm
        kwargs['form'] = OrdineForm
        return super().get_form(request, obj, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/gestisci-articoli/',
                 self.admin_site.admin_view(self.gestisci_articoli_view),
                 name='ordine_gestisci_articoli'),
        ]
        return custom_urls + urls

    def get_inlines(self, request, obj=None):
        """Mostra gli articoli inline SOLO se l'ordine è STANDARD e già salvato"""
        if obj and obj.tipo_ordine == 'STANDARD':
            return [ArticoloOrdineInline]
        return []

    def get_fieldsets(self, request, obj=None):
        """Fieldsets diversi per creazione e modifica, e in base al tipo ordine"""
        if not obj:  # Creazione nuovo ordine - solo info base
            return (
                ('Informazioni Ordine', {
                    'fields': ('numero_ordine', 'richiesta_offerta', 'fornitore', 'data_ordine', 'tipo_ordine'),
                    'description': '<strong>⚠️ STEP 1:</strong> Inserisci le informazioni base dell\'ordine. '
                                 'Dopo aver salvato, potrai gestire gli articoli o collegare l\'ordine di riferimento.'
                }),
                ('Sede e Garanzia Default (solo per ordini Standard)', {
                    'fields': (('sede_default', 'mesi_garanzia_default'),),
                    'description': '<strong>Solo per ordini Standard:</strong> Questi valori saranno applicati automaticamente agli articoli.<br>'
                                 '<em>Per RMA e Rinnovo Garanzia, questi campi saranno ereditati dall\'ordine di riferimento.</em>',
                    'classes': ('collapse',)
                }),
                ('Note', {
                    'fields': ('note',)
                }),
            )
        else:  # Modifica ordine esistente
            if obj.tipo_ordine == 'STANDARD':
                return (
                    ('Informazioni Ordine', {
                        'fields': ('numero_ordine', 'richiesta_offerta', 'fornitore', 'data_ordine', 'tipo_ordine')
                    }),
                    ('Default per Articoli', {
                        'fields': (('sede_default', 'mesi_garanzia_default'),),
                        'description': '<strong>⚠️ IMPORTANTE:</strong> Questi valori vengono applicati automaticamente a tutti i nuovi articoli.'
                    }),
                    ('Note', {
                        'fields': ('note',)
                    }),
                )
            else:  # RMA o Rinnovo Garanzia
                return (
                    ('Informazioni Ordine', {
                        'fields': ('numero_ordine', 'richiesta_offerta', 'fornitore', 'data_ordine', 'tipo_ordine')
                    }),
                    ('Ordine Collegato', {
                        'fields': ('ordine_originale_rma' if obj.tipo_ordine == 'RMA' else 'ordine_materiale_collegato',),
                        'description': 'Seleziona l\'ordine di riferimento per questo {}'.format(
                            'RMA' if obj.tipo_ordine == 'RMA' else 'Rinnovo Garanzia'
                        )
                    }),
                    ('Documento PDF', {
                        'fields': ('pdf_ordine',),
                        'description': 'Carica il documento PDF dell\'ordine'
                    }),
                    ('Note', {
                        'fields': ('note',)
                    }),
                )

    def get_readonly_fields(self, request, obj=None):
        """Dopo la creazione, tipo_ordine diventa read-only"""
        if obj:
            return ['tipo_ordine']
        return []

    autocomplete_fields = ['sede_default', 'richiesta_offerta', 'ordine_originale_rma', 'ordine_materiale_collegato']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra ordini collegati per cliente quando possibile"""
        if db_field.name in ['ordine_originale_rma', 'ordine_materiale_collegato']:
            # Ottieni l'ordine se stiamo modificando
            if request.resolver_match and 'object_id' in request.resolver_match.kwargs:
                ordine_id = request.resolver_match.kwargs['object_id']
                try:
                    ordine = Ordine.objects.get(pk=ordine_id)
                    if ordine.sede_default:
                        # Filtra ordini dello stesso cliente
                        kwargs["queryset"] = Ordine.objects.filter(
                            tipo_ordine='STANDARD',
                            sede_default__cliente=ordine.sede_default.cliente
                        ).exclude(pk=ordine.pk)
                    else:
                        # Se non c'è sede default, mostra tutti gli ordini standard
                        kwargs["queryset"] = Ordine.objects.filter(tipo_ordine='STANDARD').exclude(pk=ordine.pk)
                except Ordine.DoesNotExist:
                    pass
            else:
                # Durante la creazione, mostra solo ordini standard
                kwargs["queryset"] = Ordine.objects.filter(tipo_ordine='STANDARD')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def gestisci_articoli_view(self, request, object_id):
        """View personalizzata per gestire articoli in base al tipo ordine"""
        ordine = self.get_object(request, object_id)
        if ordine is None:
            return redirect('admin:orders_ordine_changelist')

        if ordine.tipo_ordine == 'STANDARD':
            # Redirect alla normale change view con inline articoli
            return redirect('admin:orders_ordine_change', object_id)
        else:
            # Mostra interfaccia per selezionare ordine esistente + upload PDF
            from django.shortcuts import render

            if request.method == 'POST':
                # Gestisci selezione ordine e upload PDF
                ordine_collegato_id = request.POST.get('ordine_collegato')
                pdf_file = request.FILES.get('pdf_ordine')

                if ordine_collegato_id:
                    try:
                        ordine_collegato = Ordine.objects.get(pk=ordine_collegato_id)
                        if ordine.tipo_ordine == 'RMA':
                            ordine.ordine_originale_rma = ordine_collegato
                        else:  # RINNOVO_GARANZIA
                            ordine.ordine_materiale_collegato = ordine_collegato
                    except Ordine.DoesNotExist:
                        pass

                if pdf_file:
                    ordine.pdf_ordine = pdf_file

                ordine.save()
                self.message_user(request, '✅ Ordine aggiornato con successo!')
                return redirect('admin:orders_ordine_change', object_id)

            # GET: mostra form per selezione
            # Filtra ordini per cliente se possibile
            ordini_disponibili = Ordine.objects.filter(tipo_ordine='STANDARD').exclude(pk=ordine.pk)

            context = {
                'ordine': ordine,
                'ordini_disponibili': ordini_disponibili,
                'opts': self.model._meta,
                'has_view_permission': self.has_view_permission(request, ordine),
                'has_change_permission': self.has_change_permission(request, ordine),
            }

            return render(request, 'admin/orders/ordine_gestisci_articoli.html', context)


    def response_add(self, request, obj, post_url_continue=None):
        """Dopo la creazione, redirect alla gestione articoli"""
        if obj.tipo_ordine == 'STANDARD':
            # Per ordini standard, vai alla change view con inline articoli
            self.message_user(
                request,
                format_html(
                    '✅ Ordine creato con successo! <strong>Ora aggiungi gli articoli</strong> usando "Aggiungi un altro Articolo Ordine" qui sotto.'
                ),
                level='success'
            )
            return redirect('admin:orders_ordine_change', obj.pk)
        else:
            # Per RMA/Rinnovo, vai alla view di gestione articoli
            self.message_user(
                request,
                format_html(
                    '✅ Ordine creato! <strong>Ora seleziona l\'ordine di riferimento e carica il PDF.</strong>'
                ),
                level='success'
            )
            return redirect('admin:orders_ordine_change', obj.pk)

    def save_model(self, request, obj, form, change):
        """Applica i default a tutti gli articoli quando cambiano"""
        is_new = not change

        # Salva prima l'ordine
        super().save_model(request, obj, form, change)

        # Se è una modifica (non nuovo ordine), aggiorna gli articoli esistenti
        if change:
            # Aggiorna sede_default su tutti gli articoli se impostata
            if obj.sede_default:
                obj.articoli.filter(sede_cliente__isnull=True).update(sede_cliente=obj.sede_default)
                # Messaggio all'utente
                count_sede = obj.articoli.filter(sede_cliente=obj.sede_default).count()
                if count_sede > 0:
                    self.message_user(request, f'Sede default applicata a {count_sede} articoli')

            # Aggiorna mesi_garanzia_default su tutti gli articoli
            if obj.mesi_garanzia_default:
                articoli_aggiornati = obj.articoli.filter(service_contract__isnull=True)
                for articolo in articoli_aggiornati:
                    articolo.mesi_garanzia = obj.mesi_garanzia_default
                    # Ricalcola scadenza garanzia
                    if obj.data_ordine:
                        from dateutil.relativedelta import relativedelta
                        articolo.data_scadenza_garanzia = obj.data_ordine + relativedelta(months=obj.mesi_garanzia_default)
                    articolo.save()

                count_garanzia = articoli_aggiornati.count()
                if count_garanzia > 0:
                    self.message_user(request, f'Garanzia default ({obj.mesi_garanzia_default} mesi) applicata a {count_garanzia} articoli')

    def tipo_ordine_badge(self, obj):
        colors = {
            'STANDARD': '#2196F3',
            'RMA': '#ff9800',
            'RINNOVO_GARANZIA': '#4caf50',
        }
        color = colors.get(obj.tipo_ordine, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_tipo_ordine_display()
        )
    tipo_ordine_badge.short_description = 'Tipo'

    def numero_articoli(self, obj):
        return obj.articoli.count()
    numero_articoli.short_description = 'N. Articoli'

    def save_formset(self, request, form, formset, change):
        """Applica sede_default e mesi_garanzia_default ai nuovi articoli prima del salvataggio."""
        instances = formset.save(commit=False)
        ordine = form.instance
        for instance in instances:
            if isinstance(instance, ArticoloOrdine):
                # sede default
                if not instance.sede_cliente and getattr(ordine, 'sede_default', None):
                    instance.sede_cliente = ordine.sede_default
                # mesi garanzia default (solo se non impostato o impostato al default 12)
                if (not instance.mesi_garanzia or instance.mesi_garanzia == 12) and getattr(ordine, 'mesi_garanzia_default', None):
                    instance.mesi_garanzia = ordine.mesi_garanzia_default
                # calcolo scadenza se non sotto SC
                if not instance.service_contract and not instance.data_scadenza_garanzia and ordine.data_ordine and instance.mesi_garanzia:
                    from dateutil.relativedelta import relativedelta
                    instance.data_scadenza_garanzia = ordine.data_ordine + relativedelta(months=instance.mesi_garanzia)
            instance.save()
        formset.save_m2m()

    def gestisci_articoli_view(self, request, object_id):
        """View personalizzata per gestire articoli in base al tipo ordine"""
        ordine = self.get_object(request, object_id)
        if ordine is None:
            return redirect('admin:orders_ordine_changelist')

        if ordine.tipo_ordine == 'STANDARD':
            # Redirect alla normale change view con inline articoli
            return redirect('admin:orders_ordine_change', object_id)
        else:
            # Mostra interfaccia per selezionare ordine esistente + upload PDF
            from django.shortcuts import render

            if request.method == 'POST':
                # Gestisci selezione ordine e upload PDF
                ordine_collegato_id = request.POST.get('ordine_collegato')
                pdf_file = request.FILES.get('pdf_ordine')

                if ordine_collegato_id:
                    try:
                        ordine_collegato = Ordine.objects.get(pk=ordine_collegato_id)
                        if ordine.tipo_ordine == 'RMA':
                            ordine.ordine_originale_rma = ordine_collegato
                        else:  # RINNOVO_GARANZIA
                            ordine.ordine_materiale_collegato = ordine_collegato

                        # Copia anche sede_default e mesi_garanzia_default dall'ordine collegato
                        if not ordine.sede_default:
                            ordine.sede_default = ordine_collegato.sede_default
                        if ordine.mesi_garanzia_default == 12:  # Valore di default
                            ordine.mesi_garanzia_default = ordine_collegato.mesi_garanzia_default

                    except Ordine.DoesNotExist:
                        self.message_user(request, '❌ Ordine selezionato non trovato', level='error')

                if pdf_file:
                    ordine.pdf_ordine = pdf_file

                ordine.save()
                self.message_user(request, '✅ Ordine aggiornato con successo!')
                return redirect('admin:orders_ordine_change', object_id)

            # GET: mostra form per selezione
            # Filtra ordini per cliente se possibile
            ordini_disponibili = Ordine.objects.filter(
                tipo_ordine='STANDARD'
            ).exclude(pk=ordine.pk).select_related('fornitore', 'sede_default__cliente')

            # Se ordine ha già una sede_default, filtra per quello stesso cliente
            if ordine.sede_default:
                ordini_disponibili = ordini_disponibili.filter(
                    sede_default__cliente=ordine.sede_default.cliente
                )

            # Ordina per data decrescente
            ordini_disponibili = ordini_disponibili.order_by('-data_ordine')

            context = {
                'ordine': ordine,
                'ordini_disponibili': ordini_disponibili,
                'opts': self.model._meta,
                'has_view_permission': self.has_view_permission(request, ordine),
                'has_change_permission': self.has_change_permission(request, ordine),
                'title': f'Gestisci {ordine.get_tipo_ordine_display()}: {ordine.numero_ordine}',
            }

            return render(request, 'admin/orders/ordine_gestisci_articoli.html', context)


    def response_add(self, request, obj, post_url_continue=None):
        """Dopo la creazione, redirect alla gestione articoli"""
        if obj.tipo_ordine == 'STANDARD':
            # Per ordini standard, vai alla change view con inline articoli
            self.message_user(
                request,
                format_html(
                    '✅ Ordine creato con successo! <strong>Ora aggiungi gli articoli</strong> usando "Aggiungi un altro Articolo Ordine" qui sotto.'
                ),
                level='success'
            )
            return redirect('admin:orders_ordine_change', obj.pk)
        else:
            # Per RMA/Rinnovo, vai alla view di gestione articoli
            self.message_user(
                request,
                format_html(
                    '✅ Ordine creato! <strong>Ora seleziona l\'ordine di riferimento e carica il PDF.</strong>'
                ),
                level='success'
            )
            return redirect('admin:orders_ordine_change', obj.pk)

    def save_model(self, request, obj, form, change):
        """Applica i default a tutti gli articoli quando cambiano"""
        is_new = not change

        # Salva prima l'ordine
        super().save_model(request, obj, form, change)


        # Se è una modifica (non nuovo ordine), aggiorna gli articoli esistenti
        if change:
            # Aggiorna sede_default su tutti gli articoli se impostata
            if obj.sede_default:
                obj.articoli.filter(sede_cliente__isnull=True).update(sede_cliente=obj.sede_default)
                # Messaggio all'utente
                count_sede = obj.articoli.filter(sede_cliente=obj.sede_default).count()
                if count_sede > 0:
                    self.message_user(request, f'Sede default applicata a {count_sede} articoli')

            # Aggiorna mesi_garanzia_default su tutti gli articoli
            if obj.mesi_garanzia_default:
                articoli_aggiornati = obj.articoli.filter(service_contract__isnull=True)
                for articolo in articoli_aggiornati:
                    articolo.mesi_garanzia = obj.mesi_garanzia_default
                    # Ricalcola scadenza garanzia
                    if obj.data_ordine:
                        from dateutil.relativedelta import relativedelta
                        articolo.data_scadenza_garanzia = obj.data_ordine + relativedelta(months=obj.mesi_garanzia_default)
                    articolo.save()

                count_garanzia = articoli_aggiornati.count()
                if count_garanzia > 0:
                    self.message_user(request, f'Garanzia default ({obj.mesi_garanzia_default} mesi) applicata a {count_garanzia} articoli')

    def tipo_ordine_badge(self, obj):
        colors = {
            'STANDARD': '#2196F3',
            'RMA': '#ff9800',
            'RINNOVO_GARANZIA': '#4caf50',
        }
        color = colors.get(obj.tipo_ordine, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_tipo_ordine_display()
        )
    tipo_ordine_badge.short_description = 'Tipo'

    def numero_articoli(self, obj):
        return obj.articoli.count()
    numero_articoli.short_description = 'N. Articoli'

    def save_formset(self, request, form, formset, change):
        """Applica sede_default e mesi_garanzia_default ai nuovi articoli prima del salvataggio."""
        instances = formset.save(commit=False)
        ordine = form.instance
        for instance in instances:
            if isinstance(instance, ArticoloOrdine):
                # sede default
                if not instance.sede_cliente and getattr(ordine, 'sede_default', None):
                    instance.sede_cliente = ordine.sede_default
                # mesi garanzia default (solo se non impostato o impostato al default 12)
                if (not instance.mesi_garanzia or instance.mesi_garanzia == 12) and getattr(ordine, 'mesi_garanzia_default', None):
                    instance.mesi_garanzia = ordine.mesi_garanzia_default
                # calcolo scadenza se non sotto SC
                if not instance.service_contract and not instance.data_scadenza_garanzia and ordine.data_ordine and instance.mesi_garanzia:
                    from dateutil.relativedelta import relativedelta
                    instance.data_scadenza_garanzia = ordine.data_ordine + relativedelta(months=instance.mesi_garanzia)
            instance.save()
        formset.save_m2m()


@admin.register(ArticoloOrdine)
class ArticoloOrdineAdmin(admin.ModelAdmin):
    list_display = ['get_articolo_code', 'numero_seriale', 'ordine', 'sede_cliente', 'quantita',
                    'data_scadenza_garanzia', 'stato_garanzia', 'get_service_contract']
    list_filter = ['articolo__categoria', 'articolo__costruttore', 'ordine__fornitore',
                   'sede_cliente__cliente', 'service_contract']
    search_fields = ['articolo__codice_articolo', 'numero_seriale',
                     'ordine__numero_ordine', 'sede_cliente__cliente__nome', 'sede_cliente__nome_sede',
                     'note']
    date_hierarchy = 'data_scadenza_garanzia'
    autocomplete_fields = ['articolo', 'sede_cliente']
    readonly_fields = ['data_scadenza_garanzia', 'mostra_service_contract_info']
    actions = ['aggiungi_a_service_contract', 'rimuovi_da_service_contract']

    def get_service_contract(self, obj):
        """Per visualizzazione in list_display"""
        if obj.service_contract:
            return obj.service_contract.numero_contratto
        return '-'
    get_service_contract.short_description = 'Service Contract'

    def mostra_service_contract_info(self, obj):
        """Visualizza service contract con messaggio informativo (read-only completo)"""
        if obj.service_contract:
            return format_html(
                '<div style="padding: 12px; background-color: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; margin: 10px 0;">'
                '<div style="margin-bottom: 8px;">'
                '<strong style="font-size: 16px; color: #2e7d32;">🔒 Service Contract: {}</strong>'
                '</div>'
                '<div style="padding: 8px; background-color: #fff3cd; border-left: 4px solid #ff9800; border-radius: 4px; margin-top: 8px;">'
                '<strong style="color: #e65100;">⚠️ Come rimuovere:</strong><br>'
                '<span style="color: #333;">Admin → <strong>Articoli Ordine</strong> → seleziona articolo → Azioni → <strong>"🔓 Rimuovi da Service Contract"</strong></span>'
                '</div>'
                '</div>',
                obj.service_contract.numero_contratto
            )
        return format_html(
            '<div style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 6px; color: #666;">'
            '<strong>Nessun Service Contract</strong><br>'
            '<small>Aggiungibile tramite: Admin → Service Contracts → seleziona SC → "Aggiungi Articoli"</small>'
            '</div>'
        )
    mostra_service_contract_info.short_description = 'Service Contract'

    def aggiungi_a_service_contract(self, request, queryset):
        """Azione per aggiungere articoli selezionati a un service contract"""
        # Verifica che tutti gli articoli siano dello stesso cliente
        clienti = set()
        for articolo in queryset:
            if articolo.sede_cliente:
                clienti.add(articolo.sede_cliente.cliente)

        if len(clienti) == 0:
            self.message_user(request, "Nessun articolo ha una sede cliente assegnata", level='error')
            return

        if len(clienti) > 1:
            self.message_user(request, "Gli articoli selezionati appartengono a clienti diversi. Seleziona articoli dello stesso cliente.", level='error')
            return

        cliente = list(clienti)[0]

        # Mostra form per selezionare il service contract
        from django import forms

        class ServiceContractForm(forms.Form):
            service_contract = forms.ModelChoiceField(
                queryset=ServiceContract.objects.filter(cliente=cliente, attivo=True),
                label='Service Contract',
                help_text=f'Seleziona il service contract per {cliente.nome}'
            )

        if 'apply' in request.POST:
            form = ServiceContractForm(request.POST)
            if form.is_valid():
                sc = form.cleaned_data['service_contract']
                count = queryset.update(service_contract=sc)
                self.message_user(request, f'{count} articoli aggiunti al service contract {sc.numero_contratto}')
                return
        else:
            form = ServiceContractForm()

        context = {
            **self.admin_site.each_context(request),
            'title': f'Aggiungi articoli a Service Contract',
            'queryset': queryset,
            'form': form,
            'cliente': cliente,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }

        return render(request, 'admin/aggiungi_service_contract.html', context)

    aggiungi_a_service_contract.short_description = "Aggiungi articoli selezionati a Service Contract"

    fieldsets = (
        ('Informazioni Ordine', {
            'fields': ('ordine', 'articolo')
        }),
        ('Dettagli Articolo', {
            'fields': ('numero_seriale', 'quantita', 'note')
        }),
        ('Assegnazione', {
            'fields': ('sede_cliente',)
        }),
        ('Garanzia/Service Contract', {
            'fields': ('mesi_garanzia', 'data_scadenza_garanzia', 'mostra_service_contract_info'),
            'description': 'Il Service Contract può essere gestito solo tramite le azioni dedicate nell\'admin.'
        }),
    )

    def get_articolo_code(self, obj):
        return obj.articolo.codice_articolo
    get_articolo_code.short_description = 'Codice Articolo'
    get_articolo_code.admin_order_field = 'articolo__codice_articolo'

    def stato_garanzia(self, obj):
        if obj.is_in_garanzia():
            return format_html('<span style="color: green;">✓ In Garanzia</span>')
        return format_html('<span style="color: red;">✗ Fuori Garanzia</span>')
    stato_garanzia.short_description = 'Stato Garanzia'

    def rimuovi_da_service_contract(self, request, queryset):
        """Rimuove gli articoli selezionati dal loro service contract (dissociazione)"""
        # Filtra solo articoli che hanno un service contract
        articoli_con_sc = queryset.filter(service_contract__isnull=False)

        if not articoli_con_sc.exists():
            self.message_user(
                request,
                '⚠️ Nessun articolo selezionato ha un service contract da rimuovere',
                level='warning'
            )
            return

        count = articoli_con_sc.count()
        sc_nomi = set(articoli_con_sc.values_list('service_contract__numero_contratto', flat=True))

        # Rimuovi service contract da tutti gli articoli (dissociazione, non eliminazione)
        articoli_con_sc.update(service_contract=None)

        self.message_user(
            request,
            format_html(
                '✅ {} articoli rimossi da service contract: <strong>{}</strong>',
                count,
                ', '.join(sc_nomi)
            ),
            level='success'
        )

    rimuovi_da_service_contract.short_description = "🔓 Rimuovi da Service Contract (solo dissociazione)"


@admin.register(RMA)
class RMAAdmin(admin.ModelAdmin):
    list_display = ['numero_rma', 'articolo_originale', 'data_apertura', 'stato',
                    'override_garanzia', 'ordine_fornitore']
    list_filter = ['stato', 'override_garanzia', 'data_apertura']
    search_fields = ['numero_rma', 'articolo_originale__articolo',
                     'articolo_originale__numero_seriale', 'motivo']
    date_hierarchy = 'data_apertura'

    fieldsets = (
        ('Informazioni RMA', {
            'fields': ('numero_rma', 'articolo_originale', 'motivo', 'stato')
        }),
        ('Gestione Garanzia', {
            'fields': ('override_garanzia',)
        }),
        ('Ordine Fornitore', {
            'fields': ('ordine_fornitore',)
        }),
        ('Note', {
            'fields': ('note',),
            'classes': ('collapse',)
        }),
    )


# Admin per Offerte

class RigaOffertaInline(admin.TabularInline):
    model = RigaOfferta
    extra = 1
    fields = ['articolo', 'descrizione', 'quantita', 'prezzo_unitario', 'mesi_durata', 'note']
    autocomplete_fields = ['articolo']


@admin.register(RichiestaOfferta)
class RichiestaOffertaAdmin(admin.ModelAdmin):
    list_display = ['numero_richiesta', 'cliente', 'tipo_richiesta', 'stato_badge', 'data_richiesta', 'commerciale', 'ordine_link']
    list_filter = ['stato', 'tipo_richiesta', 'data_richiesta', 'commerciale']
    search_fields = ['numero_richiesta', 'cliente__nome', 'richiesta_testuale']
    date_hierarchy = 'data_richiesta'
    inlines = [RigaOffertaInline]
    autocomplete_fields = ['cliente']
    readonly_fields = ['numero_richiesta']

    fieldsets = (
        ('Informazioni Richiesta', {
            'fields': ('numero_richiesta', 'cliente', 'tipo_richiesta', 'stato', 'commerciale'),
            'description': 'Il numero offerta viene generato automaticamente nel formato OFF-YYYYMMDD-NNN'
        }),
        ('Richiesta Cliente', {
            'fields': ('richiesta_testuale',)
        }),
        ('Dettagli Rinnovo', {
            'fields': ('scadenza_attuale',),
            'classes': ('collapse',)
        }),
        ('Conversione', {
            'fields': ('ordine_convertito',),
            'classes': ('collapse',)
        }),
        ('Note', {
            'fields': ('note',),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Nuovo oggetto
            if not obj.commerciale:
                obj.commerciale = request.user
        super().save_model(request, obj, form, change)

    def stato_badge(self, obj):
        colors = {
            'BOZZA': '#6c757d',
            'IN_LAVORAZIONE': '#ffc107',
            'INVIATA': '#17a2b8',
            'APPROVATA': '#28a745',
            'RIFIUTATA': '#dc3545',
            'CONVERTITA': '#6f42c1',
        }
        color = colors.get(obj.stato, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_stato_display()
        )
    stato_badge.short_description = 'Stato'

    def ordine_link(self, obj):
        if obj.ordine_convertito:
            url = reverse('admin:orders_ordine_change', args=[obj.ordine_convertito.pk])
            return format_html('<a href="{}">{}</a>', url, obj.ordine_convertito.numero_ordine)
        return '-'
    ordine_link.short_description = 'Ordine'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:richiesta_id>/converti/', self.admin_site.admin_view(self.converti_in_ordine), name='converti_offerta'),
        ]
        return custom_urls + urls

    def converti_in_ordine(self, request, richiesta_id):
        """Converte offerta approvata in ordine"""
        richiesta = RichiestaOfferta.objects.get(pk=richiesta_id)

        if not richiesta.can_convert():
            self.message_user(request, "Offerta non può essere convertita (stato non approvato o già convertita)", level='error')
            return redirect('admin:orders_richiestaofferta_change', richiesta_id)

        # Crea ordine
        tipo_ordine_map = {
            'MATERIALE': 'STANDARD',
            'RINNOVO_GARANZIA': 'RINNOVO_GARANZIA',
            'SERVICE_CONTRACT': 'STANDARD',
        }

        ordine = Ordine.objects.create(
            numero_ordine=f"ORD-{richiesta.numero_richiesta}",
            richiesta_offerta=richiesta,
            fornitore=Fornitore.objects.first(),  # TODO: selezionare fornitore corretto
            data_ordine=timezone.now().date(),
            tipo_ordine=tipo_ordine_map.get(richiesta.tipo_richiesta, 'STANDARD'),
            note=f"Convertito da offerta {richiesta.numero_richiesta}\n\nRichiesta originale:\n{richiesta.richiesta_testuale}"
        )

        # Crea articoli ordine dalle righe offerta
        for riga in richiesta.righe.all():
            if riga.articolo:
                ArticoloOrdine.objects.create(
                    ordine=ordine,
                    articolo=riga.articolo,
                    quantita=riga.quantita,
                    note=f"Prezzo offerta: €{riga.prezzo_unitario}\n{riga.note}",
                    mesi_garanzia=riga.mesi_durata or ordine.mesi_garanzia_default
                )

        # Aggiorna richiesta
        richiesta.stato = 'CONVERTITA'
        richiesta.ordine_convertito = ordine
        richiesta.save()

        self.message_user(request, f"Offerta convertita in ordine {ordine.numero_ordine} con successo!")
        return redirect('admin:orders_ordine_change', ordine.pk)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        richiesta = RichiestaOfferta.objects.get(pk=object_id)
        extra_context['can_convert'] = richiesta.can_convert()
        extra_context['richiesta_id'] = object_id
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
