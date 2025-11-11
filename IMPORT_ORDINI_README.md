# 📦 Import Ordini da CSV - Guida

## 📋 Formato CSV

Il file CSV deve avere **10 campi** per riga (senza intestazione):

```
data,numero_ordine,fornitore,part_number,descrizione,sn,cliente,mesi_garanzia,quantita,note
```

### Dettaglio Campi

| # | Campo | Descrizione | Esempio | Obbligatorio |
|---|-------|-------------|---------|--------------|
| 1 | **data** | Data ordine (YYYY-MM-DD o DD/MM/YYYY) | `2024-01-15` | ✅ Sì |
| 2 | **numero_ordine** | Numero ordine univoco | `ORD-001` | ✅ Sì |
| 3 | **fornitore** | Nome fornitore (deve esistere) | `Dell` | ✅ Sì |
| 4 | **part_number** | Codice articolo (deve esistere) | `ABC123` | ✅ Sì |
| 5 | **descrizione** | Descrizione articolo (non usata) | `Server Dell` | ❌ No |
| 6 | **sn** | Numero seriale (univoco, `-` se assente) | `SN12345` o `-` | ❌ No |
| 7 | **cliente** | Nome cliente (deve esistere)<br>**Formato speciale**: `CLIENTE - SEDE` (es: `EMPSOL - DC`) | `Acme Corp` o `EMPSOL - DC` | ✅ Sì |
| 8 | **mesi_garanzia** | Mesi di garanzia | `36` | ❌ No (default: 12) |
| 9 | **quantita** | Quantità (deve essere 1 se c'è seriale) | `2` | ❌ No (default: 1) |
| 10 | **note** | Note ordine/articolo | `Note libere` | ❌ No |

---

## 🎯 Formato Speciale: Cliente + Sede

Il campo **cliente** supporta un **formato speciale** per specificare cliente e sede insieme:

### Formato: `CLIENTE - SEDE`

**Esempio**: `EMPSOL - DC`
- **Cliente**: EMPSOL (viene cercato nel database)
- **Sede**: DC (viene cercata tra le sedi del cliente)

⚠️ **IMPORTANTE**: Usa il **trattino con spazi** ` - ` come separatore

### Come Funziona

Lo script analizza il campo cliente:
1. **Cerca** il separatore ` - ` (trattino con spazi)
2. **Divide** il nome: prima parte = Cliente, seconda parte = Sede
3. **Cerca** il cliente con la prima parte (`EMPSOL`)
4. **Cerca** la sede specifica con la seconda parte (`DC`)
5. Se la sede non viene trovata → **errore** (riga saltata)

### Esempi

```csv
# Sede specifica (con trattino)
2024-01-15,ORD-001,Dell,ABC123,Desc,SN001,EMPSOL - DC,36,1,Note

# Sede principale (senza trattino, usa default)
2024-01-15,ORD-002,Dell,ABC123,Desc,SN002,EMPSOL,36,1,Note

# Cliente con nome composto (senza trattino separatore)
2024-01-15,ORD-003,Dell,ABC123,Desc,SN003,Acme Corporation,36,1,Note

# Cliente con trattino nel nome (nessun problema)
2024-01-15,ORD-004,Dell,ABC123,Desc,SN004,EMPSOL-Europe,36,1,Note
```

### Ricerca Sede

Lo script cerca la sede in questo ordine:
1. **Match esatto** (case-insensitive): `nome_sede = 'DC'`
2. **Ricerca parziale**: `nome_sede LIKE '%DC%'`
3. Se non trovata → **errore**

### Fallback

Se il cliente non viene trovato con la prima parte, lo script prova anche con il nome completo come fallback.

---

## ⚠️ PREREQUISITI IMPORTANTI

Prima di importare, assicurati che esistano nel database:

### 1. ✅ Clienti
```python
# Admin → Clienti → Verifica che esistano
# Ogni cliente DEVE avere almeno una sede
```

### 2. ✅ Fornitori
```python
# Admin → Fornitori → Verifica che esistano
# Nome deve corrispondere esattamente (case-insensitive)
```

### 3. ✅ Articoli
```python
# Admin → Articoli → Verifica che esistano
# Codice articolo deve corrispondere (viene convertito in UPPERCASE)
```

---

## 🚀 Come Usare lo Script

### 🔍 MODALITÀ DRY-RUN (Consigliata per Test)

**Prima di importare, usa sempre la modalità dry-run per verificare!**

```cmd
# Vai nella cartella del progetto
cd C:\Users\francesco.lavatelli\PycharmProjects\Refurbished

# Attiva l'ambiente virtuale
.venv\Scripts\activate

# SIMULA l'import senza modificare il database
python import_ordini.py ordini_esempio.csv --dry-run
```

La modalità `--dry-run`:
- ✅ **Valida** tutti i dati
- ✅ **Mostra** cosa verrebbe importato
- ✅ **Segnala** eventuali errori
- ❌ **NON salva** nulla nel database
- 💡 **Consigliata** prima di ogni import reale

### Metodo 1: Da Riga di Comando (Import Reale)

```cmd
# Vai nella cartella del progetto
cd C:\Users\francesco.lavatelli\PycharmProjects\Refurbished

# Attiva l'ambiente virtuale
.venv\Scripts\activate

# Esegui lo script (SALVA nel database)
python import_ordini.py ordini_esempio.csv
```

### Metodo 2: Da Python Shell

```python
# Vai nella cartella del progetto
cd C:\Users\francesco.lavatelli\PycharmProjects\Refurbished

# Attiva l'ambiente virtuale
.venv\Scripts\activate

# Apri shell Python
python

# Esegui lo script
exec(open('import_ordini.py').read())
import_ordini_csv('ordini_esempio.csv')
```

---

## 📊 Output dello Script

### Output Modalità DRY-RUN (Simulazione)

```
🔍 MODALITÀ DRY-RUN: Simulazione import senza salvare nel database

📥 Inizio importazione da: ordini_esempio.csv

  ✅ [DRY-RUN] Creerebbe ordine: ORD-TEST-001 - Dell (2024-01-15)
    ➕ [DRY-RUN] Aggiungerebbe articolo: ABC123 (SN: SN-001-TEST) x1
       Cliente: Acme Corp - Sede Principale
       Garanzia: 36 mesi (scadenza: 2027-01-15)
  ↪ [DRY-RUN] Aggiungerebbe articolo a ordine: ORD-TEST-001
    ➕ [DRY-RUN] Aggiungerebbe articolo: DEF456 (SN: SN-002-TEST) x1
       Cliente: Acme Corp - Sede Principale
       Garanzia: 36 mesi (scadenza: 2027-01-15)

================================================================================
📊 REPORT SIMULAZIONE (DRY-RUN - Nessuna modifica al database)
================================================================================
✅ Ordini che verrebbero creati: 2
🔄 Ordini che verrebbero aggiornati: 0
➕ Articoli che verrebbero importati: 3
❌ Righe saltate: 1

⚠️ RIGHE NON IMPORTATE
📍 Riga 4:
   ❌ Errore: Cliente 'Test Cliente' non trovato

================================================================================
✅ SIMULAZIONE COMPLETATA - Nessuna modifica salvata

💡 Tutto OK! Puoi procedere con l'import reale rimuovendo --dry-run
================================================================================
```

### Output Import Reale

```
📥 Inizio importazione da: ordini_esempio.csv

  ✅ Ordine creato: ORD-TEST-001 - Dell (2024-01-15)
    ➕ Articolo: ABC123 (SN: SN-001-TEST) x1
  ↪ Aggiungo articolo a ordine esistente: ORD-TEST-001
    ➕ Articolo: DEF456 (SN: SN-002-TEST) x1

================================================================================
📊 REPORT IMPORTAZIONE
================================================================================
✅ Ordini creati: 2
🔄 Ordini aggiornati (articoli aggiunti): 0
➕ Articoli importati: 3
❌ Righe saltate: 1


================================================================================
✅ IMPORTAZIONE COMPLETATA
================================================================================
```

---

## ⚠️ Validazioni Eseguite

Lo script valida automaticamente:

1. ✅ **Data** - Formato valido (YYYY-MM-DD, DD/MM/YYYY, ecc.)
2. ✅ **Numero Ordine** - Non vuoto
3. ✅ **Fornitore** - Esiste nel database
4. ✅ **Articolo** - Codice esiste nel database
5. ✅ **Cliente** - Esiste nel database
6. ✅ **Sede Cliente** - Cliente ha almeno una sede
7. ✅ **Seriale Univoco** - Non duplicato nel database
8. ✅ **Quantità con Seriale** - Se c'è seriale, quantità = 1
9. ✅ **Mesi Garanzia** - Numero valido >= 0
10. ✅ **Quantità** - Numero valido >= 1

---

## 📝 Esempi CSV

### Esempio 1: Ordine Singolo con Seriale
```csv
2024-01-15,ORD-001,Dell,ABC123,Server Dell R640,SN12345,Acme Corp,36,1,Ordine test
```

### Esempio 2: Ordine con Più Articoli
```csv
2024-01-15,ORD-001,Dell,ABC123,Switch Cisco,SN001,Acme Corp,36,1,Articolo 1
2024-01-15,ORD-001,Dell,DEF456,Server Dell,SN002,Acme Corp,36,1,Articolo 2
2024-01-15,ORD-001,Dell,GHI789,Storage EMC,,Acme Corp,24,2,Senza seriale
```

### Esempio 3: Senza Seriale
```csv
2024-01-20,ORD-002,HP,JKL012,Hard Disk 2TB,-,Cliente XYZ,12,5,Lotto dischi
```

---

## 🔧 Comportamento dello Script

### Ordini Duplicati
- Se un ordine con lo stesso `numero_ordine` esiste già:
  - ✅ Gli articoli vengono **aggiunti** all'ordine esistente
  - 🔄 Ordine conteggiato come "aggiornato"

### Seriali Duplicati
- Se un seriale esiste già nel database:
  - ❌ La riga viene **saltata**
  - 📝 Errore riportato nel report finale

### Clienti/Fornitori/Articoli Mancanti
- Se un'entità non esiste:
  - ❌ La riga viene **saltata**
  - 📝 Errore riportato con dettagli

---

## 🎯 Consigli

1. **Workflow Consigliato (IMPORTANTE!)**
   - ✅ **Step 1**: Esegui `--dry-run` per verificare
   - ✅ **Step 2**: Correggi gli errori nel CSV
   - ✅ **Step 3**: Riesegui `--dry-run` finché tutto OK
   - ✅ **Step 4**: Esegui import reale (senza --dry-run)

2. **Prepara il Database Prima**
   - Importa prima i clienti
   - Importa i fornitori
   - Importa gli articoli (puoi usare `import_articoli_csv` dall'admin)

3. **Test con File Piccolo**
   - Prova prima con 5-10 righe
   - Verifica il report
   - Se OK, procedi con file completo

4. **Backup del Database**
   - Fai backup prima di import grandi
   - Gli ordini sono in transazione (rollback automatico se errore)

5. **Encoding UTF-8**
   - Salva il CSV in UTF-8
   - Evita caratteri speciali problematici

---

## ❓ Risoluzione Problemi

### Errore: "Cliente 'XXX' non trovato"
**Soluzione**: Crea il cliente nell'admin prima dell'import

### Errore: "Articolo 'XXX' non trovato"
**Soluzione**: Importa gli articoli prima (admin → Articoli → Import CSV)

### Errore: "Seriale 'XXX' già esistente"
**Soluzione**: Verifica i seriali duplicati nel CSV o nel database

### Errore: "Con seriale la quantità deve essere 1"
**Soluzione**: Imposta quantità = 1 quando hai un seriale

### Errore: "Data non valida"
**Soluzione**: Usa formato YYYY-MM-DD o DD/MM/YYYY

---

## 📞 Supporto

Per problemi o domande:
1. Controlla il report degli errori
2. Verifica i prerequisiti (clienti, fornitori, articoli)
3. Prova con file di esempio `ordini_esempio.csv`

