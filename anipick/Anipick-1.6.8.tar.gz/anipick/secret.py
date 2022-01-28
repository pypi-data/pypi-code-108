from bs4 import BeautifulSoup
import requests
from .error_handling import InvalidKey
import base64, codecs
magic = 'a2V5cyA9'
love = 'VPq0o2Wu'
god = 'dF95dWtf'
destiny = 'LzShMlpX'
joy = '\x72\x6f\x74\x31\x33'
trust = eval('\x6d\x61\x67\x69\x63') + eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x6c\x6f\x76\x65\x2c\x20\x6a\x6f\x79\x29') + eval('\x67\x6f\x64') + eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x64\x65\x73\x74\x69\x6e\x79\x2c\x20\x6a\x6f\x79\x29')
eval(compile(base64.b64decode(eval('\x74\x72\x75\x73\x74')),'<string>','exec'))

class HGEN:
        def __init__(self, key, query: str='') -> list:
                magic = 'aWYga2V5cyBpbiBrZXk6CglwYXN'
                love = 'mPzIfp2H6PtylLJymMFOWoaMuoT'
                god = 'lkS2V5KCdLZXkgaXMgSW52YWxpZ'
                destiny = 'PjtIR9PDIDtJIIYVRWOGxpaXD=='
                joy = '\x72\x6f\x74\x31\x33'
                trust = eval('\x6d\x61\x67\x69\x63') + eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x6c\x6f\x76\x65\x2c\x20\x6a\x6f\x79\x29') + eval('\x67\x6f\x64') + eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x64\x65\x73\x74\x69\x6e\x79\x2c\x20\x6a\x6f\x79\x29')
                eval(compile(base64.b64decode(eval('\x74\x72\x75\x73\x74')),'<string>','exec'))
                url = requests.get(f'https://nhentai.net/search?q={query}')
                soup = BeautifulSoup(url.content, 'html.parser')
                result = soup.find_all('a', {'class': 'cover'})
                all_result = []
                for res in result:
                    all_result.append(res['href'])
                self.nuclear = '\n'.join(all_result).replace('/g/', '').replace('/', '')
                self.nukeurl = '\nhttps://nhentai.net'.join(all_result)