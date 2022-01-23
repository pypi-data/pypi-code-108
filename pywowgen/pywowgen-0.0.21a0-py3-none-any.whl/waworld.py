"""
This is the "waworld" module.
"""
import os
import json
import time
from pathlib import Path
import shutil
import logging

from pywowgen.wamap import wamap
from pywowgen.wagenerators import waelevator, wavideotext, wasidescroller, wamapfromtemplate
from pywowgen.waresources import waindex
from pywowgen.remotes import git_clone


class waworld:
    """

    handles a workadventure world

    >>> tw = waworld()
    >>> tw.read( str(os.path.join( os.environ.get('WOWGEN_EXTRA'), 'wowgen.git/examples/default_pipeline.json') ) )
    True

    """

    def __init__(self):
        self.resources = []  # index objects
        self.maps_custom = []  # wamap objects, for individual maps, not from generators
        self.maps_generated = []
        self.config = {}  # world, generators and tool config
        self.messages = []  # messages from actions performed
        self.generators = []  # wamapgenerator objects
        self.generators_resources = []  # wamapgenerator resource files to be generated
        self.analysis = []  # graph suitable for cytoscape
        self.maps_resources = []  # resources needed in maps

        self.name = None
        self.path_res = None
        self.path_tmp = None
        self.path_target = None
        self.flatten_export = None
        self.zip_export = None

        self.analysis_maps = None
        self.analysis_starts = None  # all startlayers, or entry points to the maps, to be checked again

        # todo: add custom, individual maps

    def initialize(self, name=None, fullpath_target=None, fullpaths_resources=None, fullpath_tmp=None):
        try:
            self.name = name
            self.path_res = os.path.abspath(fullpaths_resources)
            self.path_tmp = os.path.abspath(fullpath_tmp)
            self.path_target = os.path.abspath(fullpath_target)
            self.flatten_export = False
            self.zip_export = False
            return True
        except Exception as err:
            return False

    def read(self, filepath):
        try:
            # optionally convert a single instance config into default config
            fObj = open(os.path.abspath(filepath), encoding='utf-8', )
            tmpconfig = json.load(fObj)
            for cfgop in tmpconfig:
                if cfgop.startswith('gen_') and type(tmpconfig[cfgop]) == dict:
                    self.config[cfgop] = [tmpconfig[cfgop]]
                else:
                    self.config[cfgop] = tmpconfig[cfgop]
            return True
        except Exception as err:
            return False

    def set(self, worldjson):
        try:
            tmpconfig = json.loads(worldjson)
            for cfgop in tmpconfig:
                if cfgop.startswith('gen_') and type(tmpconfig[cfgop]) == dict:
                    self.config[cfgop] = [tmpconfig[cfgop]]
                else:
                    self.config[cfgop] = tmpconfig[cfgop]
            return True
        except Exception as err:
            return False

    def __world_map_overwrites__(self):
        world_overwrites = []
        if self.config['config_world']['apply_world_map_overwrites']:
            try:
                world_overwrites.append({"name": "mapCopyright", "value": self.config['config_world']['mapCopyright'],
                                         "tpl_feature_type": "map_property"})
                world_overwrites.append(
                    {"name": "mapDescription", "value": self.config['config_world']['mapDescription'],
                     "tpl_feature_type": "map_property"})
                world_overwrites.append({"name": "mapLink", "value": self.config['config_world']['mapLink'],
                                         "tpl_feature_type": "map_property"})
                world_overwrites.append({"name": "mapName", "value": self.config['config_world']['mapName'],
                                         "tpl_feature_type": "map_property"})
                world_overwrites.append(
                    {"name": "script", "value": self.config['config_world']['mapDefaultExtendedApiUrl'],
                     "tpl_feature_type": "map_property"})

                world_overwrites.append(
                    {"name": "exitUrl", "target": "tpl_exit_main",
                     "value": self.config['config_world']['main_exit_url'],
                     "tpl_feature_type": "layer_property"})

                world_overwrites.append(
                    {"name": "exitUrl", "target": "tpl_exit_lobby",
                     "value": self.config['config_world']['lobby_exit_url'],
                     "tpl_feature_type": "layer_property"})

                for badge in self.config['config_world']['badges']:
                    world_overwrites.append(
                        {
                            "name": "getBadge",
                            "target": "tpl_map_badge",
                            "object": badge['name'],
                            "value": badge['value'],
                            "tpl_feature_type": "layer_object_property"
                        }
                    )
            except KeyError:
                pass
        return world_overwrites

    def __generators__(self):
        gnl = []
        for tlc in self.config:
            if str(tlc).startswith('gen_'):
                gnl.append(
                    {'generator': tlc,
                     'config': self.config[tlc],
                     })
        return gnl

    def __resources__(self):
        try:
            return self.config['config_tool']['res_paths']
        except KeyError as err:
            raise ValueError('Missing Configuration: {err}')

    def __message_add__(self, message):
        """add a message, which will be used in analysis"""
        message['timestamp'] = int(time.time())
        self.messages.append(message)
        return True

    def generate(self):
        """

        generate map objects and apply world map overrides if configured
         - from generators
         - and custom maps folder

        """

        # initialize resources
        logging.debug('initiating resource indexes')
        for rp in self.__resources__():
            # if folder is a git repo url starting with https:// and ending with .git clone it to extra dir
            if rp.startswith('https://') and rp.endswith('.git'):
                # pass
                # use the part after the last / as folder name
                fn = str(rp).split('/')[-1]
                rpt = (rp, fn, None)
                git_clone([rpt])

                # add folder to index
                path_to_res = os.path.join(os.environ.get('WOWGEN_EXTRA'), fn.strip(".git"), 'res')
                mr = waindex(fn.strip(".git"))
                mr.scan(path_to_res)
                self.resources.append(mr)
                logging.debug('added folder {fn} as index {mr.name}')

            # add it, if it's a working file path
            elif Path(rp).is_dir():
                # add folder to index
                mr = waindex('fromWorldConfig')
                mr.scan(rp)
                self.resources.append(mr)
                logging.debug('added folder {rp} as index {mr.name}')

        # custom maps
        logging.debug('applying custom maps')
        try:
            if self.config['config_world']['copy_maps_if_present']:
                for index in self.resources:
                    for custommap in index.find_custom_maps_path():
                        tm = wamap('customMap')
                        # set map to be created from json file
                        tm.read(os.path.abspath(custommap[0]))

                        # apply world map overrides if configured
                        # print('apply world map overwrites')
                        tm.update(self.__world_map_overwrites__())

                        self.messages.extend(tm.message())
                        self.maps_resources.extend(tm.resource())
                        self.maps_custom.append(tm)
        except KeyError:
            pass

        # execute configured generators
        logging.debug('executing generators')
        for generator in self.__generators__():
            if generator['generator'] == 'gen_mapfromtemplate':
                for gencfg in generator['config']:
                    genobj = wamapfromtemplate()
                    for res in self.resources:
                        genobj.addindex(res)
                    genobj.configure(gencfg)
                    self.generators.append(genobj)
            if generator['generator'] == 'gen_videotext':
                for gencfg in generator['config']:
                    genobj = wavideotext()
                    for res in self.resources:
                        genobj.addindex(res)
                    genobj.configure(gencfg)
                    self.generators.append(genobj)
            if generator['generator'] == 'gen_elevator':
                for gencfg in generator['config']:
                    genobj = waelevator()
                    for res in self.resources:
                        genobj.addindex(res)
                    genobj.configure(gencfg)
                    self.generators.append(genobj)
            if generator['generator'] == 'gen_sidescroller':
                for gencfg in generator['config']:
                    genobj = wasidescroller()
                    for res in self.resources:
                        genobj.addindex(res)
                    genobj.configure(gencfg)
                    self.generators.append(genobj)

        for mgenerator in self.generators:
            self.generators_resources.extend(mgenerator.resources())
            for mmap in mgenerator.maps():
                # apply world map overrides if configured
                # print(f"apply world map overwrites {mmap['data'].name}")
                mmap.update(self.__world_map_overwrites__())

                self.messages.extend(mmap['data'].message())
                self.maps_resources.extend(mmap['data'].resource())
                self.maps_generated.append(mmap['data'])

        return self.generators

    def missing_resources(self):
        """check for missing resources"""
        mr = []
        found = False
        for neededres in self.maps_resources:
            for generator in self.generators:
                if generator.find_resource_path_string(neededres['file']):
                    found = True
                else:
                    for index in self.resources:
                        if index.find_resource_path_string(neededres['file']):
                            found = True
            if not found:
                mr.append(neededres)
        return mr

    def save(self):
        """execute generators, save maps and resources"""

        # create tmp directory, clean if configured or just ise if exists
        # try:
        #     os.makedirs(os.path.split(os.path.abspath(Path(self.config['config_tool']['tmp_path'])))[0], exist_ok=True)
        #     #     os.makedirs(os.path.split(os.path.abspath(Path(self.config['config_tool']['tmp_path'])))[0], exist_ok=True)
        # except PermissionError:
        #     # cleaning
        if self.config['config_tool']['clean_target_directories']:
            try:
                shutil.rmtree(Path(self.config['config_tool']['tmp_path']))
                os.makedirs(os.path.split(os.path.abspath(Path(self.config['config_tool']['tmp_path'])))[0],
                            exist_ok=True)
            except FileNotFoundError:
                os.makedirs(os.path.split(os.path.abspath(Path(self.config['config_tool']['tmp_path'])))[0],
                            exist_ok=True)
        else:
            os.makedirs(os.path.split(os.path.abspath(Path(self.config['config_tool']['tmp_path'])))[0])
        # final world, not used....
        # fnp = os.path.join(Path(self.config['config_tool']['final_path']),
        #                    self.config['config_world']['world_name'])
        # os.makedirs(os.path.split(os.path.abspath(fnp))[0], exist_ok=True)

        # needed resources from all maps
        for myitem in self.maps_resources:
            # copy file if in one of the worlds indexes
            for index in self.resources:
                found = False
                for chk in ['udp:', 'http:', 'ftp:', 'https:']:
                    if chk in myitem['file']:
                        found = True
                if not found:
                    index.copy(myitem['file'],
                               os.path.join(Path(self.config['config_tool']['tmp_path']), Path(myitem['file'])))

        # copy of additional maps
        custommaptarget = Path(self.config['config_tool']['tmp_path'])
        paths = os.path.split(custommaptarget)

        if len(paths) > 2:
            os.makedirs(os.path.split(custommaptarget)[0], exist_ok=True)
        else:
            os.makedirs(custommaptarget, exist_ok=True)
        for custommap in self.maps_custom:
            ffp = Path(custommap.sourcefilename)
            custommap.targetfilename = os.path.join(custommaptarget, ffp)
            custommap.write()

        # generators files
        for mygenerator in self.generators:
            # write generators map files
            for mygeneratormap in mygenerator.maps():
                ffp = Path(mygeneratormap['path'])
                target = os.path.join(Path(self.config['config_tool']['tmp_path']), ffp)
                os.makedirs(os.path.split(target)[0], exist_ok=True)
                mygeneratormap['data'].write(filepath=target)
            # write generators resource files
            for mygeneratorres in mygenerator.resources():
                nfp = os.path.join(Path(self.config['config_tool']['tmp_path']), Path(mygeneratorres['path']))
                os.makedirs(os.path.split(nfp)[0], exist_ok=True)
                with open(os.path.abspath(nfp), "w+b") as write_file:
                    write_file.write(mygeneratorres['data'].getbuffer())

        # Merging Metadata
        for fn in ['LICENSE', 'COPYRIGHT', 'AUTHORS']:
            target = os.path.join(Path(self.config['config_tool']['tmp_path']), fn)
            os.makedirs(os.path.split(target)[0], exist_ok=True)
            with open(os.path.abspath(target), "w+") as write_file:
                write_file.write('# {fn} info by subfolder\n')
                for index in self.resources:
                    for metadatfile in index.find_metadata_files_path():
                        try:
                            if metadatfile.endswith(fn):
                                mdf = index.read(metadatfile)
                                write_file.writelines(mdf)
                        except UnicodeDecodeError:
                            pass
                            print('Cant Read Metadata File: {metadatfile}')
        return self.config['config_tool']['tmp_path']

    def check_maps(self, sourcepath=None):

        self.analysis_maps = []
        self.analysis_starts = []  # all startlayers, or entry points to the maps, to be checked again

        if not sourcepath:
            sourcepath = os.path.abspath(Path(self.config['config_tool']['tmp_path']))

        def get_maps(sourcepath):
            p = []
            all_files = os.walk(sourcepath)
            for directory in all_files:
                dn = directory[0]
                dirfiles = directory[2]
                for file in dirfiles:
                    filefullpath = os.path.join(dn, file)  # os.path.abspath('{}/{}'.format(dir, file))
                    if file.endswith('.json'):
                        p.append(filefullpath)
            return p

        maps = get_maps(sourcepath)

        # init maps and get the maps entrypoints
        for mymap in maps:
            tm = wamap('customMap')

            # set map to be created from json file
            tm.read(os.path.abspath(mymap))

            self.analysis_maps.append(tm)
            self.analysis_starts.append(tm.__wastart__())

            # analyze the map, append results to world analysis graph
            nodes, links = tm.analyze(possible_entrypoints=self.analysis_starts)
            self.analysis.extend(nodes)
            self.analysis.extend(links)

        return self.analysis

    def dumps(self):
        return json.dumps(self.config, indent=4)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
