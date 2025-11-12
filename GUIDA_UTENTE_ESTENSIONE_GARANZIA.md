# 📘 Guida Utente Completa - Sistema Estensione Garanzia

**Versione:** 2.0 (Calcolo Dinamico)  
**Data:** 12 Novembre 2025

---

## 📑 Indice

1. [Introduzione](#introduzione)
2. [Come Funziona](#come-funziona)
3. [Procedura Operativa](#procedura-operativa)
4. [Esempi Pratici](#esempi-pratici)
5. [Domande Frequenti (FAQ)](#domande-frequenti-faq)
6. [Troubleshooting](#troubleshooting)
7. [Note Tecniche](#note-tecniche)

---

## 📖 Introduzione

Il sistema di **Estensione Garanzia** permette di rinnovare automaticamente la garanzia degli articoli già presenti in ordini esistenti.

### ✨ Caratteristiche Principali

- ✅ **Calcolo dinamico**: La garanzia estesa è calcolata in tempo reale, senza modificare il database
- ✅ **Reversibile**: Elimina l'ordine di rinnovo → la garanzia torna automaticamente al valore originale
- ✅ **Estensioni multiple**: Puoi aggiungere più rinnovi successivi (si sommano automaticamente)
- ✅ **Qualsiasi durata**: Da 1 anno fino a 10+ anni di estensione

### 🎯 Risposta alla Domanda Chiave

**"Cosa succede se elimino l'ordine di rinnovo?"**

✅ **Le date tornano automaticamente al valore originale!**

Il sistema NON modifica mai i dati nel database. Tutto è calcolato dinamicamente quando visualizzi gli articoli.

---

## 💡 Come Funziona

### Principio di Base

Quando crei un **Ordine di Rinnovo Garanzia** e lo colleghi a un ordine standard esistente, il sistema:

1. **Trova tutti gli ordini di rinnovo** collegati all'ordine originale
2. **Calcola dinamicamente** la scadenza: `scadenza_base + somma_estensioni`
3. **Mostra il risultato** quando visualizzi gli articoli
4. **Si aggiorna automaticamente** se elimini o modifichi i rinnovi

### Esempio Visivo

```
┌─────────────────────────────────────────────────────────┐
│ DATABASE (invariato)                                     │
├─────────────────────────────────────────────────────────┤
│ mesi_garanzia: 36                                       │
│ data_scadenza_garanzia: 01/07/2024                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ ORDINE RINNOVO collegato (+36 mesi)                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ VISUALIZZAZIONE (calcolata dinamicamente)               │
├─────────────────────────────────────────────────────────┤
│ Mesi totali: 72 (36 + 36)                              │
│ Scadenza estesa: 01/07/2027                            │
│ Stato: ✓ In Garanzia                                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ ELIMINI L'ORDINE RINNOVO                                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ VISUALIZZAZIONE (aggiornata automaticamente)            │
├─────────────────────────────────────────────────────────┤
│ Mesi totali: 36 (valore originale)                     │
│ Scadenza: 01/07/2024 (valore originale)                │
│ Stato: ✗ Scaduta                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Procedura Operativa

### Step 1: Crea l'Ordine di Rinnovo Garanzia

1. Vai su **Admin → Ordini → Aggiungi ordine**

2. Compila i dati base:
   - **Numero ordine**: es. "RG-2024-001"
   - **Fornitore**: seleziona il fornitore
   - **Data ordine**: data dell'ordine di rinnovo
   - **Tipo ordine**: seleziona **"Rinnovo Garanzia"**

3. **IMPORTANTE - Garanzia Default (mesi)**:
   - Inserisci i **mesi totali di ESTENSIONE** che vuoi aggiungere
   - Tabella di conversione:
     * 12 mesi = 1 anno
     * 24 mesi = 2 anni
     * 36 mesi = 3 anni
     * 48 mesi = 4 anni
     * 60 mesi = 5 anni
     * 72 mesi = 6 anni
     * ... e così via
   - **Formula**: Anni × 12 = Mesi
   - Esempio: 7 anni e mezzo = 7.5 × 12 = 90 mesi

4. Clicca **Salva e continua le modifiche**

### Step 2: Collega l'Ordine Originale

1. Dopo il salvataggio, vedrai la pagina di modifica ordine

2. Nella sezione **"Ordine Collegato"**:
   - Campo **"Ordine materiale collegato"**: seleziona l'ordine standard con gli articoli da estendere
   - Il sistema filtra automaticamente per cliente (se la sede è già impostata)

3. (Opzionale) Nella sezione **"Documento PDF"**:
   - Carica il PDF dell'ordine di rinnovo

4. Clicca **Salva**

### Step 3: Verifica l'Estensione

1. Nella sezione **"Estensione Garanzia"** vedrai:
   ```
   ✓ Estensione Attiva (Calcolo Dinamico)
   Articoli interessati: 15
   Estensione: +36 mesi
   
   💡 La garanzia è calcolata dinamicamente dalle view.
   Se elimini o scolleghi questo ordine, la garanzia torna
   automaticamente al valore originale.
   ```

2. Vai sulla pagina dell'**ordine originale** (quello standard)

3. Visualizza gli articoli - vedrai:
   ```
   Garanzia: 96 mesi
     📅 Base: 36 + Estens: 2
   Scadenza: 01/01/2032
     ⏱️ Base: 01/01/2024
   Stato: ✓ In Garanzia
   ```

---

## 📊 Esempi Pratici

### Esempio 1: Estensione Singola di 3 Anni

**Situazione Iniziale:**
- Ordine Standard #SO-044648 del 07/07/2021
- Garanzia originale: 36 mesi (3 anni)
- Scadenza originale: 07/07/2024
- Stato: Scaduta

**Azione:**
- 20/06/2024: Crei ordine Rinnovo Garanzia #RG-2024-001
- Inserisci: **36 mesi** di estensione (3 anni)
- Colleghi a ordine #SO-044648

**Risultato:**
- Nuova scadenza: **07/07/2027** (da 07/07/2024 + 36 mesi)
- Mesi totali: **72** (36 originali + 36 estensione)
- Stato: **✓ In Garanzia**

---

### Esempio 2: Estensione di 5 Anni

**Situazione Iniziale:**
- Ordine Standard #SO-123456 del 15/03/2020
- Garanzia originale: 24 mesi (2 anni)
- Scadenza originale: 15/03/2022
- Stato: Scaduta da tempo

**Azione:**
- 10/02/2022: Crei ordine Rinnovo Garanzia #RG-2022-015
- Inserisci: **60 mesi** di estensione (5 anni)
- Colleghi a ordine #SO-123456

**Risultato:**
- Nuova scadenza: **15/03/2027** (da 15/03/2022 + 60 mesi)
- Mesi totali: **84** (24 originali + 60 estensione)
- Stato: **✓ In Garanzia**

---

### Esempio 3: Estensioni Multiple (Rinnovi Successivi)

**Situazione Iniziale:**
- Ordine Standard #SO-789012 del 01/01/2019
- Garanzia originale: 12 mesi
- Prima scadenza: 01/01/2020

**Prima Estensione:**
- 15/12/2019: Ordine Rinnovo #RG-2019-100 → **+24 mesi**
- Scadenza dopo prima estensione: **01/01/2022**
- Mesi totali: **36** (12 + 24)

**Seconda Estensione:**
- 20/11/2021: Ordine Rinnovo #RG-2021-200 → **+36 mesi**
- Scadenza finale: **01/01/2025**
- Mesi totali: **72** (12 + 24 + 36)

**Terza Estensione:**
- 15/10/2024: Ordine Rinnovo #RG-2024-300 → **+48 mesi**
- Scadenza finale: **01/01/2029**
- Mesi totali: **120** (12 + 24 + 36 + 48)

💡 **Le estensioni si sommano automaticamente!**

---

### Esempio 4: Eliminazione di un Rinnovo

**Situazione:**
- Hai l'ordine Standard #SO-999 con 36 mesi
- Hai aggiunto 2 rinnovi:
  - Rinnovo A: +24 mesi
  - Rinnovo B: +36 mesi
- Totale visualizzato: 96 mesi

**Azione:**
- Elimini il Rinnovo B (quello da 36 mesi)

**Risultato Automatico:**
- Totale visualizzato: **60 mesi** (36 + 24)
- Scadenza ricalcolata automaticamente
- Il database dell'ordine originale **non è stato modificato**

---

## ❓ Domande Frequenti (FAQ)

### Q1: Posso rinnovare la garanzia per più anni alla volta?

**A:** Sì! Puoi inserire qualsiasi numero di mesi. Esempi:
- 60 mesi = 5 anni
- 120 mesi = 10 anni
- 90 mesi = 7 anni e mezzo

### Q2: Cosa succede se elimino l'ordine di rinnovo?

**A:** La garanzia torna automaticamente al valore originale (o a quello delle estensioni rimanenti se ce ne sono altre). Non viene modificato nulla nel database.

### Q3: Posso fare più rinnovi successivi?

**A:** Sì! Puoi aggiungere quanti rinnovi vuoi. Si sommano automaticamente in ordine cronologico.

### Q4: Come faccio ad annullare un'estensione?

**A:** Hai due opzioni:
1. **Elimina** l'ordine di rinnovo garanzia
2. **Scollega** l'ordine materiale (modifica ordine rinnovo → rimuovi collegamento)

In entrambi i casi, la garanzia torna automaticamente al valore precedente.

### Q5: L'estensione funziona anche per articoli già scaduti?

**A:** Sì! L'estensione parte sempre dalla scadenza originale dell'articolo, non dalla data odierna. Quindi anche articoli scaduti possono essere riportati in garanzia.

Esempio:
- Scadenza originale: 01/01/2020 (scaduta 5 anni fa)
- Estensione: +60 mesi
- Nuova scadenza: 01/06/2025 (5 anni dalla scadenza originale)

### Q6: Posso estendere solo alcuni articoli di un ordine?

**A:** No, l'estensione si applica a **tutti gli articoli** dell'ordine collegato. Se vuoi estendere solo alcuni articoli, dovrai creare ordini separati per quegli articoli.

### Q7: Gli articoli sotto Service Contract vengono estesi?

**A:** No, gli articoli già coperti da Service Contract mantengono la copertura del contratto. L'estensione garanzia si applica solo agli articoli con garanzia standard.

### Q8: Devo fare qualcosa manualmente dopo aver creato il rinnovo?

**A:** No! Tutto è automatico. Basta collegare l'ordine di rinnovo all'ordine originale e il sistema calcola automaticamente tutto.

---

## 🐛 Troubleshooting

### Problema: "Garanzia ancora scaduta dopo aver collegato l'ordine"

**Verifica:**
1. ✓ Stai visualizzando la pagina dell'**ordine originale** (non quello di rinnovo)?
2. ✓ L'ordine di rinnovo è **correttamente collegato**? (campo `ordine_materiale_collegato`)
3. ✓ I **mesi di estensione** sono impostati correttamente nel campo "Garanzia Default (mesi)"?
4. ✓ Hai **ricaricato la pagina** dopo aver salvato?

**Soluzione:**
- Il sistema calcola automaticamente quando visualizzi la pagina
- Prova a ricaricare la pagina (F5) o svuotare la cache del browser

---

### Problema: "Non vedo gli ordini da collegare"

**Causa:**
- Il filtro mostra solo ordini **Standard** del **stesso cliente**

**Soluzione:**
1. Verifica che l'ordine di rinnovo abbia una **sede cliente** impostata
2. Se necessario, imposta manualmente la sede prima di salvare
3. Gli ordini Standard dello stesso cliente appariranno automaticamente

---

### Problema: "Ho sbagliato i mesi di estensione"

**Soluzione:**
1. Apri l'ordine di rinnovo garanzia
2. Modifica il campo **"Garanzia Default (mesi)"**
3. Salva
4. La nuova estensione sarà calcolata automaticamente

---

### Problema: "Voglio annullare un'estensione"

**Soluzione Semplice:**

**Opzione A - Eliminazione:**
1. Vai sull'ordine di rinnovo garanzia
2. Clicca **"Elimina"**
3. Conferma
4. La garanzia torna automaticamente al valore originale

**Opzione B - Scollegamento:**
1. Apri l'ordine di rinnovo garanzia
2. Rimuovi il valore dal campo **"Ordine materiale collegato"**
3. Salva
4. La garanzia torna automaticamente al valore originale

💡 **Nessun dato viene modificato permanentemente!**

---

### Problema: "Ho più estensioni, quale conta?"

**Risposta:**
Tutte! Le estensioni si sommano in ordine cronologico:

```
Ordine Standard: 36 mesi (base)
+ Rinnovo 2022: +24 mesi
+ Rinnovo 2024: +36 mesi
+ Rinnovo 2026: +48 mesi
─────────────────────────────
Totale: 144 mesi (12 anni)
```

Ogni estensione aggiunge tempo alla scadenza calcolata dalle estensioni precedenti.

---

## 📋 Note Tecniche

### Calcolo Dinamico

Il sistema utilizza metodi sul modello `ArticoloOrdine` per calcolare la garanzia estesa:

1. **`get_estensioni_garanzia()`**
   - Trova tutti gli ordini di rinnovo collegati all'ordine dell'articolo
   - Ritorna lista di tuple (ordine_rinnovo, mesi_estensione)
   - Ordinati per data ordine

2. **`get_mesi_garanzia_totali()`**
   - Calcola: `mesi_base + somma(mesi_estensioni)`
   - Usato per visualizzare i mesi totali

3. **`get_data_scadenza_garanzia_estesa()`**
   - Parte dalla `data_scadenza_garanzia` base
   - Aggiunge ogni estensione in ordine cronologico
   - Ritorna la scadenza finale calcolata

4. **`is_in_garanzia()`**
   - Usa la scadenza estesa per verificare lo stato
   - Considera automaticamente tutte le estensioni

### Esempio di Codice Interno

```python
# Database (invariato)
articolo.mesi_garanzia = 36
articolo.data_scadenza_garanzia = 2024-07-01

# Estensioni trovate dinamicamente
estensioni = [
    (Ordine_Rinnovo_1, 24),  # +24 mesi
    (Ordine_Rinnovo_2, 36),  # +36 mesi
]

# Calcolo dinamico
totale_mesi = 36 + 24 + 36 = 96
scadenza_estesa = 2024-07-01 + 24 mesi + 36 mesi = 2029-07-01

# Visualizzazione
articolo.get_mesi_garanzia_totali() → 96
articolo.get_data_scadenza_garanzia_estesa() → 2029-07-01
articolo.is_in_garanzia() → True

# Database (ancora invariato!)
articolo.mesi_garanzia = 36
articolo.data_scadenza_garanzia = 2024-07-01
```

### Vantaggi Tecnici

- ✅ **Nessuna migrazione database** necessaria
- ✅ **Backward compatible** con dati esistenti
- ✅ **Testabile facilmente** (metodi puri senza side effects)
- ✅ **Manutenibile** (logica centralizzata nel modello)
- ✅ **Performance** (query efficienti con prefetch)

---

## 📅 Tabella di Conversione Mesi/Anni

Per facilitare l'inserimento dei mesi di estensione:

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
| 10 anni | 120 mesi | Estensione massima tipica |
| 15 anni | 180 mesi | |
| 20 anni | 240 mesi | |

💡 **Formula**: `Anni × 12 = Mesi`

Esempi:
- 3.5 anni = 3.5 × 12 = **42 mesi**
- 7.5 anni = 7.5 × 12 = **90 mesi**
- 2 anni e 3 mesi = 2.25 × 12 = **27 mesi**

---

## 🎯 Best Practices

### ✅ DO - Cose da Fare

1. **Imposta sempre i mesi di estensione** prima di collegare l'ordine
2. **Verifica la scadenza estesa** visualizzando l'ordine originale
3. **Usa nomi descrittivi** per gli ordini di rinnovo (es: "RG-2024-Cliente-3anni")
4. **Conserva il PDF** dell'ordine nella sezione "Documento PDF"
5. **Documenta nelle note** eventuali informazioni importanti sul rinnovo

### ❌ DON'T - Cose da Evitare

1. **Non modificare manualmente** i campi `mesi_garanzia` e `data_scadenza_garanzia` degli articoli
2. **Non creare ordini di rinnovo** senza collegarli (restano inutili)
3. **Non eliminare ordini standard** che hanno rinnovi collegati (potresti perdere traccia)
4. **Non dimenticare** di impostare i mesi di estensione nel campo "Garanzia Default"

---

## 🎉 Conclusione

Il sistema di Estensione Garanzia è:

- ✅ **Semplice**: Crea ordine, collega, fatto!
- ✅ **Sicuro**: Nessuna modifica permanente al database
- ✅ **Flessibile**: Estensioni multiple, qualsiasi durata
- ✅ **Reversibile**: Elimina ordine → garanzia torna al valore originale
- ✅ **Automatico**: Zero comandi manuali necessari

**Tutto è calcolato dinamicamente in tempo reale!**

---

## 📞 Supporto

Per problemi o domande non coperte da questa guida, contatta il supporto tecnico.

**Versione documento:** 2.0  
**Ultimo aggiornamento:** 12 Novembre 2025

---

*Questa guida sostituisce e consolida:*
- *ESTENSIONE_GARANZIA_IMPLEMENTATA.md*
- *GUIDA_ESTENSIONE_GARANZIA.md*
- *SOLUZIONE_FINALE_ESTENSIONE_DINAMICA.md*

