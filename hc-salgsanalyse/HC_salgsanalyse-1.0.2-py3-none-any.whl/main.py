import salgsanalyse.vareetelling as vt
import os
import pandas as pd

#Skriver ut alle kategorier med tilhørende varer som er solgt i det gitte tidsrommet
#Fra start av første semesteret, til slutt av det andre semesteret
#gi samme semester i begge for å bare telle ett semester

#'start' og 'slutt' kan enten være semester på formen "XYY" eller datetime.date objekter, syntaks er:
#kat_dict = vt.get_kategorier('start','slutt',filename = 'min_fil', sheet = 'sheet0')

#returnerer en dict med "set" <- (google it), på formen
# kat_dict['kategori_A'] = {'vare_A1', 'vare_A2', vare_A3', ...}
# kat_dict['kategori_B'] = {'vare_B1', 'vare_B2', vare_B3', ...}

#kat_dict = vt.get_kategorier('H15', 'V20')

#Skriver ut antall solgt av hver vare i kategorien og total for kategorien i den gitte perioden
#Fra start av første semesteret, til slutt av det andre semesteret
#gi samme semester i begge for å bare telle ett semester

#'start' og 'slutt' kan enten være semester på formen "XYY" eller datetime.date objekter, syntaks er:
#salg_dict = vt.tell_kategorier('start','slutt',filename = 'min_fil', sheet = 'sheet0')

#Returnerer en dict på formen
#salg_dict['vare'] = int(antall)
#salg_dict['total'] = int(antall)

#salg_dict = vt.tell_kategori('H15', 'V19', 'Blådress')
#salg_dict = vt.tell_kategori('H15', 'V19', 'Blådresse')

def hent_kategorier(fil, sheet):
    print('Hent kategorier')
    start = input('Fra semester: ')
    if check_valid_semester(start):
        slutt = input('Til semester: ')
        if check_valid_semester(slutt):
            vt.get_kategorier(start, slutt, filename=fil, sheet=sheet)
    else:
        return None

def tell_kategori(fil, sheet):
    kategorier = input('Kategorier, adskilt med ", ": ')
    start = input('Fra semester: ')
    if check_valid_semester(start):
        slutt = input('Til semester: ')
        if check_valid_semester(slutt):
            for kat in kategorier.split(", "):
                vt.tell_kategori(start, slutt, kat, filename=fil, sheet=sheet)
    else:
        return None

def check_valid_semester(sem):
    if len(sem) != 3:
        print('\nSemester må skrives på formen "XYY" hvor X er V eller H og YY er året. F.eks. sem = Semester("V20")\n'
              'du ga meg "' + sem + '" og da blir jeg sinna\n')
        return False
    if sem[0] not in ['V', 'H']:
        print('\nSemester må skrives på formen "XYY" hvor X er V eller H og YY er året. F.eks. sem = Semester("V20")\n'
                'du ga meg "'+sem+'" og da blir jeg sinna\n')
        return False

    aar = sem[1:]
    try:
        aar = int(aar)
    except:
        print('\nSemester må skrives på formen "XYY" hvor X er V eller H og YY er året. F.eks. sem = Semester("V20")\n'
                                '"YY" skal være et tall mellom 0 og 99, året skal altså være 20YY. Nå blir det: '+ str(2000+aar)+'\n')
        return False

    if aar < 0 or aar > 100:
        print('\nSemester må skrives på formen "XYY" hvor X er V eller H og YY er året. F.eks. sem = Semester("V20")\n'
              '"YY" skal være et tall mellom 0 og 99, året skal altså være 20YY. Nå blir det: ' + str(2000 + aar) + '\n')
        return False

    return True

def velg_dokument(default_file, default_sheet):
    print('#' * 50)
    print('Programmet tar bare imot excel-formaterte filer. Skriv filnavn med ending.')
    print('Tilgjengelige filer er:', [f for f in os.listdir(os.getcwd()) if '.xlsx' in f])
    filnavn = input('Filnavn: ')
    while not os.path.exists(os.getcwd() + '/' + filnavn) and filnavn != '':
        print('\nDet dokumentet fant jeg ikke!'
              '\nPrøv igjen eller trykk enter uten å skrive noe for å sette fil og ark til default.\n')
        filnavn = input('Filnavn: ')

    if filnavn == '':
        fil = default_file
        file_handler = pd.ExcelFile(default_file)
        sheet = default_sheet

    else:
        fil = filnavn
        file_handler = pd.ExcelFile(fil)
        sheet = file_handler.sheet_names[0]

    print('Aktivt dokument er:', os.getcwd() + '/' + fil)
    print('Dokumentet har arkene:', file_handler.sheet_names)
    print('Aktivt ark er:', sheet)
    return fil, sheet

def velg_ark(fil, sheet, default_file, default_sheet):
    file_handler = pd.ExcelFile(fil)
    print('Dette er navnet på arket i excel-filen du bruker, du har nå arket: ', sheet,
          '\n Tilgjengelige ark er:', file_handler.sheet_names)
    sheet = input('Arknavn: ')

    while sheet not in file_handler.sheet_names and sheet != '':
        print(sheet, 'er ikke et ark i', fil, 'Tilgjengelige ark er: ', file_handler.sheet_names,
              '\n Jeg lar deg prøve igjen, trykk enter uten å skrive noe for å sette ark og filnavn til default.')
        sheet = input('Arknavn: ')

    if sheet == '':
        sheet = default_sheet
        fil = default_file

    return fil, sheet

def loop(default_file, default_sheet='Sheet0'):
    if default_file not in [f for f in os.listdir(os.getcwd()) if '.xlsx' in f]:
        print('Jeg fant ikke det dokumentet!')
        default_file, default_sheet = velg_dokument(default_file, default_sheet)

    if default_sheet not in pd.ExcelFile(default_file).sheet_names:
        print('Jeg fant ikke det arket!')
        default_file, default_sheet = velg_ark(default_file, default_sheet, default_file, default_sheet)
    fil = default_file
    sheet = default_sheet
    valg = 0
    while valg != 'nei':
        print()
        print('#'*50)
        print('Aktivt dokument er:', fil,' Aktivt ark er:', sheet)
        print()
        print('Velg et alternativ ved å skrive tallet til alternativet, skriv "nei" for å avslutte.')
        print('1) Hent kategorier')
        print('2) Tell kategori')
        print('3) Angi fil')
        print('4) Angi ark')
        print('5) Hjelp!')
        valg = input('Valg: ')

        print()

        if valg == '1':
            hent_kategorier(fil, sheet)
        elif valg == '2':
            tell_kategori(fil, sheet)
        elif valg == '3':
            fil, sheet = velg_dokument(default_file, default_sheet)
        elif valg == '4':
            fil, sheet = velg_ark(fil, sheet, default_file, default_sheet)

        elif valg == '5':
            print('Working directory er:', os.getcwd())
            print('Tilgjengelige filer er:', [f for f in os.listdir(os.getcwd()) if '.xlsx' in f])
            print('Aktiv fil er:', fil)
            print('Aktivt ark er:', sheet)
            print()
            print('Du kan analysere Excel-filer ved å legge dem i mappen', os.getcwd())
            print('For å kjøre programmet, bruk funksjonen salgsanalyse.analyser(<min_fil.xlsx>, default_sheet=<mitt_ark>). Argumentet "default_sheet" har default-verdi "Sheet0".')
            print('Programmet er skrevet for å bruker Excel-filer som outputtes fra iZettle. Bruk "Hent kategorier" alternativet for å se hvilke varekategorier som finnes i en tidsperiode. Semester angis på formen XYY, f.eks. V18 eller H20.')
            print('Deretter kan du bruke "Tell kategori" alternativet for å se hvor mye som ble solgt av de forskjellige varene i en kategori innenfor en bestemt tidsramme.')
            print()
            print('NB: Det er et lite "easter-egg" gjemt i programmet, hvis du kan si meg hvordan det funker får du en øl eller to :)')

        if valg != 'nei':
            valg = input("Trykk enter for å fortsette, skriv 'nei' for å avslutte: ")