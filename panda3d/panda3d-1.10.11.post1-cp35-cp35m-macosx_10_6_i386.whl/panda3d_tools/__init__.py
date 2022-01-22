import os, sys
import panda3d

dir = os.path.dirname(panda3d.__file__)
del panda3d

if sys.platform in ('win32', 'cygwin'):
    path_var = 'PATH'
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(dir)
elif sys.platform == 'darwin':
    path_var = 'DYLD_LIBRARY_PATH'
else:
    path_var = 'LD_LIBRARY_PATH'

if not os.environ.get(path_var):
    os.environ[path_var] = dir
else:
    os.environ[path_var] = dir + os.pathsep + os.environ[path_var]

del os, sys, path_var, dir


def _exec_tool(tool):
    import os, sys
    from subprocess import Popen
    tools_dir = os.path.dirname(__file__)
    handle = Popen(sys.argv, executable=os.path.join(tools_dir, tool))
    try:
        try:
            return handle.wait()
        except KeyboardInterrupt:
            # Give the program a chance to handle the signal gracefully.
            return handle.wait()
    except:
        handle.kill()
        handle.wait()
        raise

# Register all the executables in this directory as global functions.
apply_patch = lambda: _exec_tool('apply_patch')
bam_info = lambda: _exec_tool('bam-info')
bam2egg = lambda: _exec_tool('bam2egg')
build_patch = lambda: _exec_tool('build_patch')
check_adler = lambda: _exec_tool('check_adler')
check_crc = lambda: _exec_tool('check_crc')
check_md5 = lambda: _exec_tool('check_md5')
dae2egg = lambda: _exec_tool('dae2egg')
deploy_stub = lambda: _exec_tool('deploy-stub')
deploy_stubw = lambda: _exec_tool('deploy-stubw')
dxf_points = lambda: _exec_tool('dxf-points')
dxf2egg = lambda: _exec_tool('dxf2egg')
egg_crop = lambda: _exec_tool('egg-crop')
egg_list_textures = lambda: _exec_tool('egg-list-textures')
egg_make_tube = lambda: _exec_tool('egg-make-tube')
egg_mkfont = lambda: _exec_tool('egg-mkfont')
egg_optchar = lambda: _exec_tool('egg-optchar')
egg_palettize = lambda: _exec_tool('egg-palettize')
egg_qtess = lambda: _exec_tool('egg-qtess')
egg_rename = lambda: _exec_tool('egg-rename')
egg_retarget_anim = lambda: _exec_tool('egg-retarget-anim')
egg_texture_cards = lambda: _exec_tool('egg-texture-cards')
egg_topstrip = lambda: _exec_tool('egg-topstrip')
egg_trans = lambda: _exec_tool('egg-trans')
egg2bam = lambda: _exec_tool('egg2bam')
egg2c = lambda: _exec_tool('egg2c')
egg2dxf = lambda: _exec_tool('egg2dxf')
egg2flt = lambda: _exec_tool('egg2flt')
egg2maya2011 = lambda: _exec_tool('egg2maya2011')
egg2maya2012 = lambda: _exec_tool('egg2maya2012')
egg2maya2013 = lambda: _exec_tool('egg2maya2013')
egg2maya2014 = lambda: _exec_tool('egg2maya2014')
egg2maya2015 = lambda: _exec_tool('egg2maya2015')
egg2maya2016 = lambda: _exec_tool('egg2maya2016')
egg2maya20165 = lambda: _exec_tool('egg2maya20165')
egg2maya2017 = lambda: _exec_tool('egg2maya2017')
egg2maya2018 = lambda: _exec_tool('egg2maya2018')
egg2maya2019 = lambda: _exec_tool('egg2maya2019')
egg2maya2020 = lambda: _exec_tool('egg2maya2020')
egg2maya2022 = lambda: _exec_tool('egg2maya2022')
egg2obj = lambda: _exec_tool('egg2obj')
egg2x = lambda: _exec_tool('egg2x')
flt_info = lambda: _exec_tool('flt-info')
flt_trans = lambda: _exec_tool('flt-trans')
flt2egg = lambda: _exec_tool('flt2egg')
fltcopy = lambda: _exec_tool('fltcopy')
image_info = lambda: _exec_tool('image-info')
image_resize = lambda: _exec_tool('image-resize')
image_trans = lambda: _exec_tool('image-trans')
interrogate = lambda: _exec_tool('interrogate')
interrogate_module = lambda: _exec_tool('interrogate_module')
lwo_scan = lambda: _exec_tool('lwo-scan')
lwo2egg = lambda: _exec_tool('lwo2egg')
make_prc_key = lambda: _exec_tool('make-prc-key')
maya2egg2011 = lambda: _exec_tool('maya2egg2011')
maya2egg2012 = lambda: _exec_tool('maya2egg2012')
maya2egg2013 = lambda: _exec_tool('maya2egg2013')
maya2egg2014 = lambda: _exec_tool('maya2egg2014')
maya2egg2015 = lambda: _exec_tool('maya2egg2015')
maya2egg2016 = lambda: _exec_tool('maya2egg2016')
maya2egg20165 = lambda: _exec_tool('maya2egg20165')
maya2egg2017 = lambda: _exec_tool('maya2egg2017')
maya2egg2018 = lambda: _exec_tool('maya2egg2018')
maya2egg2019 = lambda: _exec_tool('maya2egg2019')
maya2egg2020 = lambda: _exec_tool('maya2egg2020')
maya2egg2022 = lambda: _exec_tool('maya2egg2022')
mayacopy2011 = lambda: _exec_tool('mayacopy2011')
mayacopy2012 = lambda: _exec_tool('mayacopy2012')
mayacopy2013 = lambda: _exec_tool('mayacopy2013')
mayacopy2014 = lambda: _exec_tool('mayacopy2014')
mayacopy2015 = lambda: _exec_tool('mayacopy2015')
mayacopy2016 = lambda: _exec_tool('mayacopy2016')
mayacopy20165 = lambda: _exec_tool('mayacopy20165')
mayacopy2017 = lambda: _exec_tool('mayacopy2017')
mayacopy2018 = lambda: _exec_tool('mayacopy2018')
mayacopy2019 = lambda: _exec_tool('mayacopy2019')
mayacopy2020 = lambda: _exec_tool('mayacopy2020')
mayacopy2022 = lambda: _exec_tool('mayacopy2022')
multify = lambda: _exec_tool('multify')
obj2egg = lambda: _exec_tool('obj2egg')
p3dcparse = lambda: _exec_tool('p3dcparse')
parse_file = lambda: _exec_tool('parse_file')
pdecrypt = lambda: _exec_tool('pdecrypt')
pencrypt = lambda: _exec_tool('pencrypt')
pfm_bba = lambda: _exec_tool('pfm-bba')
pfm_trans = lambda: _exec_tool('pfm-trans')
punzip = lambda: _exec_tool('punzip')
pview = lambda: _exec_tool('pview')
pzip = lambda: _exec_tool('pzip')
show_ddb = lambda: _exec_tool('show_ddb')
test_interrogate = lambda: _exec_tool('test_interrogate')
text_stats = lambda: _exec_tool('text-stats')
vrml_trans = lambda: _exec_tool('vrml-trans')
vrml2egg = lambda: _exec_tool('vrml2egg')
x_trans = lambda: _exec_tool('x-trans')
x2egg = lambda: _exec_tool('x2egg')

