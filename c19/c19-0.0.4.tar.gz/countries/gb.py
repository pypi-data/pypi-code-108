import requests as r
from bs4 import BeautifulSoup as bs

class gb:
    ''' Stats for Pakistan COVID-19 '''
    name = 'United Kingdom'
    code = 'gb'
    _url = 'https://coronavirus.data.gov.uk/'

    def __init__(self):
        ''' Initialisation from source url. '''
        rs = r.get(self._url)
        self.soup = bs(rs.content, 'html.parser')

    def vaccinations(self):
        ''' Vaccinations: total and rate as reported in the last 24 Hrs. '''
        vaccs = {
                'partial': {'total':0, 'rate':0, },
                'full': {'total':0, 'rate':0}
                }

        first = self.soup.find('ul', attrs={'class':'first'}).find_all('li')
        second = self.soup.find('ul', attrs={'class':'second'}).find_all('li')
        booster = self.soup.find('ul', attrs={'class':'booster'}).find_all('li')

        f = {}
        f.update({'total': int(first[1].span.span.meta.attrs['content'])})
        f.update({'rate': int(first[0].span.span.meta.attrs['content'])})

        s = {}
        s.update({'total': int(second[1].span.span.meta.attrs['content'])})
        s.update({'rate': int(second[0].span.span.meta.attrs['content'])})

        b = {}
        b.update({'total': int(booster[1].span.span.meta.attrs['content'])})
        b.update({'rate': int(booster[0].span.span.meta.attrs['content'])})

        vaccs.update( {'partial': { 'total': f['total'] + s['total'], 'rate': f['rate'] + s['rate'] } })
        vaccs.update( {'full': { 'total': b['total'], 'rate': b['rate'] } })

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
        _url='https://coronavirus.data.gov.uk/details/cases?areaType=overview&areaName=United%20Kingdom'
        self._rs = r.get(_url)
        self._soup = bs(self._rs.content, 'html.parser')
        m = self._soup.find('main')
        return m.section.div.div.div.div.a.remove('span').text
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
