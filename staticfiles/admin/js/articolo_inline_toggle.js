// JavaScript per gestire mostra/nascondi dettagli articoli ordine
(function($) {
    $(document).ready(function() {
        // Aggiungi pulsante "Mostra dettagli" per ogni riga
        function addToggleButtons() {
            $('.dynamic-articoloordine_set').each(function() {
                var $row = $(this);

                // Non aggiungere se già presente
                if ($row.find('.toggle-details-btn').length > 0) {
                    return;
                }

                // Trova la cella quantità e aggiungi il pulsante lì
                var $quantitaCell = $row.find('.field-quantita');
                if ($quantitaCell.length > 0) {
                    var $btn = $('<button type="button" class="toggle-details-btn" title="Mostra/Nascondi Sede e Garanzia">📋</button>');

                    $btn.on('click', function(e) {
                        e.preventDefault();
                        $row.toggleClass('show-details');

                        if ($row.hasClass('show-details')) {
                            $(this).text('📋 Nascondi');
                        } else {
                            $(this).text('📋');
                        }
                    });

                    $quantitaCell.append($btn);
                }
            });
        }

        // Aggiungi info box sui default applicati
        function addDefaultInfo() {
            var $ordineForm = $('.field-sede_default, .field-mesi_garanzia_default').closest('fieldset');

            if ($ordineForm.length > 0 && !$('.default-info').length) {
                var sedeDefault = $('.field-sede_default select option:selected').text();
                var garanziaDefault = $('.field-mesi_garanzia_default input').val();

                if (sedeDefault && sedeDefault !== '---------' || garanziaDefault) {
                    var infoHtml = '<div class="default-info">';
                    infoHtml += '<strong>ℹ️ Default Applicati:</strong> ';

                    var parts = [];
                    if (sedeDefault && sedeDefault !== '---------') {
                        parts.push('Sede: ' + sedeDefault);
                    }
                    if (garanziaDefault) {
                        parts.push('Garanzia: ' + garanziaDefault + ' mesi');
                    }

                    infoHtml += parts.join(' | ');
                    infoHtml += ' <em>(applicati automaticamente ai nuovi articoli)</em>';
                    infoHtml += '</div>';

                    $('.inline-group:has(.dynamic-articoloordine_set)').prepend(infoHtml);
                }
            }
        }

        // Esegui all'avvio
        addToggleButtons();
        addDefaultInfo();

        // Ri-esegui quando vengono aggiunte nuove righe inline
        $('.add-row a, .grp-add-handler').on('click', function() {
            setTimeout(function() {
                addToggleButtons();
            }, 500);
        });

        // Gestisci anche il formset Django quando aggiunge righe dinamicamente
        if (typeof django !== 'undefined' && django.jQuery) {
            $(document).on('formset:added', function(event, $row, formsetName) {
                if (formsetName === 'articoli') {
                    setTimeout(function() {
                        addToggleButtons();
                    }, 100);
                }
            });
        }

        // Observer per righe aggiunte dinamicamente
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    setTimeout(function() {
                        addToggleButtons();
                    }, 100);
                }
            });
        });

        var inlineGroups = document.querySelector('.inline-group');
        if (inlineGroups) {
            observer.observe(inlineGroups, {
                childList: true,
                subtree: true
            });
        }
    });
})(django.jQuery);

