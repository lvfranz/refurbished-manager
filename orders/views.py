from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import ArticoloOrdine, Ordine, Cliente


@login_required
def ordine_detail_view(request, pk):
    """Vista dettaglio ordine con tutti gli articoli"""
    ordine = get_object_or_404(Ordine.objects.select_related('fornitore'), pk=pk)
    articoli = ordine.articoli.select_related('sede_cliente__cliente', 'service_contract').all()

    # Ordini correlati
    ordini_rma = ordine.ordini_rma.select_related('fornitore').all()
    ordini_estensione = ordine.ordini_estensione_garanzia.select_related('fornitore').all()

    context = {
        'ordine': ordine,
        'articoli': articoli,
        'ordini_rma': ordini_rma,
        'ordini_estensione': ordini_estensione,
    }

    return render(request, 'orders/ordine_detail.html', context)


@login_required
def search_view(request):
    """Vista di ricerca generale"""
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')

    results = {
        'articoli': [],
        'ordini': [],
        'clienti': [],
    }

    if query:
        if search_type in ['all', 'articolo']:
            # Ricerca per articolo e seriale
            results['articoli'] = ArticoloOrdine.objects.filter(
                Q(articolo__codice_articolo__icontains=query) |
                Q(articolo__descrizione__icontains=query) |
                Q(articolo__categoria__icontains=query) |
                Q(articolo__costruttore__icontains=query) |
                Q(numero_seriale__icontains=query) |
                Q(note__icontains=query)
            ).select_related('ordine', 'sede_cliente', 'service_contract', 'articolo')[:50]

        if search_type in ['all', 'cliente']:
            # Ricerca per cliente con sedi, ordini e articoli
            clienti = Cliente.objects.filter(
                nome__icontains=query
            ).prefetch_related('sedi')[:50]

            # Per ogni cliente, aggiungi info aggiuntive
            clienti_dettagliati = []
            for cliente in clienti:
                # Sedi del cliente
                sedi = cliente.sedi.all()

                # Ordini del cliente (tramite sede_default)
                ordini = Ordine.objects.filter(
                    sede_default__cliente=cliente
                ).select_related('fornitore').order_by('-data_ordine')[:20]

                # Articoli del cliente (tramite sede_cliente)
                articoli = ArticoloOrdine.objects.filter(
                    sede_cliente__cliente=cliente
                ).select_related('articolo', 'ordine', 'sede_cliente', 'service_contract').order_by('-ordine__data_ordine')[:50]

                # Service contracts del cliente
                from .models import ServiceContract
                service_contracts = ServiceContract.objects.filter(
                    cliente=cliente
                ).select_related('sla').order_by('-data_inizio')[:20]

                clienti_dettagliati.append({
                    'cliente': cliente,
                    'sedi': sedi,
                    'ordini': ordini,
                    'articoli': articoli,
                    'service_contracts': service_contracts,
                    'num_sedi': sedi.count(),
                    'num_ordini': ordini.count(),
                    'num_articoli': articoli.count(),
                    'num_contracts': service_contracts.count(),
                })

            results['clienti'] = clienti_dettagliati

        if search_type in ['all', 'ordine']:
            # Ricerca per ordine
            results['ordini'] = Ordine.objects.filter(
                Q(numero_ordine__icontains=query) |
                Q(fornitore__nome__icontains=query)
            ).select_related('fornitore')[:50]

    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
    }

    return render(request, 'orders/search.html', context)


@login_required
def scadenze_view(request):
    """Vista per monitorare le scadenze garanzie e service contract"""
    from datetime import date, timedelta

    oggi = date.today()
    prossimi_30_giorni = oggi + timedelta(days=30)
    prossimi_60_giorni = oggi + timedelta(days=60)

    # Garanzie in scadenza
    garanzie_scadute = ArticoloOrdine.objects.filter(
        data_scadenza_garanzia__lt=oggi,
        service_contract__isnull=True
    ).select_related('ordine', 'sede_cliente')[:100]

    garanzie_30_giorni = ArticoloOrdine.objects.filter(
        data_scadenza_garanzia__gte=oggi,
        data_scadenza_garanzia__lte=prossimi_30_giorni,
        service_contract__isnull=True
    ).select_related('ordine', 'sede_cliente')[:100]

    garanzie_60_giorni = ArticoloOrdine.objects.filter(
        data_scadenza_garanzia__gte=prossimi_30_giorni,
        data_scadenza_garanzia__lte=prossimi_60_giorni,
        service_contract__isnull=True
    ).select_related('ordine', 'sede_cliente')[:100]

    # Service contract in scadenza
    from .models import ServiceContract

    contracts_scaduti = ServiceContract.objects.filter(
        data_fine__lt=oggi,
        attivo=True
    ).select_related('cliente', 'sla')[:100]

    contracts_30_giorni = ServiceContract.objects.filter(
        data_fine__gte=oggi,
        data_fine__lte=prossimi_30_giorni,
        attivo=True
    ).select_related('cliente', 'sla')[:100]

    contracts_60_giorni = ServiceContract.objects.filter(
        data_fine__gte=prossimi_30_giorni,
        data_fine__lte=prossimi_60_giorni,
        attivo=True
    ).select_related('cliente', 'sla')[:100]

    context = {
        'oggi': oggi,
        'garanzie_scadute': garanzie_scadute,
        'garanzie_30_giorni': garanzie_30_giorni,
        'garanzie_60_giorni': garanzie_60_giorni,
        'contracts_scaduti': contracts_scaduti,
        'contracts_30_giorni': contracts_30_giorni,
        'contracts_60_giorni': contracts_60_giorni,
    }

    return render(request, 'orders/scadenze.html', context)


@login_required
def dashboard_view(request):
    """Dashboard principale"""
    from .models import RMA, ServiceContract
    from datetime import date

    oggi = date.today()

    stats = {
        'totale_articoli': ArticoloOrdine.objects.count(),
        'articoli_in_garanzia': ArticoloOrdine.objects.filter(
            data_scadenza_garanzia__gte=oggi
        ).count(),
        'rma_aperti': RMA.objects.filter(stato='APERTO').count(),
        'service_contracts_attivi': ServiceContract.objects.filter(
            attivo=True,
            data_fine__gte=oggi
        ).count(),
    }

    # Ultimi ordini
    ultimi_ordini = Ordine.objects.select_related('fornitore')[:10]

    # RMA recenti
    rma_recenti = RMA.objects.select_related(
        'articolo_originale',
        'ordine_fornitore'
    ).filter(stato='APERTO')[:10]

    context = {
        'stats': stats,
        'ultimi_ordini': ultimi_ordini,
        'rma_recenti': rma_recenti,
    }

    return render(request, 'orders/dashboard.html', context)

