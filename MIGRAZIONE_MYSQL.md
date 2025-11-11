# 🔄 MIGRAZIONE A MYSQL - Guida Completa

## ✅ Modifiche Effettuate

### 1. **Modello SLA Aggiornato**
Ora include:
- ✅ **Disponibilità copertura**: 8x5, 9x5, 12x5, 24x7, NBD
- ✅ **Tempo di risposta** (in ore)
- ✅ **Tipo di intervento**: Solo Materiale, On-Site, Remoto, On-Site+Remoto

### 2. **Database Configurato per MySQL**
- ✅ Configurazione MySQL nel `settings.py`
- ✅ Supporto variabili d'ambiente
- ✅ Driver MySQL aggiunto a requirements

---

## 🚀 PROCEDURA DI INSTALLAZIONE

### Step 1: Installa MySQL Server

#### Opzione A - Windows (XAMPP)
1. Scarica XAMPP da: https://www.apachefriends.org/
2. Installa e avvia XAMPP Control Panel
3. Clicca "Start" su **MySQL**
4. Password di default root: *vuota*

#### Opzione B - Windows (MySQL Installer)
1. Scarica da: https://dev.mysql.com/downloads/installer/
2. Installa MySQL Server
3. Durante l'installazione, imposta la password per root

#### Opzione C - MySQL già installato
Se hai già MySQL, assicurati che sia in esecuzione.

---

### Step 2: Installa il Driver MySQL per Python

```bash
pip install mysqlclient
```

**⚠️ PROBLEMI SU WINDOWS?**

Se `mysqlclient` dà errori su Windows, usa l'alternativa:
```bash
pip uninstall mysqlclient
pip install pymysql
```

Poi aggiungi all'inizio di `Refurbished/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

### Step 3: Crea il Database MySQL

Apri MySQL e crea il database:

#### Con MySQL Command Line:
```bash
mysql -u root -p
```

Poi esegui:
```sql
CREATE DATABASE refurbished_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;
EXIT;
```

#### Con phpMyAdmin (se usi XAMPP):
1. Vai su http://localhost/phpmyadmin/
2. Clicca "Nuovo" nella sidebar sinistra
3. Nome database: `refurbished_db`
4. Collation: `utf8mb4_unicode_ci`
5. Clicca "Crea"

---

### Step 4: Configura le Credenziali

#### Opzione A - Variabili d'ambiente (CONSIGLIATO)

**Windows PowerShell:**
```powershell
$env:DB_NAME="refurbished_db"
$env:DB_USER="root"
$env:DB_PASSWORD="tua_password"
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
```

**Windows CMD:**
```cmd
set DB_NAME=refurbished_db
set DB_USER=root
set DB_PASSWORD=tua_password
set DB_HOST=localhost
set DB_PORT=3306
```

#### Opzione B - File .env (con python-dotenv)

1. Installa python-dotenv:
```bash
pip install python-dotenv
```

2. Crea file `.env` nella root del progetto:
```
DB_NAME=refurbished_db
DB_USER=root
DB_PASSWORD=tua_password
DB_HOST=localhost
DB_PORT=3306
```

3. Aggiungi all'inizio di `settings.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

#### Opzione C - Modifica diretta settings.py (SOLO DEV)
Nel file `settings.py`, modifica direttamente i valori di default:
```python
'NAME': 'refurbished_db',
'USER': 'root',
'PASSWORD': 'tua_password',  # Inserisci la tua password
'HOST': 'localhost',
'PORT': '3306',
```

---

### Step 5: Esegui le Migrazioni

```bash
# Crea le nuove migrazioni per il modello SLA aggiornato
python manage.py makemigrations

# Applica le migrazioni al database MySQL
python manage.py migrate
```

Se tutto funziona, vedrai:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, orders, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

### Step 6: Crea un Nuovo Superuser

```bash
python manage.py createsuperuser
```

Inserisci:
- Username
- Email (opzionale)
- Password

---

### Step 7: Popola il Database (Opzionale)

```bash
python populate_db.py
```

Questo creerà dati di esempio con i **nuovi SLA aggiornati**.

---

### Step 8: Avvia il Server

```bash
python manage.py runserver
```

Vai su: http://127.0.0.1:8000/

---

## 🎯 NUOVO MODELLO SLA

### Campi Disponibili

#### 1. **Nome**
Identificativo dello SLA (es: "Premium 24x7")

#### 2. **Disponibilità Copertura**
Scegli tra:
- **8x5**: Lun-Ven, 8:00-18:00
- **9x5**: Lun-Ven, 8:00-17:00
- **12x5**: Lun-Ven, 8:00-20:00
- **24x7**: 24 ore su 24, 7 giorni su 7
- **NBD**: Next Business Day

#### 3. **Tempo di Risposta**
Ore entro cui si risponde (es: 4 ore)

#### 4. **Tipo di Intervento**
Scegli tra:
- **Solo Materiale**: Solo invio materiale sostitutivo
- **On-Site**: Intervento presso il cliente
- **Remoto**: Intervento da remoto
- **On-Site + Remoto**: Entrambe le modalità

---

## 📋 Esempio di Utilizzo

### Creare uno SLA nell'Admin

1. Vai su: http://127.0.0.1:8000/admin/
2. Clicca su "SLA" → "Aggiungi SLA"
3. Compila:
   - **Nome**: Premium 24x7 On-Site
   - **Disponibilità**: 24x7 (24 ore su 24, 7 giorni su 7)
   - **Tempo risposta**: 2 ore
   - **Tipo intervento**: On-Site
   - **Descrizione**: SLA premium con intervento on-site garantito

---

## 🔍 Verifica Connessione MySQL

### Test Rapido
```bash
python manage.py dbshell
```

Se si apre la shell MySQL, la connessione funziona! ✅

Esci con:
```sql
EXIT;
```

---

## ⚠️ TROUBLESHOOTING

### Errore: "Can't connect to MySQL server"
✅ **Soluzione**: Assicurati che MySQL sia in esecuzione
- XAMPP: Avvia MySQL dal Control Panel
- Servizio Windows: Controlla nei servizi

### Errore: "Access denied for user 'root'@'localhost'"
✅ **Soluzione**: Password errata
- Controlla la password nelle variabili d'ambiente
- Con XAMPP, di default la password è vuota: `DB_PASSWORD=""`

### Errore: "Unknown database 'refurbished_db'"
✅ **Soluzione**: Devi creare il database
```sql
CREATE DATABASE refurbished_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Errore: "No module named 'MySQLdb'"
✅ **Soluzione**: Driver non installato
```bash
pip install mysqlclient
```

Se non funziona su Windows:
```bash
pip install pymysql
```
E aggiungi a `Refurbished/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Errore: "mysqlclient requires Microsoft Visual C++ 14.0"
✅ **Soluzione**: Usa PyMySQL invece
```bash
pip install pymysql
```

---

## 📊 Confronto SQLite vs MySQL

| Caratteristica | SQLite | MySQL |
|----------------|--------|-------|
| Performance | Buona per piccoli DB | Ottima per DB grandi |
| Concurrent users | Limitato | Eccellente |
| Produzione | Non consigliato | Consigliato |
| Backup | Copia file | mysqldump |
| Scalabilità | Limitata | Alta |

---

## 🎉 Vantaggi della Migrazione

✅ **Performance migliori** con molti utenti  
✅ **Gestione concurrent access** più robusta  
✅ **Backup e restore** professionali  
✅ **Pronto per produzione**  
✅ **SLA più dettagliati** (disponibilità, tipo intervento)  

---

## 🔄 Tornare a SQLite (se necessario)

Se vuoi tornare a SQLite:

1. Modifica `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

2. Esegui:
```bash
python manage.py migrate
```

---

## 📝 Checklist Completa

- [ ] MySQL Server installato e in esecuzione
- [ ] Driver Python installato (`mysqlclient` o `pymysql`)
- [ ] Database `refurbished_db` creato
- [ ] Credenziali configurate (env vars o .env)
- [ ] Migrazioni eseguite (`python manage.py migrate`)
- [ ] Superuser creato (`python manage.py createsuperuser`)
- [ ] Database popolato (opzionale: `python populate_db.py`)
- [ ] Server avviato e funzionante

---

## 🎯 Pronto!

Ora hai:
✅ MySQL configurato e funzionante  
✅ SLA con disponibilità copertura  
✅ SLA con tipo di intervento  
✅ Sistema pronto per produzione  

**Buon lavoro! 🚀**

