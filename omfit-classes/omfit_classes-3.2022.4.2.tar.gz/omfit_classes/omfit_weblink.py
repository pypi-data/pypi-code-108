try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

__all__ = ['OMFITwebLink', 'openInBrowser']


class OMFITwebLink(object):
    def __init__(self, link):
        self.link = link

    def __call__(self):
        self.run()

    def run(self):
        openInBrowser(self.normalize_link())

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.normalize_link()}')"

    def __str__(self):
        return self.normalize_link()

    def __tree_repr__(self):
        return self.__str__(), []

    def __save_kw__(self):
        return {'link': str(self)}

    def normalize_link(self):
        link = self.link
        if not re.match(r'.*:////.*', link):
            link = f'http:////{link}'
        return link


def openInBrowser(url, browser=None):
    """
    Open web-page in browser

    :param url: URL to open

    :param browser: executable of the browser
    """
    import webbrowser

    if browser is None:
        browser = OMFIT['MainSettings']['SETUP']['browser']
    try:
        if browser is None or browser.lower() == 'default':
            webbrowser.open(url)
        elif '/' in browser:
            if '%s' not in browser:
                browser = browser + ' %s'
            child = subprocess.Popen(browser % "'" + url + "'", shell=True)
            sleep(1)
            if child.poll():
                raise RuntimeError()
        else:
            webbrowser.get(browser).open(url)
    except Exception:
        from omfit_classes.OMFITx import Dialog

        Dialog(
            title="Browser not set correctly",
            message="Setup your browser in\n OMFIT['MainSettings']['SETUP']['browser']\ne.g. '/usr/bin/firefox %s'\nUse 'default' for system default",
            icon='error',
            answers=['Ok'],
        )
