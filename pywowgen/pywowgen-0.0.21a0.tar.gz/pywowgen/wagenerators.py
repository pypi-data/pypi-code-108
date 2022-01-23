"""
This is the "wagenerators" module.
"""
import os
import json
from PIL import Image, ImageDraw, ImageFont
import io
from pathlib import Path
from pywowgen.wamap import wamap
import time
from textwrap import wrap
import logging

class wamapgenerator:
    def __init__(self):
        self.genmaps = []  # maps of type wamap
        self.genresources = []  # generated resources binary file data with relative file paths/names
        self.indexes = []  # indexes of type index
        self.config = None
        self.templates = []  # rel path templates used in this generator

    def __getresource__(self, resource, resourcetype):
        # returns the full filepath from a given resource out of all configured indexes / resource folders
        res_found = None

        for index in self.indexes:
            logging.debug(
                'trying to get {resource} of type {resourcetype} in {index.name} with path {index.sourcepath}')
            res_found = index.find_resource_path_string(resource, resourcetype)
        if res_found:
            return res_found
        else:
            raise ValueError('did not find {resource} of type {resourcetype} ')

    def __generate__(self):
        """overload with specific generating code"""

        # create a map object
        genmap = wamap('will-be-filename')

        # outputs
        self.genresources = [{'data': io.BytesIO(), 'path': '.'}]
        self.genmaps = [{'data': genmap, 'path': '.'}]
        return self.genmaps, self.genresources

    def addindex(self, index):
        self.indexes.append(index)

    def configure(self, config):
        self.config = config

    def maps(self):
        """returns a list of generated maps"""
        if len(self.genmaps) == 0:
            self.genmaps, self.genresources = self.__generate__()
        return self.genmaps

    def dumpsl(self):
        """returns a list of generated maps json"""
        ml = []
        for mm in self.maps():
            ml.append(mm['data'].dumps())
        return ml

    def resources(self):
        """list of generated resources"""
        if len(self.genresources) == 0:
            self.genmaps, self.genresources = self.__generate__()
        return self.genresources

    def find_resource_path_string(self, resource):
        """returns a filepath as string if the given resource is found, or return False"""
        if len(self.genresources) == 0:
            self.genmaps, self.genresources = self.__generate__()

        found = False

        for rtv in self.genresources:
            # converting to Path() for comparison, because of file paths like / or \
            if Path(resource) == Path(rtv['path']):
                found = True

        return found


class wacopypastegenerator(wamapgenerator):
    """creates ..."""

    def __generate__(self):

        if self.config:
            # set by config
            try:
                self.name = self.config['name']
                self.templates.extend(self.config['templates'])
            except KeyError:
                return None, None

            for page in self.config['pages']:
                # img = generate_image(page)
                # if img:
                #     self.genresources.append(img)
                #
                # mp = apply_template(page['previous'], page['id'], page['next'], 'https://cccwi.de', self.templates[0])
                # if mp:
                #     self.genmaps.append(mp)
                pass

            return self.genmaps, self.genresources
        else:
            return None, None


class waelevator(wamapgenerator):
    """creates an elevator"""

    def __generate__(self):

        def generate_image(mynote, path_name_prefix='generated/stickytext'):
            myfontfile = self.__getresource__('fonts/european_teletext/EuropeanTeletext.ttf', 'fonts')
            if myfontfile:
                font = ImageFont.truetype(myfontfile, 12)
                my_image = Image.new('RGBA', (128, 128), (255, 0, 255, 0))
                img_draw = ImageDraw.Draw(my_image)
                try:
                    img_draw.text((32, 32), '{}'.format(mynote['info_8char_1'][0:8]), fill='#061a1f', font=font)
                    img_draw.text((32, 52), '{}'.format(mynote['info_8char_2'][0:8]), fill='#061a1f', font=font)
                    img_draw.text((32, 72), '{}'.format(mynote['info_8char_3'][0:8]), fill='#061a1f', font=font)
                except KeyError:
                    nt = '...  ...'
                    img_draw.text((32, 32), '{}'.format(nt[0:8]), fill='#061a1f', font=font)
                    img_draw.text((32, 52), '{}'.format(nt[0:8]), fill='#061a1f', font=font)
                    img_draw.text((32, 72), '{}'.format(nt[0:8]), fill='#061a1f', font=font)

                # files bytes object
                imgstore = io.BytesIO()
                my_image.save(imgstore, format='PNG')

                imgname = os.path.join('{path_name_prefix}{mynote["stage"]}.png')
                return {'data': imgstore, 'path': imgname}
            else:
                return None

        def generate_map(levels, template, path_name_prefix='generated/elevator'):
            # load template and edit
            mytemplatefile = self.__getresource__(template, 'templates')

            if mytemplatefile:
                fObj = open(os.path.abspath(mytemplatefile), encoding='utf-8')
                fi = json.load(fObj)
                for level in levels:
                    if level['enabled']:
                        # make relevant layers visible and update links
                        for layer in fi['layers']:
                            # activate level exit
                            if layer['name'].startswith('level_exit') and layer['name'].split('_')[-1] == level[
                                'stage']:
                                layer['visible'] = True
                                for lproperty in layer['properties']:
                                    if lproperty['name'] == 'exitUrl':
                                        lproperty['value'] = level['target']
                            # activate audio play zone
                            if layer['name'].startswith('level_switch') and layer['name'].split('_')[-1] == level[
                                'stage']:
                                layer['visible'] = True
                                for lproperty in layer['properties']:
                                    if lproperty['name'] == 'playAudio':
                                        try:
                                            lproperty['value'] = level['audio']
                                        except KeyError:
                                            # todo: set a
                                            pass

                            # make sticky notes visible
                            if layer['name'].startswith('level_note') and layer['name'].split('_')[-1] == level[
                                'stage']:
                                layer['visible'] = True

                            if layer['name'].startswith('level_text') and layer['name'].split('_')[-1] == level[
                                'stage']:
                                layer['visible'] = True

                            # switch on light
                            if layer['name'].startswith('level_bg') and layer['name'].split('_')[-1] == level['stage']:
                                layer['visible'] = True
            else:
                raise ValueError('not a proper template file {template} in {self.name} , or template not found')
            # remove invisible layers
            idxl = []
            for index, layer in enumerate(fi['layers']):
                if not layer['visible']:
                    idxl.append(layer)
            for idx in idxl:
                fi['layers'].remove(idx)

            # todo: remove unused tilesets

            # create map object
            elvmap = wamap('elevator')
            elvmap.map = fi

            return {'data': elvmap, 'path': '{}.json'.format(path_name_prefix)}

        if self.config:
            # set by config
            try:
                self.name = self.config['name']
                self.templates.extend(self.config['templates'])
            except KeyError:
                return None, None

            for level in self.config['pages']:
                # generate sticky note text
                img = generate_image(level, path_name_prefix=self.config['gen_res_prefix'])
                if img:
                    self.genresources.append(img)

            # generate map
            mp = generate_map(self.config['pages'], self.templates[0], path_name_prefix=self.config['gen_map_prefix'])
            if mp:
                self.genmaps.append(mp)

        return self.genmaps, self.genresources


class wavideotext(wamapgenerator):
    """creates a videotext"""

    def __generate__(self):

        def apply_template(previous, id, next, url, template, map_name_prefix='videotext',
                           res_name_prefix='generated/videotext'):
            # load template and edit
            mytemplatefile = self.__getresource__(template, 'templates')
            if mytemplatefile:
                fObj = open(os.path.abspath(mytemplatefile), encoding='utf-8')
                fi = json.load(fObj)

                # update the navigation
                mapping = {
                    'exityellow': '{}{}.json'.format(map_name_prefix, '100'),  # start
                    'exitblue': '{}{}.json'.format(map_name_prefix, '101'),  # index
                    'openwebsite': url
                }

                if not str(previous).endswith('.json'):
                    mapping['exitred'] = '{}{}.json'.format(map_name_prefix, previous)
                else:
                    mapping['exitred'] = previous  # '{}{}'.format(path_name_prefix, previous)

                if not str(next).endswith('.json'):
                    mapping['exitgreen'] = '{}{}.json'.format(map_name_prefix, next)
                else:
                    mapping['exitgreen'] = next  # '{}{}'.format(path_name_prefix, next)

                for replacement in mapping:
                    for layer in fi['layers']:
                        if layer['name'] == replacement:
                            for lproperty in layer['properties']:
                                if lproperty['name'] == 'exitUrl':
                                    lproperty['value'] = mapping[replacement]
                                if lproperty['name'] == 'openWebsite':
                                    lproperty['value'] = mapping[replacement]

                # replace the tileset image which carries the text
                for tileset in fi['tilesets']:
                    if tileset['name'] == 'page1':
                        tileset['image'] = '{}{}.png'.format(res_name_prefix, id)

                # remove invisible layers
                idxl = []
                for index, layer in enumerate(fi['layers']):
                    if not layer['visible']:
                        idxl.append(layer)
                for idx in idxl:
                    fi['layers'].remove(idx)

                # todo: remove unused tilesets

                # create map object
                thismap = wamap('videotext')
                thismap.map = fi

                return {'data': thismap, 'path': '{}{}.json'.format(map_name_prefix, id)}
            else:
                return None

        def insert_newlines(string, every=64, chars=None):
            """
            like seen in https://stackoverflow.com/a/2657733
            :param string: string to edit
            :param every: int add \n every number of chars
            :param chars: list of chars ['#', ] to follow \n
            :return: string
            """

            if chars is None:
                chars = ['#']
            outs = ''

            for c in chars:
                string = string.replace(c, ' \n {}'.format(c))

            xs = string.splitlines()
            for line in xs:
                l = '\n'.join(line[i:i + every] for i in range(0, len(string), every))
                outs = outs + ' ' + l
            return outs

        def generate_image(mypage, path_name_prefix='generated/videotext'):
            myfontfile = self.__getresource__('fonts/european_teletext/EuropeanTeletext.ttf', 'fonts')

            font = ImageFont.truetype(myfontfile, 14)
            fontbig = ImageFont.truetype(myfontfile, 18)
            # image
            my_image = Image.new('RGBA', (704, 576), (0, 0, 0, 0))
            img_draw = ImageDraw.Draw(my_image)

            # Header
            img_draw.multiline_text((10, 10),
                                    '{}'.format(mypage['id']), fill='white', font=font)
            img_draw.multiline_text((250, 10),
                                    '{}'.format(mypage['title']), fill='white', font=font)
            img_draw.multiline_text((470, 10),
                                    '{}  {}'.format(mypage['date'], mypage['time']), fill='white', font=font)

            # Main Text

            # update text with newlines to fit into videotext frames ...
            newtext = insert_newlines(mypage['text'], every=56, chars=['#'])
            img_draw.multiline_text((70, 100), '{}'.format(newtext), fill='white', font=font)

            # Nav
            img_draw.multiline_text((30, 540), ' - ', fill='white', font=fontbig)
            img_draw.multiline_text((170, 540), ' + ', fill='white', font=fontbig)
            img_draw.multiline_text((320, 540), ' main ', fill='white', font=fontbig)
            img_draw.multiline_text((550, 540), ' index ', fill='white', font=fontbig)

            # files bytes object
            imgstore = io.BytesIO()
            my_image.save(imgstore, format='PNG')

            imgname = os.path.join('{path_name_prefix}{mypage["id"]}.png')
            return {'data': imgstore, 'path': imgname}

        def validvals(page, countpages, defurl='https://www.cccwi.de'):

            freshpage = {'id': None, 'title': None, 'date': None, 'time': None, 'text': None, 'previous': None,
                         'next': None, 'url': None}

            for itm in freshpage:
                if itm == 'url':
                    try:
                        freshpage[itm] = page[itm]
                    except KeyError as missingkey:
                        freshpage[itm] = defurl

                elif itm == 'previous':
                    try:
                        freshpage[itm] = page[itm]
                    except KeyError as missingkey:
                        freshpage[itm] = int(page['id']) - 1

                elif itm == 'next':
                    try:
                        freshpage[itm] = page[itm]
                    except KeyError as missingkey:
                        # if there are more pages
                        pager = countpages * 100
                        if int(page['id']) < pager:
                            freshpage[itm] = int(page['id']) + 1
                        elif int(page['id']) == pager:
                            freshpage[itm] = 100
                        else:
                            freshpage[itm] = page['id']

                else:
                    try:
                        freshpage[itm] = page[itm]
                    except KeyError as missingkey:
                        raise ValueError('missing configuration: {missingkey}')

            return freshpage

        if self.config:
            # set by config
            try:
                self.name = self.config['name']
                self.templates.extend(self.config['templates'])
            except KeyError:
                return None, None

            real_pages = []

            for page in self.config['pages']:

                page['date'] = time.strftime("%Y-%m-%d", time.gmtime())
                page['time'] = time.strftime("%H:%M:%S", time.gmtime())

                # apply page break if text is longer then count of chars
                page['readmore'] = wrap(page['text'], 1000)
                page['text'] = '{} \n ...'.format(page['readmore'][0])

                # and append pages to read more
                if len(page['readmore']) > 1:
                    tnewpages = []
                    c = 0
                    for subpage in page['readmore']:
                        if not c == 0:
                            sp = page.copy()
                            sp.pop('readmore')
                            sp['id'] = '{}{}'.format(page['id'], c)
                            # update the subpage if it is not the last
                            if c < len(page['readmore']) - 1:
                                sp['next'] = '{}{}'.format(page['id'], c + 1)
                                sp['previous'] = page['id']
                                sp['text'] = '{}{}'.format(page['readmore'][c], ' \n ...')
                            # last
                            else:
                                try:
                                    sp['previous'] = page['previous']
                                except KeyError:
                                    pass

                                try:
                                    sp['next'] = page['next']
                                except KeyError:
                                    pass

                                sp['text'] = page['readmore'][c]
                            tnewpages.append(sp)
                        c += 1

                    # append subpages to pages to be rendered
                    real_pages.extend(tnewpages)

                    # replace next link in parent page
                    page['next'] = '{}{}'.format(page['id'], 1)

                # and append pages
                real_pages.append(page)

            for page in real_pages:
                # real_pages = pages after adding page breaks

                # validate, generate values
                freshp = validvals(page, len(real_pages))

                img = generate_image(page, path_name_prefix=self.config['gen_res_prefix'])
                if img:
                    self.genresources.append(img)

                # and go!
                # mp = apply_template(page['previous'], page['id'], page['next'], page['url'], self.templates[0],
                #                     map_name_prefix=self.config['gen_map_prefix'],
                #                     res_name_prefix=self.config['gen_res_prefix'])

                mp = apply_template(freshp['previous'], freshp['id'], freshp['next'], freshp['url'], self.templates[0],
                                    map_name_prefix=self.config['gen_map_prefix'],
                                    res_name_prefix=self.config['gen_res_prefix'])

                if mp:
                    self.genmaps.append(mp)

            return self.genmaps, self.genresources
        else:
            return None


class wasidescroller(wamapgenerator):
    """creates a sidescroller"""

    def __generate__(self):

        def apply_template(previous, id, next, url, template, videotext='videotext100.json',
                           path_name_prefix='generated/sidescroller'):
            # load template and edit
            mytemplatefile = self.__getresource__(template, 'templates')
            if mytemplatefile:
                fObj = open(os.path.abspath(mytemplatefile), encoding='utf-8')
                fi = json.load(fObj)

                # update the navigation
                mapping = {
                    # 'exitleft': 'sidescroll{}.json#startright'.format(previous),
                    # 'exitright': 'sidescroll{}.json#startleft'.format(next),
                    'exitvideotext': videotext,
                    'openwebsite': url
                }

                if not str(previous).endswith('.json'):
                    mapping['exitleft'] = '{}{}.json#startright'.format(path_name_prefix, previous)
                else:
                    mapping['exitleft'] = '{}'.format(previous)

                if not str(next).endswith('.json'):
                    mapping['exitright'] = '{}{}.json#startleft'.format(path_name_prefix, next)
                else:
                    mapping['exitright'] = '{}'.format(next)

                for replacement in mapping:
                    for layer in fi['layers']:
                        if layer['name'] == replacement:
                            for lproperty in layer['properties']:
                                if lproperty['name'] == 'exitUrl':
                                    lproperty['value'] = mapping[replacement]
                                if lproperty['name'] == 'openWebsite':
                                    lproperty['value'] = mapping[replacement]

                # remove invisible layers
                idxl = []
                for index, layer in enumerate(fi['layers']):
                    if not layer['visible']:
                        idxl.append(layer)
                for idx in idxl:
                    fi['layers'].remove(idx)

                # todo: remove unused tilesets

                # create map object
                thismap = wamap('sidescroller')
                thismap.map = fi
                return {'data': thismap, 'path': '{}{}.json'.format(path_name_prefix, id)}
            else:
                return None

        if self.config:
            # set by config
            try:
                self.name = self.config['name']
                self.templates.extend(self.config['templates'])
            except KeyError:
                return None, None

            cnt_pages = len(self.config['pages'])

            for page in self.config['pages']:

                # next
                try:
                    nextpage = page['next']
                except KeyError:
                    if int(page['id']) < cnt_pages:
                        nextpage = str(int(page['id']) + 1)
                    else:
                        nextpage = str(int(page['id']))

                # previous
                try:
                    previouspage = page['next']
                except KeyError:
                    if not int(page['id']) == 1:
                        previouspage = int(page['id']) - 1
                    else:
                        previouspage = cnt_pages

                # url
                try:
                    pageurl = page['url']
                except KeyError:
                    pageurl = 'https://www.cccwi.de'

                mp = apply_template(previouspage, page['id'], nextpage, pageurl, self.templates[0],
                                    path_name_prefix=self.config['gen_map_prefix'])
                if mp:
                    self.genmaps.append(mp)

            return self.genmaps, []
        else:
            return None, None


class wamapfromtemplate(wamapgenerator):
    """creates a bunch of maps from templates"""

    # todo: replacements, edits
    #                   activate badges, if token configured or deativate if not
    #                   overwrite missing resources
    #                   change sizes (eg, when created from a blank template with only a layer setup)

    def __generate__(self):

        if self.config:
            # set by config
            try:
                self.name = self.config['name']
            except KeyError:
                return None, None

            for page in self.config['pages']:
                # load template and edit
                mytemplatefile = self.__getresource__(page['template'], 'templates')
                if mytemplatefile:

                    try:
                        fObj = open(os.path.abspath(mytemplatefile), encoding='utf-8')
                        fi = json.load(fObj)
                    except ValueError:
                        raise ValueError('can not load json file {mytemplatefile}')

                    # exchange template layer parameter values
                    try:
                        for tploption in page['layer_parameter_mapping']:
                            done = False
                            for layer in fi['layers']:
                                if layer['name'].startswith(tploption['layer_prefix']):
                                    try:
                                        for lproperty in layer['properties']:
                                            if lproperty['name'] == tploption['parameter']:
                                                lproperty['value'] = tploption['value']
                                                done = True
                                    except KeyError:
                                        pass
                            if not done:
                                pass
                    except KeyError:
                        pass
                    # init new map
                    mymap = wamap('fromTemplate')
                    mymap.map = fi

                    # add map
                    self.genmaps.append(
                        {'data': mymap, 'path': '{}{}.json'.format(self.config['gen_map_prefix'], page['id'])})
                else:
                    # can not load template
                    pass

            return self.genmaps, []
        else:
            return None, None


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
