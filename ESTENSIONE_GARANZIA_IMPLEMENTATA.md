# Estensione Garanzia Implementata

## Funzionalità

È stata implementata la gestione dell'estensione della garanzia per gli ordini di tipo "RINNOVO_GARANZIA".

### Come Funziona

1. **Creazione Ordine di Rinnovo Garanzia**:
   - Crea un nuovo ordine selezionando tipo "Rinnovo Garanzia"
   - Inserisci i dati base dell'ordine (numero, fornitore, data, ecc.)
   - **IMPORTANTE**: Nel campo "Garanzia Default (mesi)" inserisci i **mesi di estensione** (es: 36 per 3 anni)

2. **Collegamento all'Ordine Originale**:
   - Dopo il salvataggio, seleziona l'ordine standard contenente gli articoli da estendere
   - Il sistema mostra solo gli ordini dello stesso cliente (se la sede è già impostata)
   - Carica il documento PDF dell'ordine di rinnovo

3. **Estensione Automatica della Garanzia**:
   - Il sistema estende automaticamente la garanzia di **tutti gli articoli** dell'ordine selezionato
   - L'estensione parte dalla **data di scadenza attuale** di ogni articolo (non dalla data odierna!)
   - Viene aggiornata sia la `data_scadenza_garanzia` che i `mesi_garanzia` totali

### Esempio Pratico

**Scenario**:
- Ordine Standard #SO-001 del 01/07/2021 con garanzia di 36 mesi
- Scadenza garanzia articoli: **01/07/2024**
- Il 20/06/2024 si crea un ordine di Rinnovo Garanzia con estensione di 36 mesi

**Risultato**:
- Nuova scadenza garanzia: **01/07/2024 + 36 mesi = 01/07/2027**
- Mesi garanzia totali: 36 + 36 = 72 mesi

### Campi Coinvolti

**Modello Ordine**:
- `tipo_ordine`: 'RINNOVO_GARANZIA'
- `mesi_garanzia_default`: Mesi di estensione (es: 36)
- `ordine_materiale_collegato`: FK all'ordine standard originale
- `pdf_ordine`: Documento PDF dell'ordine di rinnovo

**Modello ArticoloOrdine**:
- `data_scadenza_garanzia`: Estesa automaticamente
- `mesi_garanzia`: Aggiornato con il totale dei mesi

### Feedback Utente

- **Durante la selezione**: Il template mostra quanti mesi verranno aggiunti
- **Dopo il salvataggio**: Messaggio di conferma con numero di articoli estesi
- **Esempio**: "✅ Garanzia estesa di 36 mesi per 15 articoli dell'ordine SO-001"

### File Modificati

1. `orders/admin.py`:
   - Metodo `gestisci_articoli_view` aggiornato con logica di estensione
   - Context aggiornato per passare `mesi_estensione` al template

2. `templates/admin/orders/ordine_gestisci_articoli.html`:
   - Aggiunta visualizzazione mesi di estensione
   - Feedback visivo per ogni ordine selezionabile

3. `orders/models.py`:
   - Campo `sede_default` reso opzionale (blank=True) per ordini non standard

4. `orders/forms.py`:
   - Form `OrdineForm` con validazione condizionale (sede_default obbligatoria solo per ordini Standard)

### Note Tecniche

- L'estensione usa `dateutil.relativedelta` per il calcolo accurato dei mesi
- Gli articoli sotto Service Contract non vengono modificati (logica esistente)
- Il sistema filtra automaticamente gli ordini per cliente quando possibile
- La logica è backward-compatible con ordini esistenti

## Data Implementazione

10 Novembre 2025

