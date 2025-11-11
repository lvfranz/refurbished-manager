# 🚀 Quick Start Guide - Gestionale Refurbished

## ✅ Sistema Pronto all'Uso!

Il tuo gestionale ordini refurbished è stato creato con successo e il database è già popolato con dati di esempio.

## 📋 Cosa è Stato Fatto

✅ Creata app Django "orders"  
✅ Implementati tutti i modelli (Clienti, Fornitori, Ordini, RMA, Service Contract, SLA)  
✅ Configurato pannello di amministrazione completo  
✅ Create viste per Dashboard, Ricerca e Scadenze  
✅ Applicate migrazioni al database  
✅ Popolato database con dati di esempio  

## 🎯 Prossimi Passi

### 1. Crea un Superuser

Prima di accedere al sistema, crea un utente amministratore:

```bash
python manage.py createsuperuser
```

Ti verrà chiesto di inserire:
- Username (es: admin)
- Email (opzionale)
- Password (deve essere sicura)

### 2. Avvia il Server

```bash
python manage.py runserver
```

Il server sarà disponibile su: **http://127.0.0.1:8000/**

### 3. Accedi al Sistema

Apri il browser e vai a:

#### 🏠 Dashboard Principale
**http://127.0.0.1:8000/**
- Visualizza statistiche generali
- Ultimi ordini
- RMA aperti

#### 🔍 Ricerca
**http://127.0.0.1:8000/orders/search/**
- Cerca articoli per nome, seriale
- Cerca clienti
- Cerca ordini

#### ⏰ Scadenze
**http://127.0.0.1:8000/orders/scadenze/**
- Monitora garanzie in scadenza
- Monitora service contract in scadenza

#### ⚙️ Admin Django
**http://127.0.0.1:8000/admin/**
- Gestisci tutti i dati
- Crea ordini, clienti, fornitori
- Apri RMA
- Gestisci service contract

Login con le credenziali create al punto 1.

## 📊 Dati di Esempio Già Presenti

Il database include:
- **3 SLA** predefiniti (Basic, Advanced, Premium)
- **3 Fornitori** (Dell, HP, Lenovo)
- **3 Clienti** con 4 sedi totali
- **2 Service Contract** (uno in scadenza tra 20 giorni)
- **7 Ordini** di vari tipi (Standard, RMA, Rinnovo Garanzia)
- **8 Articoli** con e senza numero seriale
- **1 RMA** aperto

## 🎓 Come Usare il Sistema

### Creare un Nuovo Ordine

1. Vai su: **http://127.0.0.1:8000/admin/**
2. Clicca su **"Ordini"** → **"Aggiungi ordine"**
3. Compila:
   - Numero ordine (es: ORD-2025-001)
   - Seleziona fornitore
   - Data ordine
   - Tipo ordine
4. Nella sezione articoli, clicca **"Aggiungi un altro Articolo Ordine"**:
   - Articolo (es: Dell Latitude 5430)
   - Descrizione
   - Numero seriale (opzionale - se presente, quantità = 1)
   - Quantità (se no seriale)
   - Assegna a cliente/sede
   - Mesi garanzia (default 12)
5. Clicca **"Salva"**

La data di scadenza garanzia viene calcolata automaticamente!

### Aprire un RMA

1. Nell'admin, vai su **"RMA"** → **"Aggiungi RMA"**
2. Compila:
   - Numero RMA (es: RMA-2025-001)
   - Seleziona articolo originale
   - Motivo dell'RMA
   - Stato (default: Aperto)
   - Se articolo fuori garanzia, spunta "Override garanzia"
3. Salva
4. Crea un ordine fornitore di tipo "RMA" e collegalo

### Cercare un Articolo

1. Vai su: **http://127.0.0.1:8000/orders/search/**
2. Digita:
   - Nome articolo (es: "Dell")
   - Numero seriale (es: "SN-DELL-001")
   - Cliente (es: "Acme")
3. Seleziona tipo di ricerca o lascia "Tutto"
4. Clicca **"Cerca"**

### Monitorare Scadenze

1. Vai su: **http://127.0.0.1:8000/orders/scadenze/**
2. Vedrai organizzato per sezioni:
   - Garanzie scadute (⚠️)
   - Garanzie in scadenza 30 giorni (⏰)
   - Garanzie in scadenza 60 giorni (📅)
   - Service Contract scaduti/in scadenza

## 🔑 Funzionalità Chiave

### ✨ Automazioni
- ✅ Calcolo automatico data scadenza garanzia
- ✅ Quantità forzata a 1 se presente numero seriale
- ✅ Validazione apertura RMA in base a garanzia
- ✅ Verifica unicità numeri seriali

### 🔗 Collegamenti
- ✅ Ordini RMA collegati all'ordine originale
- ✅ Ordini rinnovo garanzia collegati all'ordine materiale
- ✅ Service Contract rinnovabili
- ✅ RMA collegati agli ordini fornitore

### 📊 Reporting
- ✅ Dashboard con statistiche real-time
- ✅ Ricerca multi-criterio
- ✅ Monitoring scadenze proattivo

## 🛠️ Comandi Utili

```bash
# Avvia server
python manage.py runserver

# Crea superuser
python manage.py createsuperuser

# Crea nuove migrazioni (dopo modifiche ai modelli)
python manage.py makemigrations

# Applica migrazioni
python manage.py migrate

# Shell interattiva Django
python manage.py shell

# Verifica errori
python manage.py check
```

## 📁 Struttura Progetto

```
Refurbished/
├── manage.py
├── requirements.txt
├── README.md
├── QUICKSTART.md (questo file)
├── populate_db.py (script dati esempio)
├── Refurbished/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── orders/
│   ├── models.py (tutte le tabelle)
│   ├── admin.py (interfaccia admin)
│   ├── views.py (dashboard, ricerca, scadenze)
│   ├── urls.py
│   └── migrations/
└── templates/
    └── orders/
        ├── base.html
        ├── dashboard.html
        ├── search.html
        └── scadenze.html
```

## 💡 Tips & Tricks

### Filtrare nell'Admin
- Usa i filtri laterali per filtrare per fornitore, cliente, stato
- Usa la barra di ricerca per trovare rapidamente

### Inline Editing
- Puoi aggiungere sedi cliente direttamente dalla pagina del cliente
- Puoi aggiungere articoli direttamente dalla pagina dell'ordine

### Badge Colorati
- 🟢 Verde = In garanzia / Attivo
- 🔴 Rosso = Fuori garanzia / Scaduto
- 🟠 Arancione = In scadenza

### Date Hierarchy
- Usa la navigazione per data in cima alle liste
- Filtra rapidamente per anno/mese/giorno

## ❓ FAQ

**Q: Come faccio a vedere tutti gli articoli di un cliente?**  
A: Vai in Admin → Articoli Ordini → Filtra per "Sede cliente → Cliente"

**Q: Come collego un ordine RMA all'ordine originale?**  
A: Nell'ordine RMA, seleziona "Ordine originale rma" e scegli l'ordine

**Q: Posso avere sia garanzia che service contract?**  
A: Il service contract ha priorità. Se assegnato, sovrascrive la garanzia standard.

**Q: Cosa succede se inserisco un seriale con quantità > 1?**  
A: Il sistema forza automaticamente quantità = 1

**Q: Come rinnovo un service contract?**  
A: Crea un nuovo contract, poi in "Rinnovi Service Contract" collega vecchio e nuovo

## 🎉 Buon Lavoro!

Il sistema è pronto per essere usato. Inizia creando il tuo primo ordine!

Per la documentazione completa, vedi **README.md**

---

**Nota**: Questo è un ambiente di sviluppo. Per produzione, configura:
- Database production (PostgreSQL/MySQL)
- SECRET_KEY sicura
- DEBUG = False
- ALLOWED_HOSTS configurato
- Static files configurati
- HTTPS

