# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

import os
import json

from PySide2.QtWebEngineWidgets import QWebEngineView

from PySide2 import QtCore, QtWidgets, QtWebEngineWidgets, QtWebChannel


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loadFinished.connect(self.onLoadFinished)

    @QtCore.Slot(bool)
    def onLoadFinished(self, ok):
        if ok:
            self.load_qwebchannel()
            self.run_scripts_on_load()

    def load_qwebchannel(self):
        file = QtCore.QFile(":/qtwebchannel/qwebchannel.js")
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            self.runJavaScript(content.data().decode())
        if self.webChannel() is None:
            channel = QtWebChannel.QWebChannel(self)
            self.setWebChannel(channel)

    def add_objects(self, objects, signals=''):
        if self.webChannel() is not None:
            initial_script = ""
            end_script = ""
            self.webChannel().registerObjects(objects)
            for name, obj in objects.items():
                initial_script += "var {helper};".format(helper=name)
                end_script += "{helper} = channel.objects.{helper};".format(helper=name)
            js = initial_script + \
                 "new QWebChannel(qt.webChannelTransport, function (channel) {" + \
                 end_script + \
                 signals + \
                 "} );"
            self.runJavaScript(js)

    def run_scripts_on_load(self):
        pass


class GeoJSONWebPageView(WebEnginePage):
    export = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}

    def run_scripts_on_load(self):
        api_key = os.environ.get('MAPBOX_API_KEY', '')
        js = f'var token = "{api_key}";'
        js += '''
            var map = L.map('mapid').setView([0, 0], 2);

            L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
                maxZoom: 18,
                id: 'mapbox.streets',
                accessToken: token
            }).addTo(map);
        '''

        for d in self.data.values():
            js += '''
                  var geojsonFeature = ''' + json.dumps(d) + ''';

                  L.geoJSON(geojsonFeature).addTo(map);
                  '''
        self.runJavaScript(js)

    @QtCore.Slot(str)
    def on_clicked(self, html):
        self.export.emit(html)
        #print("clicked on startButton", html)


class GraphJSWebPageView(WebEnginePage):
    export = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super(GraphJSWebPageView, self).__init__(*args, **kwargs)

    def run_scripts_on_load(self):
        pass
        #self.add_objects({"jshelper": self})
        # js = '''
        #     var button = document.getElementById("startButton");
        #     button.addEventListener("click", function(){ jshelper.on_clicked(editor.getHtml()) });
        # '''
        # self.runJavaScript(js)

    @QtCore.Slot(str)
    def on_clicked(self, html):
        self.export.emit(html)
        #print("clicked on startButton", html)


class UpdatableWebPageView(WebEnginePage):
    updateHtml = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super(UpdatableWebPageView, self).__init__(*args, **kwargs)

    def run_scripts_on_load(self):
        signals = '''
            channel.objects.jshelper.updateHtml.connect(function(html) {
                document.getElementById("preview").innerHTML = html;
            });
        '''
        self.add_objects({"jshelper": self}, signals)
        js = '''
            var button = document.getElementById("startButton");
            button.addEventListener("click", function(){ jshelper.on_clicked(editor.getHtml()) });
        '''
        self.runJavaScript(js)

    @QtCore.Slot(str)
    def update_html(self, html):
        self.updateHtml.emit(html)
