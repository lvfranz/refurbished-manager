# 🚀 QUICK START - MySQL su Windows

## ⚡ Installazione Rapida (5 minuti)

### 1. Installa XAMPP (più facile per Windows)

1. **Scarica XAMPP**: https://www.apachefriends.org/download.html
2. **Installa** (lascia le impostazioni di default)
3. **Avvia XAMPP Control Panel**
4. Clicca **"Start"** su **MySQL**

✅ MySQL è ora in esecuzione!

---

### 2. Crea il Database

#### Opzione A - Con phpMyAdmin (più facile)
1. Apri browser: http://localhost/phpmyadmin/
2. Clicca **"Nuovo"** nella sidebar sinistra
3. Nome database: `refurbished_db`
4. Collation: `utf8mb4_unicode_ci`
5. Clicca **"Crea"**

#### Opzione B - Con MySQL Command Line
```bash
# Apri MySQL (password vuota con XAMPP)
mysql -u root

# Crea il database
CREATE DATABASE refurbished_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

---

### 3. Installa il Driver Python

```bash
pip install pymysql python-dotenv
```

**Nota**: Uso `pymysql` perché è più facile su Windows (niente compilazione)

---

### 4. Configura Password

**Se usi XAMPP** (password root vuota):

```bash
# PowerShell
$env:DB_PASSWORD=""

# CMD
set DB_PASSWORD=
```

**Se hai impostato una password**:
```bash
# PowerShell
$env:DB_PASSWORD="tua_password"

# CMD
set DB_PASSWORD=tua_password
```

---

### 5. Testa la Connessione

```bash
python test_mysql.py
```

Dovresti vedere:
```
✅ Connessione riuscita!
MySQL Version: 8.x.x
```

---

### 6. Applica le Migrazioni

```bash
python manage.py makemigrations
python manage.py migrate
```

Vedrai le tabelle create nel database.

---

### 7. Crea Superuser

```bash
python manage.py createsuperuser
```

---

### 8. Popola Database (Opzionale)

```bash
python populate_db.py
```

Questo crea:
- 4 SLA con i nuovi campi
- 3 Fornitori
- 3 Clienti con sedi
- 7 Ordini
- 8 Articoli
- RMA di esempio

---

### 9. Avvia!

```bash
python manage.py runserver
```

Vai su: **http://127.0.0.1:8000/**

---

## ✅ Configurazione Completa

Se tutto ha funzionato, ora hai:

✅ MySQL installato e funzionante  
✅ Database `refurbished_db` creato  
✅ Driver Python installato  
✅ Migrazioni applicate  
✅ SLA con nuovi campi (disponibilità, tipo intervento)  
✅ Dati di esempio  
✅ Sistema pronto all'uso  

---

## 🔍 Verificare che MySQL sia in Esecuzione

### Con XAMPP
- Apri XAMPP Control Panel
- Controlla che MySQL sia "Running" (verde)
- Se non è attivo, clicca "Start"

### Con Servizi Windows
1. Premi `Win + R`
2. Digita: `services.msc`
3. Cerca "MySQL" o "MySQL80"
4. Verifica che lo stato sia "In esecuzione"

---

## ⚠️ PROBLEMI COMUNI

### "Can't connect to MySQL server"
**Soluzione**: Avvia MySQL da XAMPP Control Panel

### "Access denied for user 'root'"
**Soluzione**: Con XAMPP la password è vuota:
```bash
$env:DB_PASSWORD=""
```

### "Unknown database 'refurbished_db'"
**Soluzione**: Crea il database con phpMyAdmin o MySQL command line

### "No module named 'MySQLdb'"
**Soluzione**: Installa pymysql:
```bash
pip install pymysql
```

---

## 📊 NUOVI SLA - Esempi

Il database viene popolato con 4 SLA:

### 1. Basic 8x5 - Solo Materiale
- Disponibilità: 8x5 (Lun-Ven, 8:00-18:00)
- Risposta: 8 ore
- Tipo: Solo invio materiale

### 2. Advanced 24x7 - Remoto
- Disponibilità: 24x7
- Risposta: 4 ore
- Tipo: Supporto remoto

### 3. Premium 24x7 - On-Site
- Disponibilità: 24x7
- Risposta: 2 ore
- Tipo: Intervento on-site

### 4. NBD On-Site+Remoto
- Disponibilità: Next Business Day
- Risposta: 24 ore
- Tipo: On-site + remoto

---

## 🎯 Pronto!

Hai completato la migrazione a MySQL con i nuovi campi SLA!

**Prossimi passi**:
1. Login: http://127.0.0.1:8000/
2. Vai all'Admin: http://127.0.0.1:8000/admin/
3. Esplora gli SLA creati
4. Crea Service Contract con i nuovi SLA

---

## 📝 Comandi Utili

```bash
# Vedere le tabelle nel database
python manage.py dbshell
SHOW TABLES;
EXIT;

# Test connessione
python test_mysql.py

# Backup database
mysqldump -u root refurbished_db > backup.sql

# Restore database
mysql -u root refurbished_db < backup.sql
```

---

**Tutto pronto! 🚀**

