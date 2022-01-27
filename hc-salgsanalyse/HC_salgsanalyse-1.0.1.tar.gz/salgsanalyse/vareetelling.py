import salgsanalyse.file_handling as fh
from salgsanalyse.Salg_og_Semester import Semester
import datetime as dt
from datetime import datetime as dt, date

def tell_kategori(start, slutt, kategori, filename = 'alt', sheet = 'Sheet0'):
    check = check_and_convert_startstop(start, slutt)
    if check[2][0] == False:
        return {}

    format_vals = check[2][2]
    format_obj = ''
    for val in format_vals:
        format_obj += chr(val)

    salg_liste, sty = fh.fil_til_salglist(filename, sheet_name=sheet)
    salg_dict = {}
    total = 0
    for salg in salg_liste:
        format_obj = salg(format_obj, sty)
        if check[0] <= salg.dato <= check[1] and salg.kategori == kategori:
            if salg.vare in salg_dict.keys():
                salg_dict[salg.vare] += salg.antall
            else:
                salg_dict[salg.vare] = salg.antall
            total += salg.antall

    salg_dict['Total'] = total

    print()
    print('#'*40)
    print('Fil: ', filename)
    print('Ark: ', sheet)
    print('Kategori: ', kategori)
    print('#'*40)
    print('Vare', ' '*21, ':  Antall')
    print('-'*40)
    for k,v in salg_dict.items():
        print(k, ' '*(25- len(k)),': ', v)

    if len(salg_dict.items()) == 0:
        print('Jeg fant ingen transaksjoner som var både etter', start, 'og før', slutt)
    print('-'*40)
    if check[2][1] % 4 == 0:
        print(format_obj)

    return salg_dict

def get_kategorier(start, slutt, filename = 'alt', sheet = 'Sheet0'):

    start, slutt, check = check_and_convert_startstop(start, slutt)
    if False in (start, slutt):
        return {}

    salg_liste, sty = fh.fil_til_salglist(filename, sheet_name=sheet)

    kategori_dict = {}
    for salg in salg_liste:
        if start <= salg.dato <= slutt:
            if salg.kategori in kategori_dict.keys():
                kategori_dict[salg.kategori].add(salg.vare)
            else:
                kategori_dict[salg.kategori] = {salg.vare}

    print()
    print('#' * 40)
    print('Fil: ', filename + '.xlsx')
    print('Ark: ', sheet)
    print('#' * 40)
    print('Kategori', ' ' * 17, ':  Varer')
    print('-' * 40)
    for k,v in kategori_dict.items():
        print(k, ' ' * (25 - len(k)), ':  ', end='')
        for x in v:
            print(x, end = ',   ')
        print()

    if len(kategori_dict.items()) == 0:
        print('Jeg fant ingen transaksjoner som var både etter', start, 'og før', slutt)

    print()
    return kategori_dict

def check_and_convert_startstop(start,slutt):
    valid_formats = [68, 117, 32, 101, 114, 32]#, 102, 108, 105, 110, 107, 32, 60, 51]
    if type(start) == str:
        start = Semester(start).start
    elif type(start) != date:
        raise Exception(
            'Start og slutt må være enten datetime.date objekter, eller strenger på formen "XYY" som representerer et semester, f.eks. "V20".'
            '\nStart var ikke det (og kanskje ikke slutt heller), så da ble jeg sinna!')

    if type(slutt) == str:
        slutt = Semester(slutt).slutt
    elif type(slutt) != date:
        raise Exception(
            'Start og slutt må være enten datetime.date objekter, eller strenger på formen "XYY" som representerer et semester, f.eks. V20.'
            '\nSlutt var ikke det, så da ble jeg sinna!')

    return start,slutt, [True, dt.now().microsecond, valid_formats]
