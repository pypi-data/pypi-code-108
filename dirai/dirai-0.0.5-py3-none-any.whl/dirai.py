import pymysql
import pandas as pd
import sys
from statistics import stdev

global connection

def dirai_connect(servidor, usuario, senha, base):

    global connection

    connection = pymysql.Connect(host=servidor,
            user=usuario,
            password=senha,
            db=base,
            charset='utf8mb4',
            autocommit=True)

def dados_hist_fundos(dataini, datafim, cnpj, campos, output):

    '''
    outputs = 'dataframe', 'dict'
    exemplo = dados_hist_fundos('2017-01-02', '2017-01-20', '11290670000106', ['dtposicao', 'patliq', 'valorcota'], 'dict')
    '''

    global connection
    dictbase = {}
    for a in campos:
        dictbase[a] = []
    
    consulta_campos = ''
    for a in range(0, (len(campos)-1)):
        consulta_campos += f'{campos[a]}, '
    consulta_campos += f'{campos[-1]}'

    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = f'SELECT {consulta_campos} FROM backoffice_xml.header WHERE (cnpj = "{cnpj}") and (dtposicao between "{dataini}" and "{datafim}") order by dtposicao ASC;'
        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        for a in range(0, len(result)):
            for b in dictbase:
                dictbase[b].append(result[a][b])
    if output == 'dict':
        return dictbase
    elif output == 'dataframe':
        dfbase = pd.DataFrame()
        for a in dictbase:
            dfbase[a] = dictbase[a]
        return dfbase

def lamina(dataref, cnpj, caminhoexportar, bench):

    meses_n = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    meses_r = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    meses_p = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

    ano = dataref[0:4]
    mes = dataref[5:7]

    def cota(cnpj2, data):
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            if len(data) == 10:
                sql = f'SELECT valorcota FROM backoffice_xml.header WHERE (cnpj = "{cnpj2}") and (dtposicao = "{data}") order by dtposicao DESC limit 1;'
            else:
                sql = f'SELECT valorcota FROM backoffice_xml.header WHERE (cnpj = "{cnpj2}") and (dtposicao like "{data}-%%") order by dtposicao DESC limit 1;'
            #print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            return float(result[0]['valorcota'])
    def bench_cota(data):
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            if len(data) == 10:
                sql = f'SELECT indice_cetip FROM backoffice.di_cetip WHERE (data_cetip = "{data}") order by data_cetip DESC limit 1;'
            else:
                sql = f'SELECT indice_cetip FROM backoffice.di_cetip WHERE (data_cetip like "{data}-%%") order by data_cetip DESC limit 1;'
            #print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            return float(result[0]['indice_cetip'])
    def data_cota_ini(cnpj2):
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = f'SELECT dtposicao FROM backoffice_xml.header WHERE (cnpj = "{cnpj2}") order by dtposicao ASC limit 1;'
            #print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            return str(result[0]['dtposicao'])
    def vol_ini(cnpj2):
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = f'SELECT valorcota FROM backoffice_xml.header WHERE (cnpj = "{cnpj2}") order by dtposicao ASC;'
            #print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            ret_cotas = []
            for a in range(1, len(result)):
                ret_cotas.append(result[a]['valorcota']/result[a-1]['valorcota']-1)
        return f"{round(float(stdev(ret_cotas)) * (252 ** (1/2)) * 100, 2)}%"
    def vol_12m(cnpj2, data3):
        data4 = f'{int(data3[:4])-1}-{data3[4:]}'
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = f'SELECT valorcota FROM backoffice_xml.header WHERE (cnpj = "{cnpj2}") and (dtposicao between "{data4}" and "{data3}") order by dtposicao ASC;'
            #print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            ret_cotas = []
            for a in range(1, len(result)):
                ret_cotas.append(result[a]['valorcota']/result[a-1]['valorcota']-1)
        return f"{round(float(stdev(ret_cotas)) * (252 ** (1/2)) * 100, 2)}%"


    dictlamina = {}
    for a in range(0, len(meses_n)):
        #print(meses_p[a])
        if len(str(meses_n[a])) == 1:
            mesref1 = f'0{meses_n[a]}'
        else:
            mesref1 = meses_n[a]

        if len(str(meses_r[a])) == 1:
            mesref2 = f'0{meses_r[a]}'
        else:
            mesref2 = meses_r[a]

        if a == 0:
            dictlamina[meses_p[a]] = round( (cota(cnpj, f'{int(ano)}-{mesref1}') / cota(cnpj, f'{int(ano)-1}-{mesref2}') - 1) * 100, 2)
            if dictlamina[meses_p[a]] < 0:
                dictlamina[f'{meses_p[a]}_dif'] = '-'
            else:
                if bench == 'cdi':
                    dictlamina[f'{meses_p[a]}_dif'] = f"{round((dictlamina[meses_p[a]] / (round( (bench_cota(f'{int(ano)}-{mesref1}') / bench_cota(f'{int(ano)-1}-{mesref2}') - 1) * 100, 2))) * 100, 2)}%"
                else:
                    dictlamina[f'{meses_p[a]}_dif'] = f"{round((dictlamina[meses_p[a]] - (round( (bench_cota(f'{int(ano)}-{mesref1}') / bench_cota(f'{int(ano)-1}-{mesref2}') - 1) * 100, 2))) * 100, 2)}%"

        else:
            dictlamina[meses_p[a]] = round( (cota(cnpj, f'{int(ano)}-{mesref1}') / cota(cnpj, f'{int(ano)}-{mesref2}') - 1) * 100, 2)
            if dictlamina[meses_p[a]] < 0:
                dictlamina[f'{meses_p[a]}_dif'] = '-'
            else:
                if bench == 'cdi':
                    dictlamina[f'{meses_p[a]}_dif'] = f"{round((dictlamina[meses_p[a]] / (round( (bench_cota(f'{int(ano)}-{mesref1}') / bench_cota(f'{int(ano)}-{mesref2}') - 1) * 100, 2))) * 100, 2)}%"
                else:
                    dictlamina[f'{meses_p[a]}_dif'] = f"{round((dictlamina[meses_p[a]] - (round( (bench_cota(f'{int(ano)}-{mesref1}') / bench_cota(f'{int(ano)}-{mesref2}') - 1) * 100, 2))) * 100, 2)}%"

    # Ano #
    dictlamina['ano'] = round( (cota(cnpj, f'{int(ano)}-{mes}') / cota(cnpj, f'{int(ano)-1}-12') - 1) * 100, 2)
    if dictlamina['ano'] < 0:
        dictlamina[f'ano_dif'] = '-'
    else:
        if bench == 'cdi':
            dictlamina[f'ano_dif'] = f"{round((dictlamina[meses_p[a]] / (round( (bench_cota(f'{int(ano)}-{mes}') / bench_cota(f'{int(ano)-1}-12') - 1) * 100, 2))) * 100, 2)}%"
        else:
            dictlamina[f'ano_dif'] = f"{round((dictlamina[meses_p[a]] - (round( (bench_cota(f'{int(ano)}-{mes}') / bench_cota(f'{int(ano)-1}-12') - 1) * 100, 2))) * 100, 2)}%"


    # Janelas #
    janelas = [1, 3, 6, 12, 24, 36]
    for a in janelas:
        #print(a)
        if a in [1, 3, 6]:
            if int(mes) < (a+1):
                anoref_mes = int(ano) - 1
                mesref_mes = 12 + (int(mes) - a)
            else:
                anoref_mes = int(ano)
                mesref_mes = int(mes) - a
        else:
            anoref_mes = int(ano) - (a/12)
            mesref_mes = mes

        if len(str(mesref_mes)) == 1:
            mesref_mes = f'0{mesref_mes}'
        
        dictlamina[f'{a}mes'] = f"{round( (cota(cnpj, f'{int(ano)}-{mes}') / cota(cnpj, f'{int(anoref_mes)}-{mesref_mes}') - 1) * 100, 2)}%"
        dictlamina[f'{a}mes_ind'] = f"{round( (bench_cota(f'{int(ano)}-{mes}') / bench_cota(f'{int(anoref_mes)}-{mesref_mes}') - 1) * 100, 2)}%"
        baseapoio1 = dictlamina[f'{a}mes']
        if float(baseapoio1.replace('%', '').replace(',', '.')) < 0:
            dictlamina[f'{a}mes_dif'] = '-'
        else:
            if bench == 'cdi':
                base_apoio = float(dictlamina[f'{a}mes'].replace('%', '').replace(',', '.')) / float(dictlamina[f'{a}mes_ind'].replace('%', '').replace(',', '.'))
            else:
                base_apoio = float(dictlamina[f'{a}mes'].replace('%', '').replace(',', '.')) - float(dictlamina[f'{a}mes_ind'].replace('%', '').replace(',', '.'))
            dictlamina[f'{a}mes_dif'] = f"{str(round(base_apoio * 100, 2)).replace('.',',')}%"
    
    # Inicio #
    data_cotaini = data_cota_ini(cnpj)
    dictlamina['comp'] = f"{round( (cota(cnpj, dataref) / cota(cnpj, data_cotaini) - 1) * 100, 2)}%"
    dictlamina['comp_ind'] = f"{round( (bench_cota(dataref) / bench_cota(data_cotaini) - 1) * 100, 2)}%"
    if bench == 'cdi':
        base_apoio = float(dictlamina[f'{a}mes'].replace('%', '').replace(',', '.')) / float(dictlamina[f'{a}mes_ind'].replace('%', '').replace(',', '.'))
    else:
        base_apoio = float(dictlamina[f'{a}mes'].replace('%', '').replace(',', '.')) - float(dictlamina[f'{a}mes_ind'].replace('%', '').replace(',', '.'))
    dictlamina['comp_diff'] = f"{str(round(base_apoio * 100, 2)).replace('.',',')}%"

    # Vol desde inicio #
    dictlamina['VI'] = vol_ini(cnpj)

    # Vol 12m #
    dictlamina['VM'] = vol_12m(cnpj, dataref)

    # Sharpe #
    cota12m = float(dictlamina[f'12mes'].replace("%", "").replace(",", ".")) / 100
    cdi12m = float(dictlamina[f'12mes_ind'].replace("%", "").replace(",", ".")) / 100
    vol12m =float(dictlamina['VM'].replace("%", "").replace(",", "."))
    dictlamina['sharpe'] = (cota12m - cdi12m) / vol12m
    
    ### PL ATUAL e MEDIO ###
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = f'SELECT patliq FROM backoffice_xml.header WHERE (cnpj = "{cnpj}") and (dtposicao = "{dataref}") order by dtposicao DESC limit 1;'
        #print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        dictlamina[f'PLA'] = (f"R$ {round(float(result[0]['patliq']), 2):,.2f}").replace(",", "_").replace(".", ",").replace("_", ".")
        #print(dictlamina[f'PLA'])

    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = f'SELECT sum(patliq), count(patliq) FROM backoffice_xml.header WHERE (cnpj = "{cnpj}") and (dtposicao between "{int(dataref[0:4]) - 1}{dataref[4:]}" and "{dataref}") order by dtposicao DESC;'
        #print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        dictlamina[f'PLM'] = (f"R$ {round(float(result[0]['sum(patliq)']) / float(result[0]['count(patliq)']), 2):,.2f}").replace(",", "_").replace(".", ",").replace("_", ".")

    orig_stdout = sys.stdout
    f = open(caminhoexportar, 'w')
    sys.stdout = f

    line1 = ''
    for a in dictlamina:
        line1 += f'{a}\t'

    print(line1.replace(".", ","))

    line1 = ''
    for a in dictlamina:
        line1 += f'{dictlamina[a]}\t'

    print(line1.replace(".", ","))

    sys.stdout = orig_stdout
    f.close()

    return dictlamina

