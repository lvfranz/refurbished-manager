"""Test rapido parsing cliente - sede"""
cliente_nome = "EMPSOL - DC"

if ' - ' in cliente_nome:
    parts = cliente_nome.split(' - ', 1)
    cliente_nome_solo = parts[0].strip()
    nome_sede_specifica = parts[1].strip()
    print(f"✅ Parsing OK:")
    print(f"   Input: '{cliente_nome}'")
    print(f"   Cliente: '{cliente_nome_solo}'")
    print(f"   Sede: '{nome_sede_specifica}'")
else:
    print(f"❌ Separatore ' - ' non trovato in '{cliente_nome}'")

# Test altri casi
test_cases = [
    "EMPSOL - DC",
    "EMPSOL - Milano",
    "EMPSOL",
    "EMPSOL-Europe",
    "Acme Corporation"
]

print("\nTest tutti i casi:")
for test in test_cases:
    if ' - ' in test:
        parts = test.split(' - ', 1)
        print(f"'{test}' → Cliente: '{parts[0].strip()}' | Sede: '{parts[1].strip()}'")
    else:
        print(f"'{test}' → Cliente: '{test}' | Sede: default")

