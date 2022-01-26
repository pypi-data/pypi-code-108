# -*- coding: utf-8 -*-
import os

from honeybee_radiance_folder import ModelFolder as Folder
from honeybee_radiance_folder.folderutil import add_output_spec_to_receiver
from honeybee_radiance_folder.folderutil import _nukedir


def test_static_aperture():
    radiance_folder = r'./tests/assets/project_folder'
    folder = Folder(radiance_folder)
    files = folder.aperture_files(black_out=False, rel_path=True)
    assert 'model/aperture/aperture.mat' in files
    assert 'model/aperture/aperture.rad' in files


def test_aperture_group():
    radiance_folder = r'./tests/assets/project_folder'
    folder = Folder(radiance_folder)
    apertures = folder.aperture_groups(interior=False)
    assert len(apertures) == 1
    ap = apertures[0]
    assert ap.states[0].identifier == '0_clear'
    assert ap.states[0].default == 'south_window..default..000.rad'
    assert ap.states[1].identifier == '1_diffuse'
    assert ap.states[1].default == 'south_window..default..001.rad'


def test_add_output_spec():
    re_file = r'./tests/assets/project_folder/model/aperture_group/south_window..mtx.rad'
    out_file = r'./tests/assets/temp/south_window..mtx.rad'
    output_folder = r'./tests/assets/temp'
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)
    _nukedir(output_folder, False)
    add_output_spec_to_receiver(re_file, 'cubical.vmx', out_file)
    assert os.path.isfile(out_file)
    with open(out_file) as outf:
        content = outf.read()
    assert '#@rfluxmtx h=kf u=0,0,1.0 o=cubical.vmx' in content
    _nukedir(output_folder, False)
