// Version 1.0.1 - Prefill ordine articoli
(function($) {
    "use strict";

    function log(message) {
        console.log("[Refurbished Admin] " + message);
    }

    function getDefaults() {
        const sedeId = $('#id_sede_default').val();
        const mesi = $('#id_mesi_garanzia_default').val();
        return { sedeId, mesi };
    }

    function applyDefaultsToRow($row) {
        const defaults = getDefaults();
        if (!defaults.sedeId && !defaults.mesi) return;

        log(`Applying defaults to row: ${$row.attr('id')}`);

        // Applica Sede Cliente
        const $sedeSelect = $row.find('select[name$="-sede_cliente"]');
        if (defaults.sedeId && !$sedeSelect.val()) {
            // Aggiungi l'opzione se non esiste (per autocomplete)
            if ($sedeSelect.find('option[value="' + defaults.sedeId + '"]').length === 0) {
                const sedeText = $('#id_sede_default option:selected').text();
                $sedeSelect.append(new Option(sedeText, defaults.sedeId, true, true));
            }
            $sedeSelect.val(defaults.sedeId).trigger('change');
            log(`- Sede impostata a: ${defaults.sedeId}`);
        }

        // Applica Mesi Garanzia
        const $mesiInput = $row.find('input[name$="-mesi_garanzia"]');
        if (defaults.mesi && (!$mesiInput.val() || $mesiInput.val() === '12')) {
            $mesiInput.val(defaults.mesi);
            log(`- Mesi garanzia impostati a: ${defaults.mesi}`);
        }
    }

    function applyToAllRows() {
        $('.dynamic-articoloordine_set').each(function() {
            applyDefaultsToRow($(this));
        });
    }

    $(document).ready(function() {
        log("order_inline_defaults.js loaded.");

        // Applica al caricamento iniziale
        applyToAllRows();

        // Applica quando cambiano i valori di default
        $('#id_sede_default, #id_mesi_garanzia_default').on('change', function() {
            log("Default values changed, updating all rows.");
            applyToAllRows();
        });

        // Applica quando viene aggiunta una nuova riga
        $(document).on('formset:added', function(event, $row, formsetName) {
            if (formsetName === 'articoloordine_set') {
                log("New row added, applying defaults.");
                applyDefaultsToRow($row);
            }
        });
    });

})(django.jQuery);
