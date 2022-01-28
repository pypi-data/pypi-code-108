#!/usr/bin/env python3
import logging
import secrets
import threading
import typing
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

receiver_html = r"""
<html><head><noscript><style>p{ display: none; }</style></noscript></head>
<body style="margin-left: 30%; margin-top: 10%; background: rgb(233, 233, 45); color: white;">
<div style="font-size: 256px;">
    <noscript>JavaScript Required</noscript>
    <p>:|</p>
    <form id="token_form" hidden="" method="POST" action="/" enctype="application/x-www-form-urlencoded">
        <input type="text" id="token_string" name="token_string">
    </form>
    <script>
    window.onload = function(){
        if (document.location.hash){
            document.forms.token_form.elements.token_string.value = document.location.hash.slice(1);
            document.forms.token_form.submit();
        }
    };
    </script>
</div></body></html>
""".encode('utf-8')

accepted_html = r"""
<html><body style="margin-left: 30%; margin-top: 10%; background: rgb(89, 174, 88); color: white;"><div>
    <p style="font-size: 256px;">;)</p>
    <script>setTimeout("window.close()",5000)</script>
</div></body></html>
""".encode('utf-8')

rejected_html = r"""
<html><body style="margin-left: 30%; margin-top: 10%; background: rgb(217, 33, 4); color: white;"><div>
    <p style="font-size: 256px;">:(</p>
    <script>setTimeout("window.close()",5000)</script>
</div></body></html>
""".encode('utf-8')


def build_oauth_url(authorize_url: str, oauth_params: dict):
    """
    Backup function for generating an OAuth URL to display to the user in case the listener fails
    :param authorize_url: authorization url
    :param oauth_params: auth arguments:
        client_id, etc. scope should be a single space separated string
    :return: str, full oauth validation URL
    """
    return ''.join([authorize_url, '?' if authorize_url[-1] != '?' else '', urllib.parse.urlencode(oauth_params)])


def get_oauth_code(bind_config: typing.Tuple[str, int], authorize_url: str, oauth_params: dict,
                   open_browser: bool = True, url_callback: typing.Callable[[str], None] = None, timeout: float = None):
    """
    Boot HTTP server, opens browser, and waits for a response. Raises if we can't load the http server
    :param bind_config: (address, port) to bind the listener to
    :param authorize_url: authorization url
    :param oauth_params: auth arguments:
        client_id, etc. scope should be a single space separated string
        If state isn't provided, one will be generated and written back
    :param open_browser: Try to open the browser to the authentication url
    :param url_callback: Function that runs after starting the http listener but before opening the browser.
    :param timeout: Maximum wait time in seconds
    :returns: dict containing oauth response, or raises TimeoutError
    """
    response = {}
    callback = response.update
    # I'd love to hook this to httpd._shutdown_request or whatever
    #  but I don't want to dig into HTTPServer in this project
    response_recorded = threading.Event()

    if 'state' not in oauth_params:
        oauth_params['state'] = secrets.token_urlsafe(16)
    state = oauth_params['state']

    # Wish I could pass this to the caller but I don't want to call the user callback until the listener is up
    url = build_oauth_url(authorize_url, oauth_params)

    # Looks like this is instantiated per incoming request >:C
    # There's really not a good way to get data out of this thing, so we gotta scope it
    class TokenReceiver(BaseHTTPRequestHandler):
        def __set_headers(self, code=200, content_length=None):
            self.send_response(code)
            self.send_header("Content-type", "text/html")
            if content_length:
                self.send_header("Content-Length", content_length)
            self.end_headers()

        def do_POST(self):
            if not response_recorded.is_set():
                logging.info('Received response from browser')
                form_resp = self.rfile.read(int(self.headers['Content-Length'], 0)).decode('utf-8')
                parsed_resp = {k: v[0] for k, v in
                               urllib.parse.parse_qs(urllib.parse.parse_qs(form_resp)['token_string'][0]).items()}
                # TODO: check for empty response??
                if 'state' not in parsed_resp or parsed_resp['state'] != state:
                    self.__state_crash()
                else:
                    logging.info('Response looks good')
                    self.__set_headers(content_length=len(accepted_html))
                    self.wfile.write(accepted_html)
                    callback(parsed_resp)
                    response_recorded.set()
            else:
                # Shut
                self.__set_headers(409)

        def __state_crash(self):
            # UH-OH. Alternatively they just loaded localhost or something. oops.
            self.__set_headers(content_length=len(rejected_html))
            self.wfile.write(rejected_html)
            self.wfile.flush()  # Flush because we're goin down
            msg = 'Mismatched OAuth state, your connection may be compromised!'
            logging.critical(msg)
            raise RuntimeError(msg)

        def do_GET(self):
            if not response_recorded.is_set():
                logging.info('Received response from browser')
                query_response = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                if not query_response:
                    logging.info('Empty response, may be a masked response')
                    # Twitch sends the token as a fragment, which we didn't get
                    self.__set_headers(content_length=len(receiver_html))
                    self.wfile.write(receiver_html)
                elif 'state' not in query_response or query_response['state'] != state:
                    self.__state_crash()
                else:
                    logging.info('Response looks good')
                    self.__set_headers(content_length=len(accepted_html))
                    self.wfile.write(accepted_html)
                    callback(query_response)
                    response_recorded.set()
            else:
                # Shut
                self.__set_headers(409)

        def do_HEAD(self):
            self.__set_headers()

    logging.info('Booting HTTP server')
    try:
        httpd = HTTPServer(bind_config, TokenReceiver)
    except Exception as err:
        logging.critical(f'Error launching HTTP listener: {err}')
        raise
    try:
        httpd_thread = threading.Thread(target=httpd.serve_forever, name='oauth_http_worker_', daemon=True)
        httpd_thread.start()
    except Exception as err:
        logging.critical(f'Error launching HTTP worker: {err}')
        httpd.shutdown()
        httpd.server_close()
        raise

    url_callback(url)

    if open_browser:
        logging.info(f'Opening browser to {url}')
        webbrowser.open(url, new=2, autoraise=True)

    response_recorded.wait(timeout)

    logging.info('Server shutdown')
    httpd.shutdown()
    httpd.server_close()

    if response_recorded.is_set():
        return response
    else:
        raise TimeoutError('OAuth response not received in time')
