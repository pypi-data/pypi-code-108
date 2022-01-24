from chibi_command import Command


class DD( Command ):
    command = 'dd'
    kw_format = "{key}={value}"
    kw = { 'bs': '1M', 'status': 'progress' }
    captive = False


dd = DD()
