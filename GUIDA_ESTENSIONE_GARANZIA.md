# ✅ Sistema di Estensione Garanzia Automatica

## Come Funziona

Quando crei un **Ordine di Rinnovo Garanzia** e lo colleghi a un ordine standard, il sistema **calcola dinamicamente** la garanzia estesa **senza modificare il database**.

### 💡 Vantaggi del Calcolo Dinamico

- ✅ **Nessuna modifica ai dati**: I dati originali restano intatti
- ✅ **Reversibile**: Se elimini o scolleghi l'ordine di rinnovo, la garanzia torna automaticamente al valore originale
- ✅ **Estensioni multiple**: Puoi aggiungere più rinnovi successivi senza problemi
- ✅ **Sempre aggiornato**: La scadenza viene calcolata in tempo reale quando visualizzi gli articoli

---

## 📝 Procedura Operativa

### 1. Crea l'Ordine di Rinnovo Garanzia

1. Vai su **Admin → Ordini → Aggiungi ordine**
2. Compila i dati base:
   - **Numero ordine**: es. "RG-2024-001"
   - **Fornitore**: seleziona il fornitore
   - **Data ordine**: data dell'ordine di rinnovo
   - **Tipo ordine**: seleziona **"Rinnovo Garanzia"**
   - **Garanzia Default (mesi)**: **IMPORTANTE** - inserisci i mesi totali di ESTENSIONE
     - 12 mesi = 1 anno
     - 24 mesi = 2 anni
     - 36 mesi = 3 anni
     - 48 mesi = 4 anni
     - 60 mesi = 5 anni
     - ecc...
3. Clicca **Salva e continua le modifiche**

### 2. Collega l'Ordine Originale

1. Dopo il salvataggio, nella sezione **"Ordine Collegato"**:
   - Campo **"Ordine materiale collegato"**: seleziona l'ordine standard con gli articoli da estendere
2. (Opzionale) Carica il PDF dell'ordine nella sezione **"Documento PDF"**
3. Clicca **Salva**

### 3. Verifica l'Estensione

Nella sezione **"Estensione Garanzia"** vedrai un messaggio di conferma che l'estensione è attiva e verrà calcolata dinamicamente.

---

## 📊 Esempi Pratici

### Esempio 1: Estensione di 3 anni (36 mesi)

**Scenario:**
- Ordine Standard #SO-044648 del 07/07/2021
- Garanzia originale: 36 mesi (3 anni)
- Scadenza originale: 07/07/2024

**Azione:**
- 20/06/2024: Ordine Rinnovo Garanzia #RG-2024-001
- Estensione: **36 mesi** (3 anni)

**Risultato:**
- Nuova scadenza: **07/07/2027** (da 07/07/2024 + 36 mesi)
- Mesi totali: 72 (36 originali + 36 estensione)

---

### Esempio 2: Estensione di 5 anni (60 mesi)

**Scenario:**
- Ordine Standard #SO-123456 del 15/03/2020
- Garanzia originale: 24 mesi (2 anni)
- Scadenza originale: 15/03/2022

**Azione:**
- 10/02/2022: Ordine Rinnovo Garanzia #RG-2022-015
- Estensione: **60 mesi** (5 anni)

**Risultato:**
- Nuova scadenza: **15/03/2027** (da 15/03/2022 + 60 mesi)
- Mesi totali: 84 (24 originali + 60 estensione)

---

### Esempio 3: Doppia Estensione

**Scenario:**
- Ordine Standard #SO-789012 del 01/01/2019
- Garanzia originale: 12 mesi
- Prima scadenza: 01/01/2020

**Prima Estensione:**
- 15/12/2019: Ordine Rinnovo #RG-2019-100 → +24 mesi
- Scadenza dopo prima estensione: **01/01/2022**
- Mesi totali: 36

**Seconda Estensione:**
- 20/11/2021: Ordine Rinnovo #RG-2021-200 → +36 mesi
- Scadenza finale: **01/01/2025**
- Mesi totali: 72 (12 + 24 + 36)

💡 **Nota**: Puoi estendere la garanzia più volte! Ogni estensione parte dalla scadenza attuale.

---

## 📅 Tabella di Conversione Mesi/Anni

Per facilitare l'inserimento, usa questa tabella:

| Anni | Mesi | Note |
|------|------|------|
| 1 anno | 12 mesi | Estensione breve |
| 2 anni | 24 mesi | Estensione standard |
| 3 anni | 36 mesi | Estensione comune |
| 4 anni | 48 mesi | Estensione lunga |
| 5 anni | 60 mesi | Estensione molto lunga |
| 6 anni | 72 mesi | |
| 7 anni | 84 mesi | |
| 8 anni | 96 mesi | |
| 9 anni | 108 mesi | |
| 10 anni | 120 mesi | Estensione massima |

💡 **Formula**: Anni × 12 = Mesi  
   Esempio: 7 anni e mezzo = 7.5 × 12 = 90 mesi

---

## ⚙️ Logica Tecnica

### Calcolo Dinamico

L'estensione garanzia funziona attraverso **metodi sul modello ArticoloOrdine**:

1. **`get_estensioni_garanzia()`**: Trova tutti gli ordini di rinnovo garanzia collegati
2. **`get_data_scadenza_garanzia_estesa()`**: Calcola la scadenza sommando tutte le estensioni
3. **`get_mesi_garanzia_totali()`**: Calcola i mesi totali (base + estensioni)
4. **`is_in_garanzia()`**: Verifica se in garanzia usando la scadenza estesa

### Nessuna Modifica al Database

- I campi `mesi_garanzia` e `data_scadenza_garanzia` **restano invariati**
- Le estensioni vengono trovate tramite relazione `ordini_estensione_garanzia`
- La scadenza estesa è calcolata **on-the-fly** quando visualizzi gli articoli
- Se elimini un ordine di rinnovo, il calcolo si aggiorna automaticamente

### Esempio di Calcolo

```python
# Ordine Standard: 36 mesi, scadenza 01/07/2024
articolo.mesi_garanzia = 36
articolo.data_scadenza_garanzia = 2024-07-01

# Ordine Rinnovo 1: +24 mesi
# Ordine Rinnovo 2: +36 mesi

# Calcolo dinamico:
articolo.get_mesi_garanzia_totali() → 96 (36 + 24 + 36)
articolo.get_data_scadenza_garanzia_estesa() → 2029-07-01

# Nel database rimane:
articolo.mesi_garanzia = 36  # invariato
articolo.data_scadenza_garanzia = 2024-07-01  # invariato
```

---

## 🐛 Troubleshooting

### Problema: "Garanzia ancora scaduta dopo aver collegato l'ordine"

**Verifica:**
1. Assicurati di visualizzare la pagina dell'**ordine originale** (non quello di rinnovo)
2. L'ordine di rinnovo è correttamente collegato? (campo `ordine_materiale_collegato`)
3. I mesi di estensione sono impostati correttamente?

**Il sistema calcola automaticamente**: Basta ricaricare la pagina!

### Problema: "Voglio annullare un'estensione"

**Soluzione semplice:**
1. Vai sull'ordine di rinnovo garanzia
2. **Elimina l'ordine** OPPURE **scollega l'ordine materiale**
3. La garanzia torna automaticamente al valore originale (nessun dato modificato!)

### Problema: "Ho più estensioni, quale conta?"

**Risposta:** Tutte! Le estensioni si sommano in ordine cronologico:
- Ordine Rinnovo del 2022: +24 mesi
- Ordine Rinnovo del 2024: +36 mesi
- **Totale estensione**: +60 mesi

### Verifica Funzionamento

Per verificare che tutto funzioni:
```python
# Dalla shell Django
from orders.models import ArticoloOrdine

articolo = ArticoloOrdine.objects.get(pk=XXX)

# Visualizza info
print(f"Mesi base: {articolo.mesi_garanzia}")
print(f"Scadenza base: {articolo.data_scadenza_garanzia}")
print(f"Estensioni trovate: {len(articolo.get_estensioni_garanzia())}")
print(f"Mesi totali: {articolo.get_mesi_garanzia_totali()}")
print(f"Scadenza estesa: {articolo.get_data_scadenza_garanzia_estesa()}")
print(f"In garanzia? {articolo.is_in_garanzia()}")
```

---

## 📁 File Modificati

- **orders/admin.py**: Logica estensione automatica e manuale
- **orders/models.py**: Campo sede_default opzionale per ordini non standard
- **orders/forms.py**: Validazione condizionale
- **orders/management/commands/estendi_garanzia.py**: Comando terminale
- **orders/management/commands/check_order.py**: Verifica stato
- **templates/admin/orders/ordine_gestisci_articoli.html**: UI per selezione ordine

---

## 🎯 Best Practices

1. **Sempre impostare i mesi di estensione** nel campo "Garanzia Default (mesi)" prima di collegare l'ordine
2. **Verificare sempre** nella sezione "Estensione Garanzia" che l'estensione sia applicata
3. **Se l'estensione fallisce**, usare il pulsante per applicarla manualmente
4. **Conservare il PDF** dell'ordine di rinnovo nella sezione "Documento PDF"

---

**Data implementazione:** 12 Novembre 2025  
**Versione:** 1.0

