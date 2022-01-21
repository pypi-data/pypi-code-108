from bs4 import BeautifulSoup
from pprint import pprint
import getopt
import requests
import sys

def check_complaint(complaint_number):
    #complaint_number=97939
    url='http://igpcms.sindhpolice.gov.pk/Complaint_Detail_For_Complainant.aspx?Complaint_Id={}'.format(complaint_number)

    res = requests.get(url)
    parsed = BeautifulSoup(res.text, 'html.parser')
    complaint = {
            'id':0,
            'cnic':'-',
            'date':'-',
            'time':'-',
            'name':'-',
        }

    print('\nSINDH POLICE COMPLAINT')
    print('----------------------')

    try:
        complaint['id'] = parsed.find('span', {'id': 'Label_Track'}).text
        complaint['date'] = parsed.find('span', {'id': 'Label_Date'}).text
        complaint['time'] = parsed.find('span', {'id': 'LabelTime'}).text
        complaint['cnic'] = parsed.find('span', {'id': 'LabelCNIC'}).text
        complaint['cname'] = parsed.find('span', {'id': 'Label_Complainent_Name'}).text
        complaint['fname'] = parsed.find('span', {'id': 'Label_Father_Namne'}).text
        complaint['deadline'] = parsed.find('span', {'id': 'LabelResponseDate'}).text
        complaint['status'] = parsed.find('div', {'class': 'middle_text'}).text
        complaint['comments'] = parsed.find('span', {'class': 'title'})
    except:
        print('ERROR: ', 'Failed to acquire complaint.')

    print('ID: ', complaint['id'])
    print('DATE: ', complaint['date'])
    print('TIME: ', complaint['time'])
    print('CNIC: ', complaint['cnic'])
    print('COMPLAINANT: ', complaint['cname'])
    print('FATHER: ', complaint['fname'])
    print('DEADLINE: ', complaint['deadline'])
    print('STATUS: ', complaint['status'].strip())
    if complaint['comments']:
        print('COMMENTS: ')
        c = complaint['comments']
        while True:
            c = c.nextSibling
            if c:
                pprint(c.text)
            else:
                break

def show_help_and_exit():
            print('Usage: spcs <complaint_number>')
            sys.exit(0)


if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], 'h',['help'])
    if len(opts) < 1: show_help_and_exit()

    for opt in opts:
        if opt[0] in ['-h', '', '--help']:
            show_help_and_exit()
    complaint_number=sys.argv[1]
    check_complaint(complaint_number)
