"""
    This is the "helpers" module

    check paths and envs, data files
    >>> a, b, c, d = prepare_paths()
    >>> print(True if len(os.environ.get('WOWGEN_EXTRA')) > 0 else False)
    True
    >>> do_test()

"""
import os
import logging
import shutil
from pathlib import Path
import tempfile
import doctest

import pywowgen.wamap as wamap
import pywowgen.waresources as waresources
import pywowgen.wagenerators as wagenerators
import pywowgen.waworld as waworld
import pywowgen.waapi as waapi
import pywowgen.remotes as remotes


def run_world_gen(configfile, respath, tmppath, finpath):
    # init new world
    logging.info('init world')
    apiworld = waworld.waworld()
    apiworld.read(configfile)

    #
    try:
        for rp in apiworld.config['config_tool']['res_paths']:
            if not rp.endswith('.git') and rp.startswith('https://'):
                apiworld.config['config_tool']['res_paths'].remove(rp)
        apiworld.config['config_tool']['res_paths'].extend(respath)
    except KeyError:
        raise ValueError(f'not a valid config file {str(configfile)} {str(respath)} {str(tmppath)} {str(finpath)}')

    try:
        apiworld.config['config_tool']['tmp_path'] = tmppath
        apiworld.config['config_tool']['final_path'] = finpath
    except KeyError:
        raise ValueError(f'not a valid config file {str(configfile)} {str(respath)} {str(tmppath)} {str(finpath)}')

    logging.info(f'enforced paths {str(respath)} {str(tmppath)} {str(tmppath)}')

    # generate worlds objects, register custom maps
    logging.info('generate world')
    apiworld.generate()

    logging.info('save world')
    # save the world and see where it landed
    td = apiworld.save()

    logging.info(f'saved whole world to files in directory: {td}')

    logging.info('analyze world')
    # check the generated worlds maps, returns a graph for cytoscape

    for obj in apiworld.check_maps():
        if obj['data']['label'] == 'ERROR' or obj['data']['label'] == 'WARNING':
            logging.info(obj)
    logging.info('recommendations')
    for tmmp in apiworld.analysis_maps:
        for rrrsp in tmmp.message():
            try:
                if len(rrrsp['recommendations']) > 0:
                    logging.info(rrrsp['file'], rrrsp['recommendations'])
            except KeyError:
                pass
    logging.info('done')


def run_overview(respath):
    # create index for each configured resource path
    rs = waresources.waindex('default')
    # load resources into by resource folder
    rs.scan(os.path.abspath(respath))

    # get some data
    cm = rs.find_custom_maps_path()  # res/maps , res/thumbnails
    tm = rs.find_templates_maps_path()  # res/templates/maps /res/templates/thumbnails

    tmapos = []
    mymaps = []
    mymaps.extend(cm)
    mymaps.extend(tm)
    # init a map for each json file found
    for mymap in mymaps:
        tmapo = wamap.wamap('tempmap')
        tmapo.read(mymap[0])
        tmapos.append(tmapo)
        # list template and thumbnail
        logging.info(f'-map: {mymap[0]}')
        logging.info(f'--thumbnail: {mymap[1]}')
        # list maps template features
        logging.info(f'--features: {tmapo.__tpl_features__()}')

    def copy_files(sourcepath, targetpath):
        def copy(sourcepath, targetpath):
            nsp = os.path.join(sourcepath, Path(sourcepath))
            os.makedirs(os.path.split(targetpath)[0], exist_ok=True)
            try:
                shutil.copy(nsp, targetpath)
                return True
            except FileNotFoundError as err:
                return False
            except shutil.SameFileError as err:
                return False

        all_files = os.walk(os.path.abspath(sourcepath))
        for directory in all_files:
            dn = directory[0]
            dirfiles = directory[2]
            for file in dirfiles:
                filefullpath = os.path.abspath(os.path.join(dn, file))  # os.path.abspath('{}/{}'.format(dir, file))
                amiok = True
                for ble in ['__', 'py', 'test_data', '.package-lock.json', 'TMP', 'TEST', 'FIN', 'TOOL']:
                    if str(ble) in str(filefullpath):
                        amiok = False

                areyouok = False
                if amiok:
                    for wle in ['tilesets', 'templates', 'sh', 'maps', 'js', 'html', 'generated', 'fonts', 'div',
                                'audio']:
                        if str(wle) in str(filefullpath):
                            areyouok = True

                if amiok and areyouok:
                    # print(sourcepath, targetpath)

                    fulltargetpath = os.path.join(os.environ.get('WOWGEN_DEFAULT'),
                                                  os.path.relpath(os.path.join(dn, file), start=sourcepath))

                    # print(dir, file, fulltargetpath)
                    copy(filefullpath, fulltargetpath)


def get_dependent_files(respath=None, locpath=None, inspath=None, extpath=None):
    """ copies files from respath to locpath and returns
    [('relative folder path to write file to, without filename, ['file w. its absolute path to copy'])]

    if extpath is set, tries to clone the tool´s repo there
    """

    def get_files_rel(sourcepath, targetbase):
        """ returns [('relative folder path to write file to, without filename, ['file w. its absolute path to copy'])] """
        p = []
        all_files = os.walk(os.path.abspath(sourcepath), topdown=False)
        for directory in all_files:
            dn = directory[0]
            dirfiles = directory[2]
            for file in dirfiles:
                filefullpath = os.path.relpath(os.path.join(dn), start=sourcepath)
                fulltargetpath = os.path.join(sourcepath, os.path.relpath(os.path.join(dn, file), start=sourcepath))
                p.append((str(os.path.join(str(targetbase), str(filefullpath))), [str(fulltargetpath)]))
        return p

    if extpath:
        remotes.git_clone(repolist=[("https://git.cccwi.de/2dwt/wowgen.git", "wowgen.git", "main")], git_dir=extpath)

    return get_files_rel(str(os.path.join(extpath, "wowgen.git")), inspath)


def prepare_paths(path_to_resources=None, path_to_os_tmp=None, path_to_default_data=None, path_to_extra_data=None):
    # set paths and env
    if not path_to_os_tmp:
        if tempfile.gettempdir():
            tmpdir = tempfile.gettempdir()
        else:
            tmpdir = os.path.curdir

        path_to_os_tmp = str(tmpdir)
    else:
        tmpdir = str(os.path.split(path_to_os_tmp)[0])

    # data cloned from git, user data
    if not path_to_extra_data:
        if os.environ.get('WOWGEN_EXTRA'):
            path_to_extra_data = os.environ.get('WOWGEN_EXTRA')
        else:
            os.environ['WOWGEN_EXTRA'] = str(os.path.join(tmpdir, 'wowgen_extra'))
            path_to_extra_data = str(os.path.join(tmpdir, 'wowgen_extra'))

    logging.info(f'extra data dir: {path_to_extra_data} env: WOWGEN_EXTRA')

    return path_to_resources, path_to_os_tmp, path_to_default_data, path_to_extra_data


def do_test():
    path_to_resources, path_to_os_tmp, path_to_default_data, path_to_extra_data = prepare_paths()
    get_dependent_files(
        respath=path_to_resources,
        locpath=path_to_os_tmp,
        inspath=path_to_default_data,
        extpath=path_to_extra_data
    )

    logging.info('testing')

    # doctests
    doctest.testmod(wamap, verbose=False)
    doctest.testmod(waresources, verbose=False)
    doctest.testmod(wagenerators, verbose=False)
    doctest.testmod(waworld, verbose=False)
    doctest.testmod(waapi, verbose=False)
    doctest.testmod(remotes, verbose=False)

    logging.info('testing finished')


if __name__ == "__main__":
    doctest.testmod(verbose=True)
