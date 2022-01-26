import requests,re
import pandas as pd

def main():
 l=input('Select a value to sort by from deaths, VSL, eDamage_per_GNI: ')
 print('downloading total_deaths.csv file')
 import subprocess as sp
 sp.call("wget https://github.com/owid/covid-19-data/raw/master/public/data/jhu/total_deaths.csv",shell=True)
 sp.call("wget https://github.com/Kiuchi424/Lostlifevalue/raw/main/VSL_WWDATASET.csv",shell=True)
 p=pd.read_csv('total_deaths.csv')
 date=p['date'][len(p)-1]
 vsl = pd.read_csv('VSL_WWDATASET.csv')
 d=vsl.Country
 dd=pd.DataFrame(
  { 
   "country": d,
   "deaths": range(len(d)),
   "population": range(len(d)),
   "VSL": range(len(d)),
   "eloss_total": range(len(d)),
   "GNI": range(len(d)),
   "GNI_total": range(len(d)),
   "eDamage_per_GNI": range(len(d)),
  })
 print('score is created in result.csv')
 print('date is ',date)
 p=p.fillna(0)
 for i in d:
  dd.loc[dd.country==i,'deaths']=int(p[i][len(p)-1])
  dd.loc[dd.country==i,'population']=round(float(vsl.loc[vsl.Country==i,'Population']/100000),3)
  dd.loc[dd.country==i,'VSL']=float(vsl.loc[vsl.Country==i, 'VSL'])
  dd.loc[dd.country==i,'eloss_total']=float(dd.loc[dd.country==i,'deaths']*dd.loc[dd.country==i,'VSL'])
  dd.loc[dd.country==i,'GNI']=float(vsl.loc[vsl.Country==i, 'GNI'])
  dd.loc[dd.country==i,'GNI_total']=float(dd.loc[dd.country==i,'GNI']*dd.loc[dd.country==i,'population'])
  dd.loc[dd.country==i,'eDamage_per_GNI']=round(float((dd.loc[dd.country==i,'eloss_total']*1000000)/(dd.loc[dd.country==i,'GNI_total']*1000*100000)),4) 
 
 dd=dd.sort_values(by=[l],ascending=False)
 dd.to_csv('result.csv',index=False)
 df=pd.read_csv('result.csv',index_col=0)
 pd.set_option('display.max_rows', None)
 print(df)
 sp.call("rm total_deaths.csv VSL_WWDATASET.csv",shell=True)

if __name__ == "__main__":
 main()
