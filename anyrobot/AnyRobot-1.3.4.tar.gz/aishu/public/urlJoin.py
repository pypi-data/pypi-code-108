
from urllib.parse import urljoin
from aishu import setting

def url(pathUrl):
    return urljoin('{http}://{ip}:{port}'.format(http='http',ip=setting.host,port='80'),pathUrl)