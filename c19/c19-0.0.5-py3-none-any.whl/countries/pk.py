import requests as r
from bs4 import BeautifulSoup as bs

class pk:
    ''' Stats for Pakistan COVID-19 '''
    name = 'Pakistan'
    code = 'pk'
    _url = 'https://covid.gov.pk'

    def __init__(self):
        ''' Initialisation from source url. '''
        rs = r.get(self._url)
        self.soup = bs(rs.content, 'html.parser')

    def vaccinations(self):
        ''' Vaccinations: total and rate as reported in the last 24 Hrs. '''
        vaccs = {
                'partial': {'total':0, 'rate':0},
                'full': {'total':0, 'rate':0}
                }

        vacc_texts = self.soup.find_all('div', attrs={'class':'vacc_text'})
        vaccs['partial']['total'] = int(vacc_texts[0].contents[3].text.replace(',',''))
        vaccs['partial']['rate'] = int(vacc_texts[0].contents[5].span.text.replace(',',''))
        vaccs['full']['total'] = int(vacc_texts[1].contents[3].text.replace(',',''))
        vaccs['full']['rate'] = int(vacc_texts[1].contents[5].span.text.replace(',',''))

        return vaccs

    def doses(self):
        ''' Doses: total and rate as reported in the last 24 Hrs. '''
        dosage = { 'total':0, 'rate': 0 }
        
        vacc_texts = self.soup.find_all('div', attrs={'class':'vacc_text'})
        dosage['total'] = int(vacc_texts[2].contents[3].text.replace(',',''))
        dosage['rate'] = int(vacc_texts[2].contents[5].span.text.replace(',',''))

        return dosage

    def cases(self):
        ''' Cases (Normal and Critical): total and rate as reported in the last 24 Hrs. '''
        cases = { 'total':0, 'rate': 0, 'critical': { 'total': 0, 'rate': 0} }
        
        c = self.soup.find('li', attrs={'class':'tests'})
        d = c.find_all('div')
        cases['total'] = int(d[0].span.text.replace(',',''))
        cases['rate'] = int(d[2].b.text.replace(',',''))

        c = self.soup.find('li', attrs={'class':'total'})
        d = c.find_all('div')
        cases['critical']['total'] = int(d[0].span.text.replace(',',''))
        cases['critical']['rate'] = int(d[2].b.text.replace(',',''))

        return cases 

    def deaths(self):
        ''' Deaths: total and rate as reported in the last 24 Hrs. '''
        deaths = { 'total':0, 'rate': 0 }
        c = self.soup.find('li', attrs={'class':'deaths'})
        d = c.find_all('div')
        deaths['total'] = int(d[0].span.text.replace(',',''))
        deaths['rate'] = int(d[2].b.text.replace(',',''))

        return deaths

    def recoveries(self):
        ''' Recoveries: total and rate as reported in the last 24 Hrs. '''
        recoveries = { 'total':0, 'rate': 0 }
        c = self.soup.find('li', attrs={'class': 'recovered'})
        d = c.find_all('div')
        recoveries['total'] = int(d[0].span.text.replace(',',''))
        recoveries['rate'] = int(d[2].b.text.replace(',',''))

        return recoveries

    def tests(self):
        ''' Tests: total and rate as reported in the last 24 Hrs. '''
        tests = { 'total':0, 'rate': 0 }
        c = self.soup.find('li', attrs={'class': 'active'})
        d = c.find_all('div')
        tests['total'] = int(d[0].span.text.replace(',',''))
        tests['rate'] = int(d[2].b.text.replace(',',''))

        return tests
