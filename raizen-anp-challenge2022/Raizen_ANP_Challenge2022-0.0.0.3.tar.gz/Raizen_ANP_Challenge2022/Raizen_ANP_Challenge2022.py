import pandas as pd
class Raizen_ANP_Challenge2022:
  "This function download the real files needed to solve this challenge"
  @property
  def derivados(self):
    #base de dados 1
    df = pd.read_csv('https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/vdpb/vendas-derivados-petroleo-e-etanol/vendas-derivados-petroleo-etanol-m3-1990-2021.csv',sep=';' )
    df["year_month"] = df['ANO'].map(str)+ '-' + df['MÊS'].map(str) 
    df.drop(["ANO", "MÊS", "GRANDE REGIÃO"], axis = 1, inplace = True)
    df = df.rename(columns={'UNIDADE DA FEDERAÇÃO': 'uf', 'PRODUTO': 'product', 'VENDAS':'sales_vol'})
    df.loc[:,'unit'] = 'm^3'
    df=df[["year_month","uf","product","unit","sales_vol"]]
    df.to_csv('vendas-derivados-petroleo.csv', index=False)

  @property
  def diesel(self):
    #base de dados 1
    df2 = pd.read_csv('https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/vdpb/vct/vendas-oleo-diesel-tipo-m3-2013-2021.csv',sep=';')
    df2["year_month"] = df2['ANO'].map(str)+ '-' + df2['MÊS'].map(str) 
    df2.drop(["ANO", "MÊS"], axis = 1, inplace = True)
    df2 = df2.rename(columns={'UNIDADE DA FEDERAÇÃO': 'uf', 'PRODUTO': 'product', 'VENDAS':'sales_vol'})
    df2.loc[:,'unit'] = 'm^3'
    df2=df2[["year_month","uf","product","unit","sales_vol"]]
    return df2.to_csv('vendas-oleo-diesel-tipo.csv', index=False)


  "This function shows metadata's link"
  @property
  def metadados(self):
    print('Link 1: https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/vdpb/vendas-derivados-petroleo-e-etanol/metadados-vendas-derivados-petroleo-etanol.pdf')
    print('Link 2: https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/vdpb/vct/metadados-vendas-oleo-diesel-por-tipo.pdf')
  
