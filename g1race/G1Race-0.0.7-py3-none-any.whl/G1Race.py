import requests, re
import pandas as pd
import subprocess as sp

def main():
	smile=input('Select a distance category from SMILE: ')
	url = 'https://www.ifhaonline.org/resources/WTGradedRanking/LWGRank.asp?batch=5'
	page = requests.get(url)
	page.encoding='Shift_jis'
	df = pd.read_html(page.text)[0]
	df.to_csv('race.csv', index=False)
	dff = pd.read_csv('race.csv', index_col=0)
	dff = dff.drop(['Miles','Track','Sex'], axis=1)
	dfs = dff.loc[dff.Cat==smile]
	list=dfs.Country.unique()
	dd = pd.DataFrame(
		{
		 "country": list,
		 "Number_of_races": range(len(list)),
		})
	pd.set_option('display.max_rows', None)
	print('Category:　'+smile)
	print(dfs, '\n')
	print('Number of '+smile+'-category races ranked in 2021')
	for i in list:
		dd.loc[dd.country==i, "Number_of_races"]=int(len(dfs.loc[dfs.Country==i]))
	dd=dd.sort_values(by=['Number_of_races'],ascending=False)
	print(dd.to_string(index=False))
	sp.call("rm race.csv", shell=True)
	
if __name__=="__main__":
	main()
