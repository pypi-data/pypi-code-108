# Creator : Sunkyeong Lee
# Inquiry : sunkyeong.lee@concentrix.com / sunkyong9768@gmail.com

import urllib.request
import json
from sqlalchemy import create_engine
import pandas as pd
import time

api_key = ''

def getConversionData(company, start_date, end_date, site_code, channel):
    url = 'https://api.similarweb.com/v1/segment/{company}/conversion-analysis/query?api_key={api_key}&start_date={start_date}&end_date={end_date}&country={site_code}&metrics=visits,converted-visits&channel={channel}&main_domain_only=false&format=json&show_verified=false'.format(company = company, api_key = api_key, start_date = start_date, end_date = end_date, site_code = site_code, channel = channel)

    response = urllib.request.urlopen(url)
    response_message = response.read().decode('utf8')

    return pd.DataFrame(json.loads(response_message)['segments'])

# 22-01-27 트래픽 추가
def getTrafficData(domain, start_date, end_date, site_code):
    url = 'https://api.similarweb.com/v1/website/{domain}/total-traffic-and-engagement/visits?api_key={api_key}&start_date={start_date}&end_date={end_date}&country={site_code}&granularity=monthly&main_domain_only=false&format=json&show_verified=false&mtd=false'.format(domain = domain, api_key = api_key, start_date = start_date, end_date = end_date, site_code = site_code)

    response = urllib.request.urlopen(url)
    response_message = response.read().decode('utf8')

    return pd.DataFrame(json.loads(response_message)['visits'])

# 22-01-27 bounce rate 추가
def getBounceRateData(domain, start_date, end_date, site_code):
    url = 'https://api.similarweb.com/v1/website/{domain}/total-traffic-and-engagement/bounce-rate?api_key={api_key}&start_date={start_date}&end_date={end_date}&country={site_code}&granularity=monthly&main_domain_only=false&format=json&show_verified=false&mtd=false'.format(domain = domain, api_key = api_key, start_date = start_date, end_date = end_date, site_code = site_code)

    response = urllib.request.urlopen(url)
    response_message = response.read().decode('utf8')

    return pd.DataFrame(json.loads(response_message)['bounce_rate'])

def getMobileChannel(domain, start_date, end_date, site_code):
    url = 'https://api.similarweb.com/v1/website/{domain}/traffic-sources/mobile-overview-share?api_key={api_key}&start_date={start_date}&end_date={end_date}&country={site_code}&granularity=monthly&main_domain_only=false&format=json'.format(domain = domain, api_key = api_key, start_date = start_date, end_date = end_date, site_code = site_code)

    response = urllib.request.urlopen(url)
    response_message = response.read().decode('utf8')

    a = pd.DataFrame(json.loads(response_message)['visits'][domain])    

    df3 = []
    for j in range(len(a['visits'])):
        df = a['visits'].loc[j]
        df2 = pd.DataFrame(df)
        df2.insert(0, 'source', a['source_type'].loc[j], True)
        p = df2.to_dict('records')
        for i in range(len(p)):
            df3.append(p[i])

    return pd.DataFrame(df3)
    
    # return pd.DataFrame(json.loads(response_message)['visits'][domain])    


def stackTodb(dataFrame, dbTableName):
    print(dataFrame)
    db_connection_str = 'mysql+pymysql://root:12345@127.0.0.1:3307/similarweb'
    db_connection = create_engine(db_connection_str, encoding='utf-8')
    conn = db_connection.connect()

    dataFrame.to_sql(name=dbTableName, con=db_connection, if_exists='append', index=False)
    print("finished")


def websiteConverter(website):
    website_list = {'samsung' : 'samsung.com%23', 'apple' : 'apple.com%23', 'lg' : 'lg.com%23', 'currys' : 'currys.co.uk%23', 'amazon.uk mobile phone' : 'amazon.co.uk%23Mobile%20Phones%20and%20Communication', 'amazon.uk home appliances' : 'amazon.co.uk%23Kitchen%20and%20Home%20Appliances', 'hp' : 'hp.com%23', 'amazon.uk home cinema' : 'amazon.co.uk%23Home%20Cinema,%20TV%20and%20Video', 'dell' : 'dell.com%23', 'amazon cell phone' : 'amazon.com%23Cell%20Phones%20and%20Accessories', 'amazon electronics' : 'amazon.com%23Electronics', 'walmart' : 'walmart.com%23Electronics', 'amazon appliances' : 'amazon.com%23Appliances', 'bestbuy' : 'bestbuy.com%23'}
    return website_list[website]

def companyNameConverter(company):
    company_list = {'samsung' : 'samsung', 'apple' : 'apple', 'lg' : 'lg', 'currys' : 'currys', 'amazon.uk mobile phone' : 'amazon', 'amazon.uk home appliances' : 'amazon', 'hp' : 'hp', 'amazon.uk home cinema' : 'amazon', 'dell' : 'dell', 'amazon cell phone' : 'amazon', 'amazon electronics' : 'amazon', 'walmart' : 'walmart', 'amazon appliances' : 'amazon', 'bestbuy' : 'bestbuy'}
    return company_list[company]

# 22-01-14 eg, world 추가
def siteCodeConverter(sitecode):
    sitecode_list = {'world' : 'world', 'au' : 'au', 'br' : 'br', 'ca' : 'ca', 'fr' : 'fr', 'de' : 'de', 'in' : 'in', 'id' : 'id', 'it' : 'it', 'nl' : 'nl', 'ru' : 'ru', 'sa' : 'sa', 'es' : 'es', 'se' : 'se', 'tr' : 'tr', 'uk' : 'gb', 'ae' : 'ae', 'us' : 'us', 'eg' : 'eg'}
    return sitecode_list[sitecode]

# 22-01-26 channel 추가
def channelConverter(channel):
    channel_list = {'total' : 'total', 'direct' : 'direct', 'paid-search' : 'paid-search', 'organic-search' : 'organic-search', 'display-ads' : 'display-ads', 'referrals' : 'referrals', 'mail' : 'mail', 'social' : 'social'}
    return channel_list[channel]

# 22-01-27 domain 추가
def domainConverter(domain):
    domain_list = {'samsung' : 'samsung.com', 'apple' : 'apple.com'}
    return domain_list[domain]

def dataCaller(company, start_date, end_date, site_code, channel):
    dataFrame = getConversionData(websiteConverter(company), start_date, end_date, siteCodeConverter(site_code), channelConverter(channel))
    dataFrame.insert(0, "site_code", site_code, True)
    dataFrame.insert(1, "data_saved", time.strftime('%Y-%m-%d', time.localtime()), True)
    dataFrame.insert(2, "company_name", companyNameConverter(company), True)
    dataFrame.insert(3, "sub_company_name", company, True)
    dataFrame.insert(4, "channel", channel, True)

    return dataFrame

def dataCallerTraffic(domain, start_date, end_date, site_code):
    dataFrame = getTrafficData(domainConverter(domain), start_date, end_date, siteCodeConverter(site_code))
    dataFrame.insert(0, "site_code", site_code, True)
    dataFrame.insert(1, "data_saved", time.strftime('%Y-%m-%d', time.localtime()), True)
    dataFrame.insert(2, "domain", domainConverter(domain), True)
    
    return dataFrame

def dataCallerBR(domain, start_date, end_date, site_code):
    dataFrame = getBounceRateData(domainConverter(domain), start_date, end_date, siteCodeConverter(site_code))
    dataFrame.insert(0, "site_code", site_code, True)
    dataFrame.insert(1, "data_saved", time.strftime('%Y-%m-%d', time.localtime()), True)
    dataFrame.insert(2, "domain", domainConverter(domain), True)
    
    return dataFrame


def dataCallerMobileChannel(domain, start_date, end_date, site_code):
    dataFrame = getMobileChannel(domainConverter(domain), start_date, end_date, siteCodeConverter(site_code))
    dataFrame.insert(0, "site_code", site_code, True)
    dataFrame.insert(1, "data_saved", time.strftime('%Y-%m-%d', time.localtime()), True)
    dataFrame.insert(2, "domain", domainConverter(domain), True)
    
    return dataFrame


def SW_Conversion(company, channel, start_date, end_date, site_code, dbTableName):
    for i in range(len(company)):
        for j in range(len(site_code)):
            for p in range(len(channel)):
                while True:
                    try:
                        stackTodb(dataCaller(company[i], start_date, end_date, site_code[j], channel[p]), dbTableName)
                
                    except urllib.error.HTTPError:
                        print('No Matching Data : {company} X {site_code} X {channel}'.format(company = company[i], site_code = site_code[j], channel = channel[p]))

                    break

def SW_Traffic(domain, start_date, end_date, site_code, dbTableName):
    for i in range(len(domain)):
        for j in range(len(site_code)):
            while True:
                try:
                    stackTodb(dataCallerTraffic(domain[i], start_date, end_date, site_code[j]), dbTableName)
            
                except urllib.error.HTTPError:
                    print('No Matching Data : {domain} X {site_code}'.format(domain = domain[i], site_code = site_code[j]))

                break

def SW_BounceRate(domain, start_date, end_date, site_code, dbTableName):
    for i in range(len(domain)):
        for j in range(len(site_code)):
            while True:
                try:
                    stackTodb(dataCallerBR(domain[i], start_date, end_date, site_code[j]), dbTableName)
            
                except urllib.error.HTTPError:
                    print('No Matching Data : {domain} X {site_code}'.format(domain = domain[i], site_code = site_code[j]))

                break


def SW_MobileChannel(domain, start_date, end_date, site_code, dbTableName):
    for i in range(len(domain)):
        for j in range(len(site_code)):
            while True:
                try:
                    stackTodb(dataCallerMobileChannel(domain[i], start_date, end_date, site_code[j]), dbTableName)
            
                except urllib.error.HTTPError:
                    print('No Matching Data : {domain} X {site_code}'.format(domain = domain[i], site_code = site_code[j]))

                break


# if __name__ == "__main__":

#     # company = ['apple', 'samsung']
#     # start_date = '2021-05'
#     # end_date = '2021-09'
#     # site_code = ['uk', 'us']
#     # channel = ['total', 'direct', 'mail']
#     # dbTableName = 'tb_conversion_test'

#     # SW_Conversion(company, channel, start_date, end_date, site_code, dbTableName)

# # visit
#     domain = ['apple', 'samsung']
#     start_date = '2021-05'
#     end_date = '2021-06'
#     site_code = ['world']
#     dbTableName = 'tb_conversion_traffic_v2'

#     SW_Traffic(domain, start_date, end_date, site_code, dbTableName)

# # Bounce rate

#     # domain = ['apple', 'samsung']
#     # start_date = '2021-05'
#     # end_date = '2021-06'
#     # site_code = ['uk', 'us']
#     # dbTableName = 'tb_conversion_br_v2'

#     # SW_BounceRate(domain, start_date, end_date, site_code, dbTableName)


# # Bounce rate

    # domain = ['apple', 'samsung']
    # start_date = '2021-05'
    # end_date = '2021-07'
    # site_code = ['uk', 'us']
    # dbTableName = 'tb_conversion_mobile_v3'

    # SW_MobileChannel(domain, start_date, end_date, site_code, dbTableName)


    # domain = "apple.com"
    # api_key = '37db97c3c6de4c0ebc245fffde9258a0'
    # start_date = '2020-01'
    # end_date = '2020-03'
    # site_code = "us"
    # url = 'https://api.similarweb.com/v1/website/{domain}/traffic-sources/mobile-overview-share?api_key={api_key}&start_date={start_date}&end_date={end_date}&country={site_code}&granularity=monthly&main_domain_only=false&format=json'.format(domain = domain, api_key = api_key, start_date = start_date, end_date = end_date, site_code = site_code)

    # response = urllib.request.urlopen(url)
    # response_message = response.read().decode('utf8')

    # # p = json.loads(response_message)['visits'][domain]
    # a = pd.DataFrame(json.loads(response_message)['visits'][domain])
    # # b = a.transpose()
    # # p = a['source_type'].loc[0]
    # # for i in range(5):
    # #     print(p)

    # # b = a['visits']
    # # p = a['visits'].loc[0]
    # # print(pd.DataFrame(p))

    # # df3 = pd.DataFrame(columns=['source', 'date', 'visits'])

    # df3 = []
    # for j in range(len(a['visits'])):
    #     df = a['visits'].loc[j]
    #     df2 = pd.DataFrame(df)
    #     df2.insert(0, 'source', a['source_type'].loc[j], True)
    #     p = df2.to_dict('records')
    #     for i in range(len(p)):
    #         df3.append(p[i])
    
    # print(pd.DataFrame(df3))



    # for i in range(2):
    #     df3.remove