import requests
from bs4 import BeautifulSoup
from itertools import product
from integrations.integration import Integration
import pandas as pd

''' get wikipedia page using beaufulsap that will be used to parse a wikipedia table '''
def get_wikipedia_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

''' get wikipedia table using beaufulsap that will be used to parse a wikipedia table '''
def get_wikipedia_table(soup):
    table = soup.find('table', {'class': 'wikitable'})
    return table

''' get wikipedia table using beaufulsap that will be used to parse a wikipedia table '''
def get_wikipedia_tables(soup):
    tables = soup.find_all('table', {'class': 'wikitable'})
    return tables

''' get wikipedia table headers using beaufulsap that will be used to parse a wikipedia table '''
def get_wikipedia_table_headers(table_rows):
    headers = []
    for th in table_rows[0].find_all('th'):
        headers.append(th.text.strip())
    return headers

def wikipedia_table_to_dataframe(table_tag):
    rowspans = []  # track pending rowspans
    rows = table_tag.find_all('tr')

    # first scan, see how many columns we need
    colcount = 0
    for r, row in enumerate(rows):
        cells = row.find_all(['td', 'th'], recursive=False)
        # count columns (including spanned).
        # add active rowspans from preceding rows
        # we *ignore* the colspan value on the last cell, to prevent
        # creating 'phantom' columns with no actual cells, only extended
        # colspans. This is achieved by hardcoding the last cell width as 1. 
        # a colspan of 0 means “fill until the end” but can really only apply
        # to the last cell; ignore it elsewhere. 
        colcount = max(
            colcount,
            sum(int(c.get('colspan', 1)) or 1 for c in cells[:-1]) + len(cells[-1:]) + len(rowspans))
        # update rowspan bookkeeping; 0 is a span to the bottom. 
        rowspans += [int(c.get('rowspan', 1)) or len(rows) - r for c in cells]
        rowspans = [s - 1 for s in rowspans if s > 1]

    # it doesn't matter if there are still rowspan numbers 'active'; no extra
    # rows to show in the table means the larger than 1 rowspan numbers in the
    # last table row are ignored.

    # build an empty matrix for all possible cells
    table = [[None] * colcount for row in rows]

    # fill matrix from row data
    rowspans = {}  # track pending rowspans, column number mapping to count
    for row, row_elem in enumerate(rows):
        span_offset = 0  # how many columns are skipped due to row and colspans 
        for col, cell in enumerate(row_elem.find_all(['td', 'th'], recursive=False)):
            # adjust for preceding row and colspans
            col += span_offset
            while rowspans.get(col, 0):
                span_offset += 1
                col += 1

            # fill table data
            rowspan = rowspans[col] = int(cell.get('rowspan', 1)) or len(rows) - row
            colspan = int(cell.get('colspan', 1)) or colcount - col
            # next column is offset by the colspan
            span_offset += colspan - 1
            value = cell.get_text().strip()
            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value
                    rowspans[col + dcol] = rowspan
                except IndexError:
                    # rowspan or colspan outside the confines of the table
                    pass

        # update rowspan bookkeeping
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}
    df = pd.DataFrame(table)

    header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = header 
    return df

class wikipedia_table(Integration):
    def load():
    	print('Mamma says hi')

#Test
url = 'https://en.wikipedia.org/wiki/2021%E2%80%9322_UEFA_Champions_League'
soup = get_wikipedia_page(url)
table = get_wikipedia_table(soup)
wikipedia_table_to_dataframe(table)

#Concatenated all the df from the same table
wikipedia_table_to_dataframe(get_wikipedia_tables(soup)[0]).append(wikipedia_table_to_dataframe(get_wikipedia_tables(soup)[1])).append(wikipedia_table_to_dataframe(get_wikipedia_tables(soup)[2]))