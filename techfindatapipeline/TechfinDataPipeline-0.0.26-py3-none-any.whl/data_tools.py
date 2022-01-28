import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from pycarol.carol import Carol
from pycarol.auth.PwdAuth import PwdAuth
from pycarol.staging import Staging
from pycarol.data_models import DataModel
from pycarol.query import Query
from pycarol.connectors import Connectors

from TechfinDataPipeline.invoice_struct import InvoiceStruct
from TechfinDataPipeline.nfe_xml_parser import parse_nfe_invoicebra

#from invoice_struct import InvoiceStruct
#from nfe_xml_parser import parse_nfe_invoicebra

def getData(stag, list_of_tables, connector, rename_rule=None, valid_assert=True, max_workers=1):
    '''
    Download the data from Carol

    Params
    stag: Staging carol object
    list_of_tables: List of tables to be downloaded with each columns. E.g.: ['table', ['field_1', 'field_2', 'field_3'], ...]
    connector: Connector name
    rename_rule: If want to rename any column. Default value is None

    Return
    Pandas DataFrame
    '''
    downloaded_tables = {}

    for table in list_of_tables:
        print(f'Downloading {table[0]}...')
        try:
            data = stag.fetch_parquet(table[0], 
                                      connector_name=connector,
                                      merge_records=True, 
                                      backend='pandas',
                                      return_dask_graph=False,
                                      columns=table[1], 
                                      return_metadata=False, 
                                      callback=None,
                                      max_hits=None, 
                                      cds=True, 
                                      max_workers=max_workers, 
                                      file_pattern=None,
                                      return_callback_result=False)

            data = data.drop_duplicates()
            if 'deleted' in data.columns:
                data = data[data['deleted'] == False]
                data = data.drop(['deleted'], axis=1)

            print('Done.')
            
        except:
            print('Error downloading data.')
            data = []
        
        if valid_assert:
            if len(data) == 0:
                print(f"There is no data on {table[0]} table. Check the CDS Golden data.")
                continue

        downloaded_tables.update({table[0]:data})

    return downloaded_tables


def getListOfTables(session,connector_name):
    '''
    Returns de default list of main tables used in antecipa/financial cockpit project

    Return
    List with table name and fields
    '''
    
    # Baixo todos os nomes de stagings do connector especificado para verificar quais tabelas estão disponiveis para download.
    conn_stats = Connectors(session).stats(connector_name=connector_name)
    st = [i for i in list(conn_stats.values())[0]]
    st = sorted(st)
    st
    
    tables =  [['arinvoice',['_orgid', 'businesspartner_id', 'deleted', 'docissue', 'invoice_id', 'transactiontype'],True],
               ['arinvoiceinstallment',['_orgid', 'invoice_id', 'invoiceinstallment_id', 'duedatecash', 'deleted', 'sequencecode', 'erp_id'],True],
               ['arinvoicepayments', ['_orgid', 'amount', 'amountlocal', 'currency_id', 'deleted',
                                      'invoiceinstallment_id', 'invoicepayments_id', 'issuedate',
                                      'paymentdate', 'paymentstype_id', 'paymentsreference'],True],
               ['apinvoice', ['_orgid', 'businesspartner_id', 'deleted', 'docissue', 'invoice_id', 'transactiontype'],True],
               ['apinvoiceinstallment', ['_orgid', 'invoice_id', 'invoiceinstallment_id', 'duedatecash', 'deleted', 'sequencecode', 'erp_id'],True],
               ['apinvoicepayments', ['_orgid', 'amount', 'amountlocal', 'currency_id', 'deleted',
                                      'invoiceinstallment_id', 'invoicepayments_id', 'issuedate',
                                      'paymentdate', 'paymentstype_id', 'paymentsreference'],True],
               ['arpaymentstype', ['cashflow', 'code', 'deleted', 'description', 'signal',  'transactiontype_id',  'updatebalance'],True],
               ['arinvoicebra', ['_orgid', 'arinvoice_id', 'xmlnfe', 'erp_id'], False],
               ['apinvoicebra', ['_orgid', 'invoice_id', 'xmlnfe', 'erp_id'], False],
               ['arinvoiceorigin', ['_orgid', 'devolutioninvoice_id', 'itemtotalizer', 'devolutioninvoicetotal', 'originalinvoice_id', 'amount'], False],
               ['organization', ['federalid', 'uuid'], True],
               ['mddocreference', ['docreference_id', 'docreference', 'doctype'], True],
               ['mdbusinesspartnerdocreference', ['businesspartner_id', 'docreference_id'], True],
               ['mdbusinesspartner', None, True],
               ['arpaymentsbank', ['bankpayment_id', 'deleted', 'invoicepayments_id'],False],
               ['arbankpayment', ['amountlocal', 'bank_id', 'bankpayment_id', 'deleted'], False],
               ['mdbankaccount', ['bank_id', 'bankreferenceid', 'deleted', 'name'], False]
              ]
    
    for t in tables:
        if t[0] not in st:
            if t[2]:
                return False,tables
            else:
                tables.remove(t)
    
    return True,tables


def ar_mergeData(downloaded_tables):
    '''
    Function to merge the data from Invoice, Installment, Payments and Paymentstypes
    
    Params
    downloaded_tables: Dict with {table_name:DataFrame}. This data can be got calling the function getData.

    Return
    DataFrame with the data.
    '''
    #-----------------------
    # Dados de recebimentos
    #-----------------------
    downloaded_tables['arinvoice'] = downloaded_tables['arinvoice'].rename({'docreference':'erp_docreference'}, axis=1)
    
    ar_merged_data = downloaded_tables['arinvoice'].merge(downloaded_tables['arinvoiceinstallment'],
                                                          left_on=['_orgid','invoice_id'],
                                                          right_on=['_orgid','invoice_id'],
                                                          how='left')
    
    ar_merged_data = ar_merged_data.merge(downloaded_tables['arinvoicepayments'],
                                          left_on=['_orgid','invoiceinstallment_id'],
                                          right_on=['_orgid','invoiceinstallment_id'],
                                          how='left')
    
    #-----------------------
    # Tipos de registro de payments
    #-----------------------
    ar_merged_data = ar_merged_data.merge(downloaded_tables['arpaymentstype'],
                                     left_on=['paymentstype_id'],
                                     right_on=['transactiontype_id'],
                                     how='left')
    
    #-----------------------
    # Dados do Cliente
    #-----------------------
    ar_merged_data = ar_merged_data.merge(downloaded_tables['mdbusinesspartnerdocreference'].drop(['_orgid'], axis=1),
                                     left_on=['businesspartner_id'],
                                     right_on=['businesspartner_id'],
                                     how='left')
    
    ar_merged_data = ar_merged_data.merge(downloaded_tables['mddocreference'].drop(['_orgid'], axis=1),
                                     left_on=['docreference_id'],
                                     right_on=['docreference_id'],
                                     how='left')
    
    #-----------------------
    # Dados da empresa
    #-----------------------
    downloaded_tables['organization'] = downloaded_tables['organization'].sort_values(by=['federalid']).drop_duplicates(subset=['uuid'])
    
    ar_merged_data = ar_merged_data.merge(downloaded_tables['organization'],
                                    left_on='_orgid',
                                    right_on='uuid',
                                    how='left')
    
    ar_merged_data['duedatecash'] = pd.to_datetime(ar_merged_data['duedatecash'], errors='coerce').dt.tz_localize(None)
    ar_merged_data['paymentdate'] = pd.to_datetime(ar_merged_data['paymentdate'], errors='coerce').dt.tz_localize(None)
    ar_merged_data['docissue'] = pd.to_datetime(ar_merged_data['docissue'], errors='coerce').dt.tz_localize(None)
    ar_merged_data['issuedate'] = pd.to_datetime(ar_merged_data['issuedate'], errors='coerce').dt.tz_localize(None)
    
    ar_merged_data = ar_merged_data[['_orgid',
                                      'invoice_id',
                                      'invoiceinstallment_id',
                                      'invoicepayments_id',
                                      'docissue',
                                      'duedatecash',
                                      'paymentdate',
                                      'issuedate',
                                      'amount',
                                      'amountlocal',
                                      'cashflow',
                                      'code',
                                      'description',
                                      'signal',
                                      'sequencecode',
                                      'docreference',
                                      'doctype',
                                      'federalid',
                                      'erp_id',
                                      'paymentsreference',
                                      'transactiontype']]
    
    ar_merged_data = ar_merged_data.sort_values(by=['issuedate', 'code'])
    ar_merged_data = ar_merged_data[~ar_merged_data['invoiceinstallment_id'].isna()]
    
    return ar_merged_data


def ar_mergeDataBordero(ar_merged_data, downloaded_tables):
    
    keys = downloaded_tables.keys()
    
    if 'arpaymentsbank' in keys and 'arbankpayment' in keys and 'mdbankaccount' in keys:
        #-----------------------
        # Dados de borderos
        #-----------------------
        ar_merged_data = ar_merged_data.merge(downloaded_tables['arpaymentsbank'][['invoicepayments_id', 'bankpayment_id']],
                         left_on=['invoicepayments_id'],
                         right_on=['invoicepayments_id'],
                         how='left')

        downloaded_tables['arbankpayment'] = downloaded_tables['arbankpayment'].rename({'amountlocal':'amountlocal_bank'}, axis=1)

        ar_merged_data = ar_merged_data.merge(downloaded_tables['arbankpayment'][['bankpayment_id','amountlocal_bank', 'bank_id']],
                         left_on=['bankpayment_id'],
                         right_on=['bankpayment_id'],
                         how='left')

        downloaded_tables['mdbankaccount'] = downloaded_tables['mdbankaccount'].rename({'name':'name_bank'}, axis=1)

        ar_merged_data = ar_merged_data.merge(downloaded_tables['mdbankaccount'][['bank_id', 'name_bank']],
                                                   left_on=['bank_id'],
                                                   right_on=['bank_id'],
                                                   how='left')

        ar_merged_data = ar_merged_data[['_orgid',
                                          'invoice_id',
                                          'invoiceinstallment_id',
                                          'invoicepayments_id',
                                          'docissue',
                                          'duedatecash',
                                          'paymentdate',
                                          'issuedate',
                                          'amount',
                                          'amountlocal',
                                          'cashflow',
                                          'code',
                                          'description',
                                          'signal',
                                          'sequencecode',
                                          'docreference',
                                          'doctype',
                                          'federalid',
                                          'erp_id',
                                          'bankpayment_id',
                                          'amountlocal_bank',
                                          'name_bank',
                                          'paymentsreference',
                                          'transactiontype']]
    
    return ar_merged_data


def ap_mergeData(downloaded_tables):
    '''
    Function to merge the data from Invoice, Installment, Payments and Paymentstypes
    
    Params
    downloaded_tables: Dict with {table_name:DataFrame}. This data can be got calling the function getData.

    Return
    DataFrame with the data.
    '''
    downloaded_tables['apinvoice'] = downloaded_tables['apinvoice'].rename({'docreference':'erp_docreference'}, axis=1)
    
    ap_merged_data = downloaded_tables['apinvoice'].merge(downloaded_tables['apinvoiceinstallment'],
                                                          left_on=['_orgid','invoice_id'],
                                                          right_on=['_orgid','invoice_id'],
                                                          how='left')
    
    ap_merged_data = ap_merged_data.merge(downloaded_tables['apinvoicepayments'],
                                          left_on=['_orgid','invoiceinstallment_id'],
                                          right_on=['_orgid','invoiceinstallment_id'],
                                          how='left')
    
    ap_merged_data = ap_merged_data.merge(downloaded_tables['arpaymentstype'],
                                     left_on=['paymentstype_id'],
                                     right_on=['transactiontype_id'],
                                     how='left')
    
    ap_merged_data = ap_merged_data.merge(downloaded_tables['mdbusinesspartnerdocreference'],
                                     left_on=['businesspartner_id'],
                                     right_on=['businesspartner_id'],
                                     how='left')
    
    ap_merged_data = ap_merged_data.merge(downloaded_tables['mddocreference'],
                                     left_on=['docreference_id'],
                                     right_on=['docreference_id'],
                                     how='left')
    
    downloaded_tables['organization'] = downloaded_tables['organization'].sort_values(by=['federalid']).drop_duplicates(subset=['uuid'])
    
    ap_merged_data = ap_merged_data.merge(downloaded_tables['organization'],
                                    left_on='_orgid',
                                    right_on='uuid',
                                    how='left')
    
    ap_merged_data['duedatecash'] = pd.to_datetime(ap_merged_data['duedatecash'], errors='coerce').dt.tz_localize(None)
    ap_merged_data['paymentdate'] = pd.to_datetime(ap_merged_data['paymentdate'], errors='coerce').dt.tz_localize(None)
    ap_merged_data['docissue'] = pd.to_datetime(ap_merged_data['docissue'], errors='coerce').dt.tz_localize(None)
    ap_merged_data['issuedate'] = pd.to_datetime(ap_merged_data['issuedate'], errors='coerce').dt.tz_localize(None)
    
    ap_merged_data = ap_merged_data[['_orgid',
                                      'invoice_id',
                                      'invoiceinstallment_id',
                                      'invoicepayments_id',
                                      'docissue',
                                      'duedatecash',
                                      'paymentdate',
                                      'issuedate',
                                      'amount',
                                      'amountlocal',
                                      'cashflow',
                                      'code',
                                      'description',
                                      'signal',
                                      'sequencecode',
                                      'docreference',
                                      'doctype',
                                      'federalid',
                                      'erp_id',
                                      'paymentsreference',
                                      'transactiontype']]
    
    ap_merged_data = ap_merged_data.sort_values(by=['issuedate', 'code'])
    ap_merged_data = ap_merged_data[~ap_merged_data['invoiceinstallment_id'].isna()]
    
    return ap_merged_data


def clean_data_inconsistency(data):
    '''
    Apply some cleanse rules to the data.
    
    Params
    DataFrame with merged data from functions ap_mergeData and ar_mergeData.

    Return
    DataFrame with the cleanse rules applied.
    '''
    
    agg_data = data.groupby(['_orgid', 'invoice_id', 'invoiceinstallment_id'])\
                   .agg({'code': 'value_counts'})\
                   .rename({'code':'quantidade'}, axis=1)\
                   .reset_index()
    
    # Crio uma pivot table com uma dimensão sendo o installment, a outra dimensão o código do evento e os valores
    # o count de quantos eventos desse tipo existem
    agg_data = pd.pivot_table(agg_data,
                               values='quantidade',
                               index=['_orgid', 'invoice_id', 'invoiceinstallment_id'],
                               columns=['code'],
                               aggfunc=np.sum)\
                  .fillna(0)\
                  .reset_index()
    
    # Removo todos os invoices que possuam algum installment com apenas exclusão sem inclusão
    invoices_without_payment_inclusion = agg_data[agg_data['02'] == 0]['invoice_id'].unique()
    data = data[~data['invoice_id'].isin(invoices_without_payment_inclusion)]
    
    # Removo todos os eventos de payments de estorno onde não houver uma ação correspondente.
    # Exemplo: Estorno de Baixa, porém não existe o evento de Baixa. Esses eventos serão considerados inconsistencias.
    
    # Removo todos os installments que não tem nenhuma baixa porém tem estorno de baixa
    if '17' in agg_data.columns:
        df_error_payments = agg_data[(agg_data['06'] == 0) & (agg_data['17'] > agg_data['06'])][['_orgid','invoice_id','invoiceinstallment_id']]

        data = data[~((data['_orgid'].isin(df_error_payments['_orgid'].tolist())) & 
                                          (data['invoice_id'].isin(df_error_payments['invoice_id'].tolist())) & 
                                          (data['invoiceinstallment_id'].isin(df_error_payments['invoiceinstallment_id'].tolist())))]
    
    if '98' in agg_data.columns:
        df_error_payments = agg_data[(agg_data['97'] == 0) & (agg_data['98'] > agg_data['97'])][['_orgid','invoice_id','invoiceinstallment_id']]

        data = data[~((data['_orgid'].isin(df_error_payments['_orgid'].tolist())) & 
                                          (data['invoice_id'].isin(df_error_payments['invoice_id'].tolist())) & 
                                          (data['invoiceinstallment_id'].isin(df_error_payments['invoiceinstallment_id'].tolist())) &
                                          (data['code'] == '98'))]
    
    # Removo parcelas com código == 99
    data = data[data['sequencecode'] != '99']
    
    return data


def read_data_struct(invoice_data):
    '''
    Apply the data struct to the data to identify the last status of each installment.
    
    Params
    DataFrame with merged data from functions ap_mergeData and ar_mergeData.

    Return
    DataFrame with the final status from each installment.
    '''
    
    invoice_struc = InvoiceStruct()
    
    invoice_data.apply(lambda row: invoice_struc.add_payment(row['_orgid'],
                                                           row['invoice_id'],
                                                           row['invoiceinstallment_id'],
                                                           row['amountlocal'],
                                                           row['code'],
                                                           row['sequencecode'],
                                                           row['docissue'],
                                                           row['duedatecash'],
                                                           row['paymentdate'],
                                                           row['issuedate'],
                                                           row['docreference'],
                                                           row['doctype'],
                                                           row['federalid'],
                                                           row['erp_id'],
                                                           row['paymentsreference'],
                                                           row['transactiontype']), axis=1)
    
    orgs_ids = invoice_struc.struct.keys()
    invoices_list = []

    for org in orgs_ids:
        invoices_ids = invoice_struc.struct[org].keys()

        for invoice in invoices_ids:
            installments_ids = invoice_struc.struct[org][invoice].keys()

            for installment in installments_ids:
                tmp_list = [org, invoice, installment]
                tmp_list += list(invoice_struc.struct[org][invoice][installment].values())

                invoices_list.append(tmp_list)


    invoices_df = pd.DataFrame(invoices_list, columns=['org_id',
                                                         'invoice_id',
                                                         'installment_id',
                                                         'value',
                                                         'balance',
                                                         'anticipated',
                                                         'duedate',
                                                         'payment_date',
                                                         'late_days',
                                                         'sequence_code',
                                                         'discount',
                                                         'docissue',
                                                         'anticipation_date',
                                                         'anticipation_value',
                                                         'days_to_receive',
                                                         'docreference',
                                                         'doctype',
                                                         'paid_values',
                                                         'federalid',
                                                         'erp_id',
                                                         'paymentsreference',
                                                         'transactiontype',
                                                         'excluded'])
    
    return invoices_df


def nfe_parser(downloaded_tables, data_class, invoices_df):
    '''
    Apply the NFe parser.
    
    Params
    invoicebra: DataFrame with the NFe XML
    invoices_df: The DataFrame that will be updated with the information from each NFe

    Return
    DataFrame with the NFe informations.
    '''
    
    if data_class == 'ar' and 'arinvoicebra' in downloaded_tables.keys():
        invoicebra = downloaded_tables['arinvoicebra']
    elif data_class == 'ap' and 'apinvoicebra' in downloaded_tables.keys():
        invoicebra = downloaded_tables['apinvoicebra']
    else:
        return invoices_df
    
    invoicebra['xmlnfe'] = invoicebra['xmlnfe'].fillna('')
    invoicebra = invoicebra[invoicebra['xmlnfe'].str.strip() != '']
    xml_parser_df = invoicebra.apply(lambda row: parse_nfe_invoicebra(row, data_class), axis=1, result_type='expand')
    
    if len(xml_parser_df) > 0:
    
        xml_parser_df.columns=['nfe_emitente',
                               'nfe_serie',
                               'nfe_numero',
                               'nfe_emissao',
                               'nfe_cliente',
                               'nfe_cfops',
                               'nfe_valor',
                               'nfe_tipo_pagamento',
                               'nfe_a_prazo',
                               'org_id',
                               'invoice_id']
        
        xml_parser_df = xml_parser_df.drop(['org_id'], axis=1)
        invoices_df = invoices_df.merge(xml_parser_df,
                                          left_on=['invoice_id'],
                                          right_on=['invoice_id'],
                                          how='left')
    
    return invoices_df


def get_returns(downloaded_tables, invoices_df):
    '''
    Identify the invoices that customer have returned.
    
    Params
    invoiceorigin: DataFrame with the returns information
    invoices_df: The DataFrame that will be updated with the information from each NFe

    Return
    DataFrame with the returns informations.
    '''
    
    if 'arinvoiceorigin' in downloaded_tables.keys():
        invoiceorigin = downloaded_tables['arinvoiceorigin']
        invoiceorigin_agg = invoiceorigin.groupby(['_orgid','devolutioninvoice_id']).agg({'itemtotalizer':'sum',
                                                                                                'devolutioninvoicetotal':'first',
                                                                                                'originalinvoice_id':'first'}).reset_index()

        devolutioninvoice_ids = invoiceorigin_agg[invoiceorigin_agg['itemtotalizer'] == invoiceorigin_agg['devolutioninvoicetotal']]['devolutioninvoice_id'].unique()

        invoiceorigin_filtered = invoiceorigin[invoiceorigin['devolutioninvoice_id'].isin(devolutioninvoice_ids)]
        invoiceorigin_filtered = invoiceorigin_filtered[['_orgid', 'originalinvoice_id', 'devolutioninvoice_id', 'amount']]\
                                                        .groupby(['_orgid', 'originalinvoice_id', 'devolutioninvoice_id'])\
                                                        .sum()\
                                                        .reset_index()

        invoiceorigin_filtered['return'] = True

        invoices_df = invoices_df.merge(invoiceorigin_filtered[['_orgid', 'originalinvoice_id', 'amount', 'return']],
                                          left_on=['org_id','invoice_id'],
                                          right_on=['_orgid', 'originalinvoice_id'],
                                          how='left')

        invoices_df['return'] = invoices_df['return'].fillna(False)

        invoices_df = invoices_df.drop(['_orgid', 'originalinvoice_id'], axis=1)
        invoices_df = invoices_df.rename({'amount':'returned_amount_total'}, axis=1)
    
    return invoices_df


def default_techfin_data_parser(connector, max_workers=1):
    '''
    Default function that runs all data pipeline from a specific connector.
    
    Params
    connector: Connector name

    Return
    DataFrame with receivables, DataFrame with payments
    '''
    
    dotenv_path = '.env'
    load_dotenv(dotenv_path)

    login = Carol()
    stag  = Staging(login)

    # Pego a lista das tabelas que precisam ser baixadas e os campos utilizados de cada uma delas
    possible,tables = getListOfTables(login, connector)
  
    
    # Faço o download das tabelas
    if possible:
        downloaded_tables = getData(stag, tables, connector, max_workers=max_workers)
    
        # Executo o merge dos dados de invoice, installment e payments
        ar_merged_data = ar_mergeData(downloaded_tables)
        ap_merged_data = ap_mergeData(downloaded_tables)
        
        # leio as informações de antecipação feita por borderos
        ar_merged_data = ar_mergeDataBordero(ar_merged_data, downloaded_tables)
        
        # Aplico regra de limpeza dos dados
        ar_merged_data = clean_data_inconsistency(ar_merged_data)
        ap_merged_data = clean_data_inconsistency(ap_merged_data)

        # Organizo os dados dos invoices na estrutura de dados definida na classe InvoiceStruct
        ar_invoices_df = read_data_struct(ar_merged_data)
        ap_invoices_df = read_data_struct(ap_merged_data)

        # Faço o parser dos XML das NFe
        ar_invoices_df = nfe_parser(downloaded_tables, 'ar', ar_invoices_df)
    
        # Identifica as devoluções
        ar_invoices_df = get_returns(downloaded_tables, ar_invoices_df)
    
        return ar_invoices_df, ap_invoices_df
    else:
        print("Tabelas importantes não estão disponiveis nesse connector, Verique na carol se está tudo certo com as tabelas:\n ")
        for t in tables:
            if t[2]:
                print(t[0]+'\n')

