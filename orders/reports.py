from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Prefetch
from django.contrib.auth.decorators import login_required
from .models import ArticoloOrdine, Ordine, Cliente, RMA


@login_required
def report_articoli_sostituiti(request):
    """Report completo articoli sostituiti tramite RMA"""

    # Trova tutti gli RMA con articoli sostituiti
    rma_list = RMA.objects.select_related(
        'articolo_originale__articolo',
        'articolo_originale__ordine',
        'articolo_originale__sede_cliente__cliente',
        'ordine_fornitore'
    ).prefetch_related(
        'ordine_fornitore__articoli__articolo'
    ).order_by('-data_apertura')

    # Prepara dati per il report
    sostituzioni = []
    for rma in rma_list:
        articolo_vecchio = rma.articolo_originale

        # Trova articolo nuovo nell'ordine RMA
        articolo_nuovo = None
        if rma.ordine_fornitore:
            articoli_nuovi = rma.ordine_fornitore.articoli.all()
            if articoli_nuovi:
                articolo_nuovo = articoli_nuovi[0]  # Prendi il primo

        sostituzioni.append({
            'rma': rma,
            'articolo_vecchio': articolo_vecchio,
            'articolo_nuovo': articolo_nuovo,
            'cliente': articolo_vecchio.sede_cliente.cliente if articolo_vecchio.sede_cliente else None,
        })

    context = {
        'sostituzioni': sostituzioni,
        'total_rma': len(sostituzioni),
    }

    return render(request, 'orders/report_sostituzioni.html', context)


@login_required
def report_sostituzioni_cliente(request, cliente_id):
    """Report sostituzioni per uno specifico cliente"""

    cliente = get_object_or_404(Cliente, pk=cliente_id)

    # Trova tutti gli articoli del cliente con RMA
    articoli_cliente = ArticoloOrdine.objects.filter(
        sede_cliente__cliente=cliente
    ).select_related(
        'articolo',
        'ordine',
        'sede_cliente'
    )

    # Trova RMA per questi articoli
    rma_cliente = RMA.objects.filter(
        articolo_originale__sede_cliente__cliente=cliente
    ).select_related(
        'articolo_originale__articolo',
        'articolo_originale__ordine',
        'ordine_fornitore'
    ).prefetch_related(
        'ordine_fornitore__articoli__articolo'
    ).order_by('-data_apertura')

    # Prepara dati sostituzioni
    sostituzioni = []
    for rma in rma_cliente:
        articolo_vecchio = rma.articolo_originale

        # Trova articolo nuovo
        articolo_nuovo = None
        if rma.ordine_fornitore:
            articoli_nuovi = rma.ordine_fornitore.articoli.all()
            if articoli_nuovi:
                articolo_nuovo = articoli_nuovi[0]

        sostituzioni.append({
            'rma': rma,
            'articolo_vecchio': articolo_vecchio,
            'articolo_nuovo': articolo_nuovo,
            'sede': articolo_vecchio.sede_cliente,
        })

    context = {
        'cliente': cliente,
        'sostituzioni': sostituzioni,
        'total_articoli': articoli_cliente.count(),
        'total_rma': len(sostituzioni),
    }

    return render(request, 'orders/report_cliente_sostituzioni.html', context)

