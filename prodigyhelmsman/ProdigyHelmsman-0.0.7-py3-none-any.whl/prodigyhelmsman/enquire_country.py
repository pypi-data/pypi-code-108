import requests
import argparse


def read_args():
    """
    Read the commandline arguments where
    1: http://localhost:8000
    2: http://www.prodigyhelmsman.co.za
    
    :return: url to hit
    """
    arg_parser = argparse.ArgumentParser(description="Get configuration parameters")
    arg_parser.add_argument(
        "url",
        choices = ["1", "2"],
        # nargs="+",
        help="Url to connect to:\n1 = local\n2 = www.prodigyhelmsman.co.za",
        default = "1"
    )
    args = arg_parser.parse_args()
    url_option = args.url
    def_url = ''
    if url_option == "1":
        def_url = 'http://localhost:8000/api/'
    elif url_option == "2":
        def_url = 'http://www.prodigyhelmsman.co.za/api/'
    # else:
    #     print('Please use 1
    return def_url


class EndpointDescriptor:
    get_ep = {
        'lc': {
            'method': "_list_countries_method",
            'description': 'list_countries',
            'query': None
        },
        'lc_lsl': {
            'method': '_list_countries_method',
            'description': 'list_countries filter currency=LSL (Lesotho loti)',
            'query': 'curr_iso=LSL'
        },
        'fc_zaf': {
            'method': '_find_country_method',
            'description': 'find_country filter cca3 = ZAF',
            'query': "cca=ZAF",
        },
        'fc_za':  {
            'method': '_find_country_method',
            'description': 'find_country filter cca3 = ZA',
            'query': 'cca=ZA'
        },
    }
    post_ep = {
        'del': {
            'method'     : '_delete_country_method',
            'description': 'delete_country where cca = DER',
            'data'      : {'cca': 'DER'}
        },
        'add': {
            'method'     : '_add_country_method',
            'description': 'add_country where cca2 = RU, cca3 = RUS, name_common = Russia',
            'data'       : {'cca2' : 'RU', 'cca3' : 'RUS', 'name_common' : 'Russia'}
        },
        'add': {
            'method'     : '_add_country_method',
            'description': 'add_country where cca2 = DE, cca3 = DER, name_common = Germany',
            'data'       : {'cca2': 'DE', 'cca3': 'DER', 'name_common': 'Germany'}
        },
    }


class ApiDemo:
    def __init__(self, p_url):
        self.url = p_url

    def do_gets(self, p_method, p_desc, p_query, p_header = True):
        if p_query:
            query = "?" + ep["query"]
        else:
            query = ''
        call = f'{self.url}{p_method}{query}'
        response = requests.get(call)
        ret_data = response.json()
        if p_header:
            self.display_header(p_method, p_desc)
            print(f'Status\t\t\t{response.status_code}')
        return ret_data

    def do_posts(self, p_method, p_desc, p_data, p_header = True):
        call = f'{self.url}{p_method}'
        response = requests.post(call, p_data)
        ret_data = response.json()
        if p_header:
            self.display_header(p_method, p_desc)
            print(f'Status\t\t\t{response.status_code}')
        return ret_data

    @staticmethod
    def display_data(p_ret_data):
        if isinstance(p_ret_data, list):
            for rec in p_ret_data:
                print(rec)
        elif isinstance(p_ret_data, dict):
            print(p_ret_data)
        print()

    def display_header(self, p_method, p_desc):
        print(f'API End Point:\t{p_desc}')
        print(f'Method:\t\t\t{p_method}')
        print(f'Url:\t\t\t{self.url}')


if __name__ == '__main__':
    url = read_args()
    endpoint_desc = EndpointDescriptor()
    api_demo = ApiDemo(url)
    for endpoint in EndpointDescriptor().get_ep:
        ep = EndpointDescriptor().get_ep[endpoint]
        res = api_demo.do_gets(ep['method'], ep['description'], ep['query'])
        api_demo.display_data(res)


    for endpoint in EndpointDescriptor().post_ep:
        ep = EndpointDescriptor().get_ep['lc']
        res = api_demo.do_gets(ep['method'], ep['description'], ep['query'], p_header = False)
        api_demo.display_data(res)

        ep = EndpointDescriptor().post_ep[endpoint]
        res = api_demo.do_posts(ep['method'], ep['description'], ep['data'])

        ep = EndpointDescriptor().get_ep['lc']
        res = api_demo.do_gets(ep['method'], ep['description'], ep['query'], p_header = False)
        api_demo.display_data(res)
    pass
