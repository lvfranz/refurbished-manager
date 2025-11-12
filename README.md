# 📦 Gestionale Ordini Refurbished

Sistema di gestione completo per ordini di materiale refurbished con gestione garanzie, service contract e RMA.

## 📚 Documentazione

📘 **[GUIDA UTENTE COMPLETA - Estensione Garanzia](GUIDA_UTENTE_ESTENSIONE_GARANZIA.md)**
- Tutto quello che devi sapere sul sistema di estensione garanzia
- Procedura operativa passo-passo
- Esempi pratici e FAQ
- Troubleshooting e best practices

## 🚀 Caratteristiche Principali

### 📋 Gestione Completa

1. **Clienti e Sedi**
   - Gestione clienti con nome
   - Sedi multiple per cliente con indirizzo completo
   
2. **Fornitori**
   - Nome fornitore
   - Riferimento commerciale
   - Contatti (email, telefono)

3. **SLA (Service Level Agreement)**
   - SLA predefiniti con tempi di risposta e risoluzione
   - Utilizzabili nei Service Contract

4. **Service Contract**
   - Contratti di assistenza per i clienti
   - Associazione SLA
   - Date di validità
   - Possibilità di rinnovo

5. **Ordini**
   - Ordini standard
   - Ordini RMA (collegati all'ordine originale)
   - Ordini di rinnovo garanzia (collegati all'ordine del materiale)
   - Tracking fornitore e data

6. **Articoli Ordine**
   - Articolo con descrizione
   - Numero seriale (opzionale)
   - Quantità automatica a 1 se presente seriale
   - Assegnazione a cliente/sede
   - Calcolo automatico scadenza garanzia
   - Possibilità di associare Service Contract invece della garanzia standard

7. **RMA (Return Merchandise Authorization)**
   - Apertura RMA per articoli in garanzia
   - Override per forzare apertura fuori garanzia
   - Creazione automatica ordine fornitore collegato
   - Stati: Aperto, In Lavorazione, Chiuso, Annullato

### 🔍 Funzionalità di Ricerca

Il sistema include una ricerca avanzata che permette di cercare per:
- Articolo
- Numero seriale
- Cliente
- Prodotto
- Ordine
- Fornitore

### ⏰ Monitoraggio Scadenze

Dashboard dedicata per monitorare:
- Garanzie scadute
- Garanzie in scadenza (30 giorni)
- Garanzie in scadenza (60 giorni)
- Service Contract scaduti
- Service Contract in scadenza (30 e 60 giorni)

### 📊 Dashboard

- Statistiche in tempo reale
- Ultimi ordini inseriti
- RMA aperti
- Service Contract attivi

## 🛠️ Installazione

1. **Crea ambiente virtuale** (se non già fatto):
```bash
python -m venv .venv
.venv\Scripts\activate
```

2. **Installa dipendenze**:
```bash
pip install -r requirements.txt
```

3. **Applica migrazioni** (già fatto):
```bash
python manage.py migrate
```

4. **Crea superuser**:
```bash
python manage.py createsuperuser
```
Inserisci username, email e password per l'amministratore.

5. **Popola database con dati di esempio** (opzionale):
```bash
python populate_db.py
```

6. **Avvia server di sviluppo**:
```bash
python manage.py runserver
```

7. **Accedi al sistema**:
   - Dashboard: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - Ricerca: http://127.0.0.1:8000/orders/search/
   - Scadenze: http://127.0.0.1:8000/orders/scadenze/

## 📖 Guida all'Uso

### Creazione di un Ordine Standard

1. Accedi all'admin Django
2. Vai su "Ordini" → "Aggiungi ordine"
3. Compila i campi:
   - Numero ordine
   - Fornitore
   - Data ordine
   - Tipo: "Ordine Standard"
4. Aggiungi articoli inline:
   - Se inserisci un numero seriale, la quantità sarà automaticamente 1
   - Se non inserisci seriale, puoi specificare qualsiasi quantità
   - Assegna l'articolo a una sede cliente
   - Specifica i mesi di garanzia (default: 12)
5. La data di scadenza garanzia viene calcolata automaticamente

### Gestione Service Contract

1. Crea un Service Contract:
   - Associa un cliente
   - Scegli un SLA
   - Imposta date inizio e fine
2. Quando crei/modifichi un articolo, puoi associarlo al Service Contract
3. Se un articolo ha un Service Contract, questo ha priorità sulla garanzia standard

### Apertura RMA

1. Trova l'articolo nell'admin
2. Crea un nuovo RMA:
   - Seleziona l'articolo originale
   - Inserisci il motivo
   - Se l'articolo è fuori garanzia, attiva "Override garanzia"
3. Il sistema verifica automaticamente se l'RMA può essere aperto
4. Crea un ordine fornitore di tipo "RMA" e collegalo all'RMA

### Rinnovo Garanzia

1. Crea un nuovo ordine di tipo "Rinnovo Garanzia"
2. Nel campo "Ordine materiale collegato" seleziona l'ordine originale
3. Aggiungi l'articolo "Estensione Garanzia"

### Rinnovo Service Contract

1. Crea un nuovo Service Contract per il rinnovo
2. Vai su "Rinnovi Service Contracts" → "Aggiungi"
3. Collega il contratto originale con quello nuovo

## 🔐 Regole di Business

### Articoli con Seriale
- Se viene inserito un numero seriale, la quantità è **automaticamente forzata a 1**
- Il numero seriale è **unico** in tutto il sistema
- Validazione automatica per evitare duplicati

### Garanzia
- La data di scadenza viene **calcolata automaticamente** in base ai mesi di garanzia
- Se un articolo ha un Service Contract, questo ha **priorità** sulla garanzia standard
- La verifica dello stato di garanzia considera entrambi i tipi

### RMA
- Un RMA può essere aperto **solo se l'articolo è in garanzia**
- È possibile forzare l'apertura con **override_garanzia**
- Ogni RMA può essere collegato a un ordine fornitore
- Gli RMA sono collegati all'ordine originale tramite il campo **ordine_originale_rma**

### Ordini Speciali
- **Ordini RMA**: collegati all'ordine originale
- **Ordini Rinnovo Garanzia**: collegati all'ordine del materiale
- Questi collegamenti permettono di tracciare la storia completa

## 📊 Modelli Dati

### Cliente
- nome
- sedi (relazione one-to-many)

### SedeCliente
- cliente (FK)
- nome_sede
- indirizzo, città, CAP, provincia

### Fornitore
- nome
- commerciale_riferimento
- email, telefono

### SLA
- nome
- tempo_risposta_ore
- tempo_risoluzione_ore

### ServiceContract
- numero_contratto
- cliente (FK)
- sla (FK)
- data_inizio, data_fine
- attivo

### Ordine
- numero_ordine
- fornitore (FK)
- data_ordine
- tipo_ordine (STANDARD, RMA, RINNOVO_GARANZIA)
- ordine_originale_rma (FK self)
- ordine_materiale_collegato (FK self)

### ArticoloOrdine
- ordine (FK)
- articolo
- descrizione
- numero_seriale (unique, optional)
- quantita
- sede_cliente (FK)
- mesi_garanzia
- data_scadenza_garanzia (auto-calcolata)
- service_contract (FK, optional)

### RMA
- numero_rma
- articolo_originale (FK)
- data_apertura
- motivo
- stato
- override_garanzia
- ordine_fornitore (FK)

## 🎨 Interfaccia Admin

L'interfaccia admin è completamente personalizzata con:
- **Liste filtrabili** per tutti i modelli
- **Ricerca avanzata** su campi multipli
- **Inline editing** per relazioni (es. sedi cliente, articoli ordine)
- **Badge colorati** per stati e garanzie
- **Organizzazione gerarchica** delle date

## 🔍 Ricerca Avanzata

La pagina di ricerca permette di:
- Cercare in tutti i campi contemporaneamente
- Filtrare per tipo (Articoli, Clienti, Ordini)
- Vedere risultati organizzati per categoria
- Visualizzare stato garanzia in tempo reale

## 📅 Monitoraggio Scadenze

La dashboard scadenze mostra:
- **Scadenze passate** (in rosso)
- **Scadenze imminenti** (30 giorni, in arancione)
- **Scadenze future** (60 giorni)
- Sia per garanzie che per Service Contract

## 🌍 Localizzazione

- Interfaccia in **Italiano**
- Timezone: **Europe/Rome**
- Formati data italiani (dd/mm/yyyy)

## 🚀 Prossimi Sviluppi Possibili

- Export Excel/PDF
- Email automatiche per scadenze
- Dashboard con grafici
- Report personalizzati
- Storico modifiche
- Upload documenti/fatture
- Tracking spedizioni
- Notifiche push

## 📝 Note

- Il database utilizzato è **SQLite** (adatto per sviluppo)
- Per produzione, configurare PostgreSQL o MySQL
- Backup regolari consigliati
- Log automatici tramite Django admin

## 👨‍💻 Supporto

Per problemi o domande, contattare l'amministratore del sistema.

---

**Versione**: 1.0  
**Data**: Novembre 2025  
**Framework**: Django 5.2.8

