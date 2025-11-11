-- Script SQL per creare il database Refurbished

-- Crea il database se non esiste
CREATE DATABASE IF NOT EXISTS refurbished_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Mostra i database esistenti
SHOW DATABASES;

-- Usa il database
USE refurbished_db;

-- Mostra le tabelle (sarà vuoto finché non esegui le migrazioni Django)
SHOW TABLES;

-- Informazioni sul database
SELECT
    SCHEMA_NAME as 'Database',
    DEFAULT_CHARACTER_SET_NAME as 'Charset',
    DEFAULT_COLLATION_NAME as 'Collation'
FROM information_schema.SCHEMATA
WHERE SCHEMA_NAME = 'refurbished_db';

