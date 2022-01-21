#!/usr/bin/env python
# -*- coding:utf-8 -*-
import webbrowser, os
from ..base import BaseHandler
import platform

class DocsHandler(BaseHandler):
    """
    docs
    """

    def get(self):
        host = self.app_config["wsgi"]["host"]
        if "127.0.0.1" not in host and "localhost" not in host and "0.0.0.0" not in host:
            if "://" in host:
                if "www" not in host:
                    host = host.replace("://", "://docs.")
                else:
                    host = host.replace("www", "docs")
            else:
                if "www" not in host:
                    host = "docs." + host
                else:
                    host = host.replace("www", "docs")
            self.redirect(host)
        else:
            html_path = "index.html" if self.app_config.get("output","html") else "docs/build/html/index.html"
            file_path = os.path.realpath("/%s/%s/%s" % (self.app_config["ROOT"],
                                                        self.app_config["api_docs"]["docs_dir"],
                                                        html_path
                                                        ))
            if platform.system() != "Windows":
                file_path = "file://" + file_path
            webbrowser.open(file_path)




