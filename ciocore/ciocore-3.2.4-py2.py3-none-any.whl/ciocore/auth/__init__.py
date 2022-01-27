import webbrowser
from ciocore.auth import server
import logging


def run(creds_file, base_url):
    logging.debug("Base URL is %s" % base_url)
    url =  "{}/api/oauth_jwt?redirect_uri=http://localhost:8085/index.html&scope=user&response_type=client_token".format(base_url)
    if webbrowser.open_new(url):
        server.run(port=8085, creds_file=creds_file)
    else:
        raise RuntimeError("Unable to open web browser.  Please contact Conductor support for help configuring Conductor Client")
