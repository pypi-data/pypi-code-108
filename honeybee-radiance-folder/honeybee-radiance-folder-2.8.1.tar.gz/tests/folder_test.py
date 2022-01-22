# -*- coding: utf-8 -*-
from honeybee_radiance_folder import ModelFolder as Folder
from honeybee_radiance_folder.folderutil import _as_posix
import honeybee_radiance_folder.config as config
import os
import shutil


def test_writer():
    """Test creating a new folder."""
    folder_path = r'./tests/assets/temp'
    shutil.rmtree(folder_path, ignore_errors=True)
    rad_folder = Folder(folder_path)
    rad_folder.write(folder_type=2, overwrite=True)

    assert os.path.isdir(rad_folder.folder)
    root_folder = rad_folder.model_folder(full=True)
    assert os.path.isdir(root_folder)
    subfolders = [
        f for f in os.listdir(root_folder)
        if os.path.isdir(_as_posix(os.path.join(root_folder, f)))
    ]

    cfg_names = ['GRID', 'VIEW'] + [k for k, v in config.minimal.items() if v is True]
    expected_subfolders = [rad_folder._get_folder_name(f) for f in cfg_names]

    assert len(subfolders) == len(expected_subfolders)
    for f in expected_subfolders:
        assert f in subfolders

    # try to remove the folder
    shutil.rmtree(folder_path, ignore_errors=True)


def test_writer_model_folder():
    """Test creating a new folder."""
    folder_path = r'./tests/assets/temp/rad_model'
    shutil.rmtree(folder_path, ignore_errors=True)
    rad_folder = Folder.from_model_folder(folder_path)
    rad_folder.write(folder_type=2, overwrite=True)

    assert os.path.isdir(rad_folder.folder)
    root_folder = rad_folder.model_folder(full=True)
    assert os.path.isdir(root_folder)
    subfolders = [
        f for f in os.listdir(root_folder)
        if os.path.isdir(_as_posix(os.path.join(root_folder, f)))
    ]

    cfg_names = ['GRID', 'VIEW'] + [k for k, v in config.minimal.items() if v is True]
    expected_subfolders = [rad_folder._get_folder_name(f) for f in cfg_names]

    assert len(subfolders) == len(expected_subfolders)
    for f in expected_subfolders:
        assert f in subfolders

    # try to remove the folder
    shutil.rmtree(folder_path, ignore_errors=True)


def test_reader():
    radiance_folder = r'./tests/assets/project_folder'
    rad_folder = Folder(radiance_folder)
    assert rad_folder.model_folder() == 'model'
    assert rad_folder.aperture_folder() == _as_posix(os.path.join('model', 'aperture'))
    assert rad_folder.aperture_group_folder() == \
        _as_posix(os.path.join('model', 'aperture_group'))
    assert rad_folder.aperture_group_folder(interior=True) == \
        _as_posix(os.path.join('model', 'aperture_group', 'interior'))
    assert rad_folder.bsdf_folder() == _as_posix(os.path.join('model', 'bsdf'))
    assert rad_folder.grid_folder() == _as_posix(os.path.join('model', 'grid'))
    assert rad_folder.ies_folder() == _as_posix(os.path.join('model', 'ies'))
    assert rad_folder.scene_folder() == _as_posix(os.path.join('model', 'scene'))
    assert rad_folder.dynamic_scene_folder() == \
        _as_posix(os.path.join('model', 'scene_dynamic'))
    assert rad_folder.dynamic_scene_folder(indoor=True) == \
        _as_posix(os.path.join('model', 'scene_dynamic', 'indoor'))
    assert rad_folder.view_folder() == _as_posix(os.path.join('model', 'view'))


def test_reader_files():
    radiance_folder = r'./tests/assets/project_folder'
    rad_folder = Folder(radiance_folder)
    assert rad_folder.has_aperture_group
    assert not rad_folder.has_dynamic_scene
    assert rad_folder.aperture_files() == [
        'model/aperture/aperture.mat', 'model/aperture/aperture.rad'
    ]
    assert rad_folder.aperture_files(black_out=True) == [
        'model/aperture/aperture.blk', 'model/aperture/aperture.rad'
    ]

    s_files = rad_folder.scene_files()
    e_files = [
        'model/scene/context.mat', 'model/scene/context.rad',
        'model/scene/partition.mat', 'model/scene/partition.rad',
        'model/scene/partition_glass.mat', 'model/scene/partition_glass.rad',
        'model/scene/room_envelope.mat', 'model/scene/room_envelope.rad'
    ]
    assert s_files.index(e_files[1]) - s_files.index(e_files[0]) == 1
    assert s_files.index(e_files[3]) - s_files.index(e_files[2]) == 1
    assert s_files.index(e_files[5]) - s_files.index(e_files[4]) == 1
    assert s_files.index(e_files[7]) - s_files.index(e_files[6]) == 1

    s_files = rad_folder.scene_files(black_out=True)
    e_files = [
        'model/scene/context.blk', 'model/scene/context.rad',
        'model/scene/partition.blk', 'model/scene/partition.rad',
        'model/scene/partition_glass.blk', 'model/scene/partition_glass.rad',
        'model/scene/room_envelope.blk', 'model/scene/room_envelope.rad'
    ]
    assert s_files.index(e_files[1]) - s_files.index(e_files[0]) == 1
    assert s_files.index(e_files[3]) - s_files.index(e_files[2]) == 1
    assert s_files.index(e_files[5]) - s_files.index(e_files[4]) == 1
    assert s_files.index(e_files[7]) - s_files.index(e_files[6]) == 1
