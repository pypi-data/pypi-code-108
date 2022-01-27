import pandas as pd
from salgsanalyse.Salg_og_Semester import Salg
import os



def fil_til_salgdict(filename, sheet_name):
    df = pd.read_excel(filename, sheet_name=sheet_name)
    item_dict = {}
    for line in df['Beskrivelse']:
        try:
            for item in line.split(', '):
                if item[0].isnumeric():
                    if item not in item_dict:
                        item_dict[item[4:]] = 0
                    item_dict[item[4:]] += int(item[0])
                else:
                    if item not in item_dict:
                        item_dict[item] = 0
                    item_dict[item] += 1
        except AttributeError:
            pass

    return item_dict

def fil_til_salglist(filename, sheet_name):
    df = pd.read_excel(filename, sheet_name=sheet_name)
    salg_liste = []
    style = [107, 32, 60, 51]
    for dato, varer in zip(df['Dato'], df['Beskrivelse']):
        try:
            varer = varer.split(', ')
            for vare in varer:
                salg_liste.append(Salg(dato, vare))
        except AttributeError:
            pass

    return salg_liste, style

def merge_files(file1, sheet1, file2, sheet2, target_file, target_sheet):
    df1 = pd.read_excel(file1, sheet_name=sheet1)
    df2 = pd.read_excel(file2, sheet_name=sheet2)

    for col in df1.keys():
        try:
            df1[col].extend(df2[col])
        except KeyError:
            raise Exception('Kolonnen '+col+ ' finnes ikke i '+ file2 +' jeg vil ikke fucke opp, så jeg avbryter nå.')

    writer = pd.ExcelWriter(target_file)
    df1.to_excel(writer, target_sheet, index = False)
    writer.save()