import xml.etree.ElementTree as ET
import traceback

class XMLFindNode():
    def __init__(self, xml, namespace):
        self.xml = xml
        self.namespace = namespace
        
    def get_content(self, path):
        complete_path = ''
        for i in path:
            complete_path += self.namespace+i+'/'
        
        return self.xml.findall(complete_path[:-1])


def parse_nfe(xml):
    notas_emitidas = []

    try:
        root = ET.fromstring(xml)
        xmlf = XMLFindNode(root, '{http://www.portalfiscal.inf.br/nfe}')

        serie = xmlf.get_content(['NFe', 'infNFe', 'ide', 'serie'])[0].text
        nota = xmlf.get_content(['NFe', 'infNFe', 'ide', 'nNF'])[0].text
        emissao = xmlf.get_content(['NFe', 'infNFe', 'ide', 'dhEmi'])[0].text
        emitente = xmlf.get_content(['NFe', 'infNFe', 'emit', 'CNPJ'])[0].text
        try:
            destinatario = xmlf.get_content(['NFe', 'infNFe', 'dest', 'CNPJ'])[0].text
        except:
            try:
                destinatario = xmlf.get_content(['NFe', 'infNFe', 'dest', 'idEstrangeiro'])[0].text
            except:
                destinatario = xmlf.get_content(['NFe', 'infNFe', 'dest', 'CPF'])[0].text
        tipo_pagamento = xmlf.get_content(['NFe', 'infNFe', 'pag', 'detPag', 'tPag'])[0].text
        pagamento_avista_aprazo = xmlf.get_content(['NFe', 'infNFe', 'pag', 'detPag', 'indPag'])[0].text
        valor = xmlf.get_content(['NFe', 'infNFe', 'pag', 'detPag', 'vPag'])[0].text

        list_cfops = []
        for cfop in xmlf.get_content(['NFe', 'infNFe', 'det', 'prod', 'CFOP']):
            list_cfops.append(cfop.text)
        
        return [emitente, serie, nota, emissao, destinatario, list_cfops, valor, tipo_pagamento, pagamento_avista_aprazo]
    except:
        return [None] * 9
    
    
def parse_nfe_invoicebra(row, data_class):
    tmp_xml_df = parse_nfe(row['xmlnfe'])
    tmp_xml_df.append(row['_orgid'])
    
    if data_class == 'ar':
        tmp_xml_df.append(row['arinvoice_id'])
    elif data_class == 'ap':
        tmp_xml_df.append(row['invoice_id'])
        
    return tmp_xml_df