"""
Script per testare la connessione MySQL
"""
import os
import sys

print("="*60)
print("TEST CONNESSIONE MYSQL")
print("="*60)

# Test 1: Verifica driver
print("\n1. Verifica driver MySQL...")
try:
    import MySQLdb
    print("   ✅ mysqlclient installato")
    driver = "mysqlclient"
except ImportError:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
        print("   ✅ pymysql installato (usato come MySQLdb)")
        driver = "pymysql"
    except ImportError:
        print("   ❌ Nessun driver MySQL trovato!")
        print("   Installa con: pip install mysqlclient")
        print("   O su Windows: pip install pymysql")
        sys.exit(1)

# Test 2: Carica Django settings
print("\n2. Caricamento Django settings...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refurbished.settings')
try:
    import django
    django.setup()
    print("   ✅ Django caricato")
except Exception as e:
    print(f"   ❌ Errore Django: {e}")
    sys.exit(1)

# Test 3: Leggi configurazione
print("\n3. Configurazione database...")
from django.conf import settings
db_config = settings.DATABASES['default']
print(f"   Engine: {db_config['ENGINE']}")
print(f"   Nome DB: {db_config['NAME']}")
print(f"   User: {db_config['USER']}")
print(f"   Host: {db_config['HOST']}")
print(f"   Port: {db_config['PORT']}")
print(f"   Password: {'***' if db_config['PASSWORD'] else '(vuota)'}")

# Test 4: Test connessione
print("\n4. Test connessione al database...")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   ✅ Connessione riuscita!")
        print(f"   MySQL Version: {version[0]}")
except Exception as e:
    print(f"   ❌ Errore connessione: {e}")
    print("\n   SUGGERIMENTI:")
    print("   - Verifica che MySQL sia in esecuzione")
    print("   - Controlla username e password")
    print("   - Verifica che il database esista")
    print("   - Per creare il database:")
    print("     mysql -u root -p")
    print(f"     CREATE DATABASE {db_config['NAME']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    sys.exit(1)

# Test 5: Verifica tabelle
print("\n5. Verifica tabelle database...")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if tables:
            print(f"   ✅ Trovate {len(tables)} tabelle")
            print("   Tabelle esistenti:")
            for table in tables[:10]:  # Mostra prime 10
                print(f"     - {table[0]}")
            if len(tables) > 10:
                print(f"     ... e altre {len(tables) - 10} tabelle")
        else:
            print("   ⚠️  Nessuna tabella trovata")
            print("   Esegui: python manage.py migrate")
except Exception as e:
    print(f"   ⚠️  Impossibile elencare tabelle: {e}")

# Test 6: Verifica migrazioni
print("\n6. Verifica stato migrazioni...")
try:
    from django.db.migrations.executor import MigrationExecutor
    from django.db import connection

    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

    if plan:
        print(f"   ⚠️  Ci sono {len(plan)} migrazioni da applicare")
        print("   Esegui: python manage.py migrate")
    else:
        print("   ✅ Tutte le migrazioni sono applicate")
except Exception as e:
    print(f"   ⚠️  Verifica migrazioni fallita: {e}")

print("\n" + "="*60)
print("TEST COMPLETATO")
print("="*60)

# Riepilogo
print("\n✅ TUTTO OK! MySQL è configurato correttamente.")
print("\nPROSSIMI PASSI:")
print("1. Se non hai tabelle, esegui: python manage.py migrate")
print("2. Crea un superuser: python manage.py createsuperuser")
print("3. Popola il database: python populate_db.py")
print("4. Avvia il server: python manage.py runserver")

