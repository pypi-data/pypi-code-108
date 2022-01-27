import sys
import os
from salgsanalyse.main import loop

if len(sys.argv) == 2:
    loop(sys.argv[1])
elif len(sys.argv) == 3:
    loop(sys.argv[1], default_sheet=sys.argv[2])
else:
    print('Bruk', 'python -m salgsanalyse <filnavn.xlsx>', 'eller', 'python -m salgsanalyse <filnavn.xlsx> <arknavn>', 'for å kjøre programmet.', sep='\n')
    print('Les readme-filen for mer hjelp')
    print('Tilgjengelige filer er', [f for f in os.listdir(os.getcwd()) if '.xlsx' in f])
    print('Du er nå i mappen', os.getcwd())
