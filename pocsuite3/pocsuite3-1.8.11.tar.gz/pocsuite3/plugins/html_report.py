import time
import sys
import os
from pocsuite3 import __version__
from pocsuite3.api import PluginBase
from pocsuite3.api import PLUGIN_TYPE
from pocsuite3.api import logger
from pocsuite3.api import conf
from pocsuite3.api import paths
from pocsuite3.api import get_results
from pocsuite3.api import register_plugin
from pocsuite3.lib.utils.markup import page


class HtmlExport:
    def __init__(self, filename='', title='Report of []'):
        self.filename = filename
        self.title = title
        self.html = page()
        self.style = """
        html {
            position: relative;
            min-height: 100%;
        }
        body {margin-bottom: 60px;}
        .footer {
            position: absolute;
            margin: 10px 0px;
            width: 100%;
            background-color: #f5f5f5;
        }
        body > .container {
          padding: 60px 15px 0;
        }
        .container .text-muted {
          margin: 20px 0;
        }

        .footer > .container {
          padding: 20px 15px;
        }

        code {
          font-size: 80%;
        }
        """

    def _write_header(self):
        self.html.init(title=self.title,
                       charset='utf-8',
                       encoding='utf-8',
                       style=self.style,
                       metainfo={
                           'viewport': 'width=device-width, initial-scale=1, shrink-to-fit=no'},
                       css=['https://cdn.bootcss.com/bootstrap/4.0.0/css/bootstrap.min.css'],
                       script=['https://cdn.bootcss.com/jquery/3.2.1/jquery.slim.min.js',
                               'https://cdn.bootcss.com/popper.js/1.12.9/umd/popper.min.js',
                               'https://cdn.bootcss.com/bootstrap/4.0.0/js/bootstrap.min.js'
                               ]
                       )

    def _write_navbar(self, name='Target', menus={}):
        self.html.nav(class_="navbar navbar-dark bg-dark fixed-top")
        self.html.addcontent('<a class="navbar-brand" href="#">{0}</a>'.format(name))
        self.html.addcontent('<button class="navbar-toggler" type="button" data-toggle="collapse" '
                             'data-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" '
                             'aria-expanded="false" aria-label="Toggle navigation">'
                             '<span class="navbar-toggler-icon"></span></button>')
        self.html.div(class_="collapse navbar-collapse", id_="navbarNavDropdown")
        self.html.ul(class_="navbar-nav")
        for k, v in menus.items():
            self.html.addcontent('<li class="nav-item"><a class="nav-link" href="{0}">{1}</a></li>'.format(v, k))
        self.html.ul.close()
        self.html.div.close()
        self.html.nav.close()

    def _writer_footer(self):
        text = 'Report was automatically generated by pocsuite3 version {0} @ {1}</br>Command line: {2}'.format(
            __version__,
            time.strftime("%Y-%m-%d %H:%M:%S"),
            " ".join(sys.argv)
        )

        self.html.footer(class_="footer")
        self.html.div(class_="container")
        self.html.addcontent('<span class="text-muted">{0}</span>'.format(text))
        self.html.div.close()
        self.html.footer.close()
        self.html.body.close()
        self.html.html.close()

    def write_results(self, results=None):
        if results:
            self.html.addcontent('<table class="table table-striped table-bordered table-hover">'
                                 '<thead class="thead-dark"><tr>'
                                 '<th scope="col">Target</th>'
                                 '<th scope="col">PoC/Exp Name</th>'
                                 '<th scope="col">SSVID</th>'
                                 '<th scope="col">Component</th>'
                                 '<th scope="col">Version</th>'
                                 '<th scope="col">Status</th>'
                                 '</tr></thead><tbody>'
                                 )
            for result in results:
                content = (
                    '<tr>'
                    '<td><a href="{0}" target="_blank">{1}</a></td>'
                    '<td>{2}</td>'
                    '<td><a href="https://www.seebug.org/vuldb/ssvid-{3}" target="_blank">{4}</a></td>'
                    '<td>{5}</td>'
                    '<td>{6}</td>'
                    '<td><span class="badge badge-success">{7}</span></td>'
                    '</tr>'
                ) if result.status == 'success' else (
                    '<tr>'
                    '<td><a href="{0}" target="_blank">{1}</a></td>'
                    '<td>{2}</td>'
                    '<td><a href="https://www.seebug.org/vuldb/ssvid-{3}" target="_blank">{4}</a></td>'
                    '<td>{5}</td>'
                    '<td>{6}</td>'
                    '<td><span class="badge badge-secondary">{7}</span></td>'
                    '</tr>'
                )

                self.html.addcontent(content.format(result.target,
                                                    result.target,
                                                    result.poc_name,
                                                    result.vul_id,
                                                    result.vul_id,
                                                    result.app_name,
                                                    result.app_version,
                                                    result.status)
                                     )

            self.html.addcontent('</tbody></table>')

    def write_html(self, results=None):
        menus = {
            'Site': 'https://pocsuite.org',
            'Seebug': 'https://www.seebug.org',
            'Help': 'https://github.com/knownsec/pocsuite3/blob/master/docs/CODING.md',
            'Bug report': 'https://github.com/knownsec/pocsuite3/issues',
        }
        self._write_header()
        self._write_navbar(name='Pocsuite3', menus=menus)
        self.html.main(role_="main", class_='container')
        self.write_results(results)
        self.html.main.close()
        self._writer_footer()

        with open(self.filename, 'w', encoding='utf-8') as f:
            for x in self.html.content:
                try:
                    f.write("{0}\n".format(x))
                except Exception:
                    pass


class HtmlReport(PluginBase):
    category = PLUGIN_TYPE.RESULTS

    def init(self):
        debug_msg = "[PLUGIN] html_report plugin init..."
        logger.debug(debug_msg)

    def start(self):
        # TODO
        # Generate html report
        filename = "pocsuite_{0}.html".format(time.strftime("%Y%m%d_%H%M%S"))
        filename = os.path.join(paths.POCSUITE_OUTPUT_PATH, filename)
        if conf.url:
            title = "Report of {0}".format(repr(conf.url))
        elif conf.dork:
            title = "Report of [{0}]".format(conf.dork)
        else:
            title = "Report of [{0}]".format('Plugin imported targets')
        html_export = HtmlExport(filename=filename, title=title)
        results = get_results()
        if results:
            results = sorted(results, key=lambda r: r.status, reverse=True)
        html_export.write_html(results)

        info_msg = '[PLUGIN] generate html report at {0}'.format(filename)
        logger.info(info_msg)


register_plugin(HtmlReport)
