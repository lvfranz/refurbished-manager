from django import forms
import csv
import io


class ImportArticoliCSVForm(forms.Form):
    """Form per importare articoli da file CSV"""
    csv_file = forms.FileField(
        label='File CSV',
        help_text='Formato: codice,descrizione (senza intestazione). Es: abc123,Cisco Switch 2960'
    )
    sovrascrivi = forms.BooleanField(
        required=False,
        initial=False,
        label='Sovrascrivi articoli esistenti',
        help_text='Se attivo, gli articoli con codice già esistente verranno aggiornati invece di essere saltati'
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']

        # Verifica che sia un file CSV
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('Il file deve essere in formato CSV')

        # Verifica dimensione (max 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Il file è troppo grande. Dimensione massima: 5MB')

        return csv_file

    def process_csv(self):
        """Processa il file CSV e ritorna lista di articoli da creare"""
        csv_file = self.cleaned_data['csv_file']

        # Leggi il contenuto del file
        file_data = csv_file.read().decode('utf-8')
        csv_reader = csv.reader(io.StringIO(file_data))

        articoli_to_create = []
        errors = []
        line_number = 0

        for row in csv_reader:
            line_number += 1

            # Salta righe vuote
            if not row or len(row) < 2:
                continue

            codice = row[0].strip().upper()  # Codice in UPPERCASE
            descrizione = row[1].strip()

            if not codice or not descrizione:
                errors.append(f"Riga {line_number}: codice o descrizione vuoti")
                continue

            # Applica regole di mappatura automatica
            costruttore = ''
            categoria = ''

            descrizione_upper = descrizione.upper()

            # Regola: Cisco → brand cisco, categoria switch
            if 'CISCO' in descrizione_upper:
                costruttore = 'Cisco'
                categoria = 'Switch'

            # Regola: SFP → brand cisco, categoria sfp
            if 'SFP' in descrizione_upper:
                costruttore = 'Cisco'
                categoria = 'SFP'

            # Regola: Del → brand dell, categoria server
            if 'DEL' in descrizione_upper:
                costruttore = 'Dell'
                categoria = 'Server'

            # Regola: HP → brand hp, categoria server
            if 'HP' in descrizione_upper or 'HEWLETT' in descrizione_upper:
                costruttore = 'HP'
                categoria = 'Server'

            # Regola: EMC, VNX, Unity → emc, categoria storage
            if any(keyword in descrizione_upper for keyword in ['EMC', 'VNX', 'UNITY']):
                costruttore = 'EMC'
                categoria = 'Storage'

            # Regola: DISK → categoria Hard Disk
            if 'DISK' in descrizione_upper:
                categoria = 'Hard Disk'

            articoli_to_create.append({
                'codice_articolo': codice,
                'descrizione': descrizione,
                'costruttore': costruttore,
                'categoria': categoria,
                'line_number': line_number
            })

        return articoli_to_create, errors

