from bs4 import BeautifulSoup
from alive_progress import alive_bar
import urllib.request

def checkKyreneNumbers():
    tldiv: str = 'sw-content-container2'
    sheets_div: str = 'sheets-viewport'
    url: str = 'https://www.kyrene.org/Page/54632'
    print(f"Checking Kryene COVID Dashboard at {url}")
    with alive_bar(3) as bar:
        bar.text('Downloaded webpage, looking for table.')
        url_contents = urllib.request.urlopen(url)
        bar()
        soup = BeautifulSoup(url_contents, 'html.parser')
        bar.text('Downloading iframe from Google sheets')
        iframe = soup.find("div", {"id": tldiv}).find("iframe")
        inner_iframe = urllib.request.urlopen(iframe.attrs["src"])
        bar()
        new_soup = BeautifulSoup(inner_iframe, 'html.parser')
        bar.text('Adding up totals')
        rows = new_soup.find("div", {"id": sheets_div}).find('table').find_all("tr")
        counts = []
        date_row = rows[1]
        date_str = (date_row.find_all('td'))[1].find(text=True)
        for row in rows[2:]:
            cols = row.find_all('td')
            if len(cols) == 0:
                continue
            data_col = cols[1].find(text=True)
            data_str = str(data_col)
            if data_str.isnumeric():
                counts.append(int(data_str))
        bar()
    print(f"As of {date_str} there are {sum(counts)} active cases")


if __name__ == "__main__":
    checkKyreneNumbers()