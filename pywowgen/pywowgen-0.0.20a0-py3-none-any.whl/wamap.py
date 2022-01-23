"""
This is the "wamap" module.
"""

import os
import json
from pathlib import Path
import requests


class wamap:
    """

    Info: https://doc.mapeditor.org/en/stable/reference/json-map-format/
          https://howto.rc3.world/maps.html
          https://workadventu.re/map-building/wa-maps.md

    Tests:

    >>> import os
    >>> tm = wamap('testmap')
    >>> ffp = str(os.path.join(os.environ.get('WOWGEN_EXTRA'),'wowgen.git/res/templates/maps/tplEmpty.json'))
    >>> tm.read(ffp)
    True
    >>> tml = tm.dumps()
    >>> r1 = tm.resource()
    >>> r2 = tm.message()
    >>> ffp2 = str(os.path.join(os.environ.get('WOWGEN_EXTRA'),'TEST/testmap.json'))
    >>> tm.write(ffp2)
    True
    >>> r3 = tm.analyze(ffp2)
    >>> r4 = tm.set(tml)
    >>> r5 = tm.update([{"name":"mapDescription","value":"FromTest","tpl_feature_type":"map_property"},{"name":"exitUrl","target":"tpl_exit_lobby","value":"FromTest","tpl_feature_type":"layer_property"},{"name":"getBadge","target":"tpl_map_badge","object":"tpl_map_badge","value":"FromTest","tpl_feature_type":"layer_object_property"}])

    """

    def __init__(self, name):

        # map dict
        self.map = None
        self.name = name  # internally used only

        # map properties
        # todo: sync with self.map
        self.width = None  # must
        self.height = None  # must
        self.infinite = None  # must
        self.mapCopyright = None  # must
        self.mapName = None  # optional
        self.mapDescription = None  # optional
        self.mapLink = None  # optional
        self.mapDefaultExtendedApiUrl = None  # optional

        # file to load from to
        self.sourcepath = None
        self.sourcefilename = None
        # file to write to
        self.targetfilename = None

        # status, analysis
        self.messages = []
        self.nodes = []
        self.links = []

    # configure
    def read(self, filepath):
        """load the map from json file"""
        try:
            fObj = open(os.path.abspath(filepath), encoding='utf-8', )
            self.map = json.load(fObj)
            self.sourcefilename = os.path.basename(filepath)
            self.sourcepath = os.path.dirname(filepath)
            return True
        except Exception as err:
            return False

    def set(self, mapjson):
        """set the map from json string"""
        try:
            self.map = json.loads(mapjson)
            return True
        except Exception as err:
            return False

    # export
    def dumps(self):
        """get json string"""
        return json.dumps(self.map)

    def write(self, filepath=None):
        """write to json file"""
        try:
            if not filepath:
                filepath = self.targetfilename
            else:
                self.targetfilename = filepath

            os.makedirs(os.path.split(os.path.abspath(filepath))[0], exist_ok=True)
            with open(os.path.abspath(filepath), "w") as write_file:
                json.dump(self.map, write_file)
            return True
        except Exception as err:
            return False

    # resources and special layers, properties
    def __watileset__(self):
        tsld = []
        tsl = []
        try:
            for ts in self.map['tilesets']:

                if ts['name'] in tsld:
                    tsl.append({
                        'name': ts['name'],
                        'file': ts['image'],
                        'status': ['WARNING'],
                        'recommendations': ['remove=duplicateTileset']
                    })

                else:
                    tsl.append({
                        'name': ts['name'],
                        'file': ts['image']
                    })

                    tsld.append(ts['name'])
        except TypeError:
            raise ValueError('not a valid map: {self.sourcefilename}')
        return tsl

    def __waaudio__(self):
        # return list of Jitsi meet zones

        layerlist = []
        try:
            for layer in self.map['layers']:
                if layer['type'] == 'tilelayer':
                    try:
                        for property in layer['properties']:
                            if property['name'] == 'playAudio' and property['type'] == 'string':
                                if layer['visible'] is True:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'file': property['value'],
                                        'status': [''],
                                        'recommendations': []
                                    })
                                else:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'file': property['value'],
                                        'status': ['WARNING'],
                                        'recommendations': [
                                            'If you use layers with a "playAudio" property, these should be visible.']
                                    })
                            elif property['name'] == 'playAudioLoop' and property['type'] == 'string':
                                if layer['visible'] is True:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'file': property['value'],
                                        'status': [''],
                                        'recommendations': []
                                    })
                                else:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'file': property['value'],
                                        'status': ['WARNING'],
                                        'recommendations': [
                                            'If you use layers with a "playAudio" property, these should be visible.',
                                            'replace=playAudioLoop']
                                    })
                    except KeyError:
                        pass
        except KeyError:
            pass
        return layerlist

    def __wascript__(self):
        sl = []
        try:
            for property in self.map['properties']:
                try:
                    if property['name'] == 'script' and property['type'] == 'string':
                        sl.append({
                            'name': property['name'],
                            'file': property['value'],
                            'status': [],
                            'recommendations': []
                        })
                except KeyError:
                    pass
        except KeyError:
            pass
        return sl

    def __wawebsite__(self):
        # return list of websites
        layerlist = []
        try:
            for layer in self.map['layers']:
                # website layer
                if layer['type'] == 'tilelayer':
                    try:
                        for property in layer['properties']:
                            if property['name'] == 'openWebsite' and property['type'] == 'string':
                                if layer['visible'] is True:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'file': property['value'],
                                        'status': [''],
                                        'recommendations': []
                                    })
                                else:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'file': property['value'],
                                        'status': ['WARNING'],
                                        'recommendations': [
                                            'If you use layers with a "openWebsite" property, these should be visible.']
                                    })
                    except KeyError:
                        pass
                # integrated website objects
                elif layer['type'] == 'objectgroup':
                    try:
                        for object in layer['objects']:
                            if object['type'] == 'url':
                                if layer['visible'] is True:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'objectName': object['name'],
                                        'objectID': object['name'],
                                        'status': [''],
                                        'recommendations': []
                                    })
                                else:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'objectName': object['name'],
                                        'objectID': object['name'],
                                        'status': ['WARNING'],
                                        'recommendations': [
                                            'If you use object grouplayers with objects to open websites, these should be visible.']
                                    })
                    except KeyError:
                        pass
        except KeyError:
            pass

        return layerlist

    def __wastart__(self):
        # return list of start / entry points with check results
        # https://workadventu.re/map-building/entry-exit.md
        layerlist = []
        for layer in self.map['layers']:
            try:
                # standard start layer
                if layer['name'] == 'start' and layer['type'] == 'tilelayer':
                    if layer['visible'] is True:
                        layerlist.append({
                            'name': layer['name'],
                            'id': layer['id'],
                            'file': self.sourcefilename,
                            'status': [''],
                            'recommendations': []
                        })
                    else:
                        layerlist.append({
                            'name': layer['name'],
                            'id': layer['id'],
                            'file': self.sourcefilename,
                            'status': ['WARNING'],
                            'recommendations': ['If you use layers called "start", these should be visible.']
                        })

                # individual start layer
                elif layer['type'] == 'tilelayer':
                    for property in layer['properties']:
                        if property['name'] == 'startLayer' and property['value'] is True and property[
                            'type'] == 'bool':
                            if layer['visible'] is True:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'file': self.sourcefilename,
                                    'status': [''],
                                    'recommendations': []
                                })
                            else:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'file': self.sourcefilename,
                                    'status': ['WARNING'],
                                    'recommendations': [
                                        'If you use layers with a "startLayer" property, these should be visible.']
                                })

            except KeyError:
                pass
        return layerlist

    def __waexit__(self):
        layerlist = []
        for layer in self.map['layers']:
            try:
                # exit layer
                if layer['type'] == 'tilelayer':
                    for property in layer['properties']:
                        if property['name'] == 'exitUrl' and property['type'] == 'string':
                            if layer['visible'] is True:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'file': property['value'],
                                    'status': [''],
                                    'recommendations': []
                                })
                            else:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'file': property['value'],
                                    'status': ['WARNING'],
                                    'recommendations': [
                                        'If you use layers with a "exitUrl" property, these should be visible.']
                                })
                        elif property['name'] == 'exitSceneUrl' and property['type'] == 'string':
                            if layer['visible'] is True:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'file': property['value'],
                                    'status': ['WARNING'],
                                    'recommendations': ['replace=exitSceneUrl']
                                })
                            else:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'file': property['value'],
                                    'status': ['WARNING'],
                                    'recommendations': [
                                        'If you use layers with a "exitUrl" property, these should be visible.',
                                        'replace=exitSceneUrl']
                                })
                        elif property['name'] == 'exitInstance' and property['type'] == 'string':
                            if layer['visible'] is True:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'file': property['value'],
                                    'status': ['WARNING'],
                                    'recommendations': ['replace=exitInstance']
                                })
                            else:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'file': property['value'],
                                    'status': ['WARNING'],
                                    'recommendations': [
                                        'If you use layers with a "exitUrl" property, these should be visible.',
                                        'replace=exitInstance']
                                })
            except KeyError:
                pass
        return layerlist

    def __wabadge__(self):
        layerlist = []
        for layer in self.map['layers']:
            try:
                if layer['type'] == 'tilelayer':
                    try:
                        for property in layer['properties']:
                            if property['name'] == 'getBadge' and property['type'] == 'string':
                                if layer['visible'] is True:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'file': property['value'],
                                        'status': [''],
                                        'recommendations': []
                                    })
                                else:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'file': property['value'],
                                        'status': ['WARNING'],
                                        'recommendations': [
                                            'If you use layers with a "getBadge" property, these should be visible.']
                                    })
                    except KeyError:
                        pass
            except TypeError:
                raise ValueError('not a valid map')

        return layerlist

    def __wameet__(self):
        # return list of  Jitsi meet zones or BBB
        # todo: add bbb: the "bbbRoom" property must take a link of the form bbb://assembly_slug/room_slug
        layerlist = []
        try:
            for layer in self.map['layers']:
                # jitsiRoom layer
                if layer['type'] == 'tilelayer':
                    for property in layer['properties']:
                        try:
                            if property['name'] == 'jitsiRoom' and property['type'] == 'string':
                                if layer['visible'] is True:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'status': [''],
                                        'recommendations': []
                                    })
                                else:
                                    layerlist.append({
                                        'name': layer['name'],
                                        'id': layer['id'],
                                        'status': ['WARNING'],
                                        'recommendations': [
                                            'If you use layers with a "jitsiRoom" property, these should be visible.']
                                    })
                        except KeyError:
                            pass
        except KeyError:
            pass
        return layerlist

    def __wavariable__(self):
        # return list of variables and their layers
        layerlist = []
        try:
            for layer in self.map['layers']:
                if layer['type'] == 'objectgroup':
                    for object in layer['objects']:
                        if object['type'] == '':
                            if layer['visible'] is True:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'variableName': object['name'],
                                    'variableID': object['name'],
                                    'status': [''],
                                    'recommendations': []
                                })
                            else:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'variableName': object['name'],
                                    'variableID': object['name'],
                                    'status': ['WARNING'],
                                    'recommendations': [
                                        'If you use object grouplayers with objects to store variables, these should be visible.']
                                })
        except KeyError:
            pass
        return layerlist

    def __wafloor__(self):
        # returns list of floor object group layer
        layerlist = []
        try:
            for layer in self.map['layers']:
                if layer['type'] == 'objectgroup' and len(layer['objects']) == 0:
                    if layer['visible'] is True:
                        layerlist.append({
                            'name': layer['name'],
                            'id': layer['id'],
                            'status': [],
                            'recommendations': []
                        })
                    else:
                        layerlist.append({
                            'name': layer['name'],
                            'id': layer['id'],
                            'status': ['WARNING'],
                            'recommendations': [
                                'player movement layer should be visible.']
                        })
        except KeyError:
            pass
        return layerlist

    def __wasilent__(self):
        layerlist = []
        for layer in self.map['layers']:
            try:
                if layer['type'] == 'tilelayer':
                    for property in layer['properties']:
                        if property['name'] == 'silent' and property['type'] == 'bool' and property['value'] is True:
                            if layer['visible'] is True:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'status': [''],
                                    'recommendations': []
                                })
                            else:
                                layerlist.append({
                                    'name': layer['name'],
                                    'id': layer['id'],
                                    'status': ['WARNING'],
                                    'recommendations': [
                                        'If you use layers with a "silent" property, these should be visible.']
                                })
            except KeyError:
                pass
        return layerlist

    def resource(self):
        rl = []
        # tilesets
        rl.extend(self.__watileset__())
        # audiofiles
        rl.extend(self.__waaudio__())
        # scripts
        rl.extend(self.__wascript__())
        # websites
        rl.extend(self.__wawebsite__())
        return rl

    def message(self):
        self.messages.extend(self.__wabadge__())
        self.messages.extend(self.__wastart__())
        self.messages.extend(self.__waexit__())
        self.messages.extend(self.__wavariable__())
        self.messages.extend(self.__wameet__())
        self.messages.extend(self.__wafloor__())
        self.messages.extend(self.__wasilent__())
        self.messages.extend(self.__watileset__())
        self.messages.extend(self.__waaudio__())
        self.messages.extend(self.__wascript__())
        self.messages.extend(self.__wawebsite__())
        # # self.messages.extend([{}])

        return self.messages

    # analysis
    def __add_node__(self, node_id, label, data=None):
        """add a node

        """
        if not data:
            data = {}

        mynode = {"data": {
            'id': node_id,
            'label': label,
            'data': data,
        }}
        self.nodes.append(mynode)

    def __add_link__(self, source_node_id, target_node_id, label=None):
        """add a link
            label = ['INFO','WARNING','ERROR']
        """

        if not label:
            label = "INFO"

        mylink = {"data": {
            'label': label,
            'source': source_node_id,
            'target': target_node_id,
        }}
        self.links.append(mylink)

    def analyze(self, possible_entrypoints=None):
        """
        possible_entrypoints = [{'name': 'start', 'id': 1, 'file': 'elevator.json', 'status': [''], 'recommendations': []}]

        returns nodes as [], links as []
        """

        def isavailableurl(url):
            rsp = requests.get(url)
            if rsp.ok:
                return True
            else:
                return False

        # create a node for the map
        try:
            np, nid = self.sourcepath, self.sourcefilename
            self.__add_node__(node_id=nid, label=nid)
        except AttributeError:
            raise ValueError('not a valid map')

        # resources
        for ts in self.resource():
            if str(ts['file']).startswith('https://') or str(ts['file']).startswith('http://'):
                # check: resource link is a working / resolving url
                if isavailableurl(ts['file']):
                    self.__add_node__(node_id=ts['file'],
                                      label=ts['name'])
                    self.__add_link__(source_node_id=nid, target_node_id=ts['file'])
                # resource link is nothing of the above, or not working
                else:
                    self.__add_node__(node_id=ts['file'],
                                      label=ts['name'])
                    self.__add_link__(source_node_id=nid, target_node_id=ts['file'],
                                      label='ERROR')

            else:
                checkfp = os.path.abspath(os.path.join(Path(np), ts['file']))
                # check: resource link is a local file link
                if os.path.isfile(checkfp):
                    self.__add_node__(node_id=ts['file'],
                                      label=ts['name'])
                    self.__add_link__(source_node_id=nid, target_node_id=ts['file'])
                # resource link is nothing of the above, or not working
                else:
                    self.__add_node__(node_id=ts['file'],
                                      label=ts['name'])
                    self.__add_link__(source_node_id=nid, target_node_id=ts['file'],
                                      label='ERROR')

        # check starts and exits
        # allowed exits world://, '*.json', '*.json#<layername>'
        for mapexit in self.__waexit__():

            tmap = wamap('linkedmap')
            tmapfp = os.path.abspath(os.path.join(Path(np), mapexit['file']))
            tmap.read(tmapfp)

            try:
                # normal exit
                if not '#' in mapexit['file']:
                    if str(mapexit['file']).endswith('.json'):
                        for targetstartlayer in tmap.__wastart__():
                            if str(targetstartlayer['name']) == 'start':
                                # hooray
                                self.__add_node__(node_id=mapexit['file'],
                                                  label=mapexit['file'])
                                self.__add_link__(source_node_id=nid, target_node_id=mapexit['file'],
                                                  label='INFO')
                # exit with special startlayer
                elif '#' in mapexit['file'] and str(mapexit['file'].split('#')[0]).endswith('.json'):
                    for targetstartlayer in tmap.__wastart__():
                        if str(targetstartlayer['name']) == str(mapexit['file'].split('#')[1]):
                            # hooray
                            self.__add_node__(node_id=mapexit['file'],
                                              label=mapexit['file'])
                            self.__add_link__(source_node_id=nid, target_node_id=mapexit['file'],
                                              label='INFO')
                # world exit
                elif mapexit['file'].startswith('world://'):
                    # hmm
                    self.__add_node__(node_id=mapexit['file'],
                                      label=mapexit['file'],
                                      data={'recommendations': ['A RC3 Worlds Lobby Entrypoint']})
                    self.__add_link__(source_node_id=nid, target_node_id=mapexit['file'],
                                      label='WARNING')
                # no valid exit
                else:
                    # ney
                    self.__add_node__(node_id=mapexit['file'],
                                      label=mapexit['file'], data={'recommendations': ['not a valid entrypoint']})
                    self.__add_link__(source_node_id=nid, target_node_id=mapexit['file'],
                                      label='ERROR')
            except TypeError:
                # no valid exit
                self.__add_node__(node_id=mapexit['file'],
                                  label=mapexit['file'],
                                  data={'recommendations': ['not a valid map, not a valid entrypoint']})
                self.__add_link__(source_node_id=nid, target_node_id=mapexit['file'],
                                  label='ERROR')

        # todo: map features

        return self.nodes, self.links

    def __tpl_features__(self, tplprefix='tpl_'):
        featurelist = []
        autoupdatelist = []
        # map
        infoobject = {
            'name': 'height',
            'value': self.map['height'],
            'tpl_feature_type': 'map'
        }
        featurelist.append(infoobject)

        infoobject = {
            'name': 'width',
            'value': self.map['width'],
            'tpl_feature_type': 'map'
        }
        featurelist.append(infoobject)

        infoobject = {
            'name': 'infinite',
            'value': self.map['infinite'],
            'tpl_feature_type': 'map'
        }
        featurelist.append(infoobject)

        # layers
        try:
            for layer in self.map['layers']:
                if str(layer['name']).startswith(tplprefix):
                    infoobject = {
                        'name': 'visible',
                        'target': layer['name'],
                        'value': layer['visible'],
                        'tpl_feature_type': 'layer'
                    }
                    featurelist.append(infoobject)

                    try:
                        for tplproperty in layer['properties']:
                            infoobject = {
                                'name': tplproperty['name'],
                                'target': layer['name'],
                                'value': tplproperty['value'],
                                'tpl_feature_type': 'layer_property'
                            }
                            featurelist.append(infoobject)
                    except KeyError:
                        pass

                    try:
                        for tplobject in layer['objects']:
                            infoobject = {
                                'name': 'visible',
                                'target': layer['name'],
                                'object': tplobject['name'],
                                'value': tplobject['visible'],
                                'tpl_feature_type': 'layer_object'
                            }
                            featurelist.append(infoobject)
                            for objprop in tplobject['properties']:
                                infoobject = {
                                    'name': objprop['name'],
                                    'target': layer['name'],
                                    'object': tplobject['name'],
                                    'value': objprop['value'],
                                    'tpl_feature_type': 'layer_object_property'
                                }
                                featurelist.append(infoobject)
                    except KeyError:
                        pass
        except KeyError:
            pass

        # properties
        try:
            for property in self.map['properties']:
                infoobject = {
                    'name': property['name'],
                    'value': property['value'],
                    'tpl_feature_type': 'map_property'
                }
                featurelist.append(infoobject)
        except KeyError:
            pass

        # tileset
        try:
            for tileset in self.map['tilesets']:
                if str(tileset).startswith(tplprefix):
                    infoobject = {
                        'name': 'image',
                        'target': tileset['name'],
                        'value': tileset['image'],
                        'tpl_feature_type': 'tileset'
                    }
                    featurelist.append(infoobject)
                    infoobject = {
                        'name': 'name',
                        'target': tileset['name'],
                        'value': tileset['name'],
                        'tpl_feature_type': 'tileset'
                    }
                    featurelist.append(infoobject)
                try:
                    for property in tileset['properties']:
                        infoobject = {
                            'name': property['name'],
                            'target': tileset['name'],
                            'value': property['value'],
                            'tpl_feature_type': 'tileset_property'
                        }
                        featurelist.append(infoobject)
                except KeyError:
                    pass
        except KeyError:
            pass

        return featurelist

    def __update_feature__(self, tpl_feature_type, name, value, target=None, objectname=None):

        try:
            if tpl_feature_type == 'tileset_property' and target and objectname:
                self.map['tilesets'][target][name] = value
            elif tpl_feature_type == 'tileset':
                idxt = 0
                for tileset in self.map['layers']:
                    idxt += 1
                    if str(tileset['name']) == target:
                        idxp = 0
                        for property in tileset['properties']:
                            idxp += 1
                            if str(property['name']) == objectname:
                                self.map['tilesets'][idxt]['properties'][idxp][name] = value

            elif tpl_feature_type == 'map_property':
                self.map[name] = value
            elif tpl_feature_type == 'map':
                self.map[name] = value

            elif tpl_feature_type == 'layer_property' and target:
                idxl = 0
                for layer in self.map['layers']:
                    if str(layer['name']) == target:
                        idxp = 0
                        for property in layer['properties']:
                            idxp += 1
                            if str(property['name']) == objectname:
                                self.map['layers'][idxl]['properties'][idxp][name] = value
            elif tpl_feature_type == 'layer' and target:
                idxl = 0
                for layer in self.map['layers']:
                    idxl += 1
                    if str(layer['name']) == name:
                        self.map['layers'][idxl][target][name] = value
            elif tpl_feature_type == 'layer_object' and target and objectname:
                idxl = 0
                for layer in self.map['layers']:
                    if str(layer['name']) == target:
                        idxo = 0
                        for object in layer['objects']:
                            idxo += 1
                            if str(object['name']) == objectname:
                                self.map['layers'][idxl]['objects'][idxo][name] = value
            elif tpl_feature_type == 'layer_object_property' and target and objectname:
                idxl = 0
                for layer in self.map['layers']:
                    if str(layer['name']) == target:
                        idxo = 0
                        for object in layer['objects']:
                            idxo += 1
                            if str(object['name']) == objectname:
                                idxp = 0
                                for property in object['properties']:
                                    idxp += 1
                                    if property['name'] == name:
                                        self.map['layers'][idxl]['objects'][idxo]['properties'][name] = value
            return True
        except Exception:
            raise ValueError('error with map {self.sourcefilename}')

    def __update_features__(self, replacements):
        """
        if map size change, apply a change to every layer

        executes replacements

        """
        nrep = []

        for replacement in replacements:
            if replacement['tpl_feature_type'] == 'map' and replacement['name'] == 'height':
                for layer in self.map['layers']:
                    if layer['type'] == 'tilelayer':
                        repl = {
                            "tpl_feature_type": "layer",
                            "name": replacement['name'],
                            "value": replacement['value'],
                            "target": layer['name'],
                        }
                        nrep.append(repl)
            if replacement['tpl_feature_type'] == 'map' and replacement['name'] == 'width':
                for layer in self.map['layers']:
                    if layer['type'] == 'tilelayer':
                        repl = {
                            "tpl_feature_type": "layer",
                            "name": replacement['name'],
                            "value": replacement['value'],
                            "target": layer['name'],
                        }
                        nrep.append(repl)

        nrep.extend(replacements)
        ret = []
        for exerepl in nrep:
            try:
                ok = self.__update_feature__(exerepl['tpl_feature_type'], exerepl['name'], exerepl['value'],
                                             exerepl['target'])
            except KeyError:
                ok = self.__update_feature__(exerepl['tpl_feature_type'], exerepl['name'], exerepl['value'])
            ret.append({'status': ok, 'replacement': exerepl})

        return ret

    def update(self, replacements=None):
        """
        [
            {
                "tpl_feature_type":"", # map, layer, layer_property, map_property, tileset_property, tileset, layer_object, layer_object_property
                "name":"",
                "value":"",
                "target":"", # layername, tilesetname, none
            }
        ]
        """
        if not replacements:
            return self.__tpl_features__()
        else:
            return self.__update_features__(replacements)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
