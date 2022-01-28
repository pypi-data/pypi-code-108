import os
import pathlib
from unittest import mock

from libpipe import settings


class Settings(settings.BaseSettings):

    DEFAULT_SETTINGS = pathlib.Path(__file__).absolute().parent / 'settings_test.toml'


def test_settings(tmp_path):
    c = Settings(None, {'vis': {'umin': 20, 'umax': 40, 'list': ['a', 'b']}, 'data_path': 'some_path'})

    assert c.vis.umin == 20
    assert c.vis.umax == 40
    assert c.data_path == 'some_path'
    assert c['vis'] == {'umin': 20, 'umax': 40, 'list': ['a', 'b']}
    assert c.vis.list == ['a', 'b']
    assert c.vis.list[1] == 'b'

    c.image = {'lmin': 100, 'data_col': 'DATA'}
    c.obs_ids = [1, 2, 3, 4]

    assert c.image.lmin == 100
    assert c.image.data_col == 'DATA'
    assert c.obs_ids == [1, 2, 3, 4]
    assert c.obs_ids[0] == 1

    s = '''
    db_path = 'some_other_path'

    [vis]
    list = ['c', 'd']

    [worker]
    nodes = 'node1[0-1][1-5]'
    concurrent = 2
    '''

    filename = tmp_path / 'test.toml'
    with open(str(filename), 'w') as f:
        f.write(s)

    c2 = Settings.load(str(filename))

    assert c2.vis.list == ['c', 'd']
    assert c2.worker.nodes == 'node1[0-1][1-5]'

    c3 = c2.copy()
    c3.worker.concurrent = 3
    c3.new = 'a'

    assert c2.worker.concurrent == 2
    assert c3.worker.concurrent == 3
    assert hasattr(c3, 'new')
    assert not hasattr(c2, 'new')

    c4 = c + c2

    assert c4.vis.umin == 20
    assert c4.vis.umax == 40
    assert c4.vis.list == ['c', 'd']
    assert c4.worker.nodes == 'node1[0-1][1-5]'
    assert c4.worker.concurrent == 2

    c5 = c + c2 + c3

    assert c5.worker.concurrent == 3
    assert c5.new == 'a'

    c = Settings.load_from_string(s)

    assert c.vis.list == ['c', 'd']
    assert c.worker.nodes == 'node1[0-1][1-5]'

    c = Settings.load_from_string(['db_path="a"', 'vis.c=2'])

    assert c.db_path == 'a'
    assert c.vis.c == 2


def test_default_settings(tmp_path):
    s = '''
    db_path = 'some_path'
    default_settings = ''

    [vis_cube]
    umax = 200
    win_fct = 'hann'

    [worker]
    nodes = 'node1[0-1][1-5]'
    concurrent = 2
    '''

    filename = tmp_path / 'config.toml'
    with open(str(filename), 'w') as f:
        f.write(s)

    c = Settings.load_with_defaults(filename)

    assert c.db_path == 'some_path'
    assert c.default_settings == ''
    assert c.vis_cube.umax == 200
    assert c.vis_cube.win_fct == 'hann'
    assert c.worker.nodes == 'node1[0-1][1-5]'
    assert c.worker.concurrent == 2
    assert c.data_dir == '.'
    assert c.vis_cube.umin == 50

    s = f'''
    db_path = 'some_other_path'
    default_settings = '{str(filename)}'

    [vis_cube]
    umax = 400

    [image]
    umax = 5000

    [worker]
    concurrent = 2
    '''

    filename2 = tmp_path / 'config2.toml'
    with open(str(filename2), 'w') as f:
        f.write(s)

    with mock.patch.object(Settings, 'DEFAULT_SETTINGS', filename):
        c = Settings.load_with_defaults(filename2)

        assert c.db_path == 'some_other_path'
        assert os.path.abspath(c.default_settings) == os.path.abspath(filename)
        assert c.vis_cube.umax == 400
        assert c.vis_cube.win_fct == 'hann'
        assert c.worker.nodes == 'node1[0-1][1-5]'
        assert c.worker.concurrent == 2
        assert c.image.umax == 5000

        c.save(strip_parents_keys=True)

        c = Settings.load_with_defaults(filename2)

        assert c.db_path == 'some_other_path'
        assert os.path.abspath(c.default_settings) == os.path.abspath(filename)
        assert c.vis_cube.umax == 400
        assert c.vis_cube.win_fct == 'hann'
        assert c.worker.nodes == 'node1[0-1][1-5]'
        assert c.worker.concurrent == 2
        assert c.image.umax == 5000

        c = Settings.load(filename2)

        print(open(filename2).readlines())
        assert c.db_path == 'some_other_path'
        assert os.path.abspath(c.default_settings) == os.path.abspath(filename)
        assert c.image.umax == 5000
        assert c.vis_cube.umax == 400
        assert not hasattr(c, 'worker')
        assert not hasattr(c.image, 'win_fct')


def test_duplicate(tmp_path):
    s = '''
    db_path = 'some_path'
    default_settings = ''

    [worker]
    nodes = 'node1[0-1][1-5]'
    concurrent = 2
    some_parset = 'config/some_file.parset'
    '''
    os.chdir(tmp_path)

    filename = tmp_path / 'config.toml'
    with open(str(filename), 'w') as f:
        f.write(s)

    os.makedirs(tmp_path / 'config')

    (tmp_path / 'config' / 'some_file.parset').touch()

    s = Settings.load_with_defaults(filename)

    new_file = tmp_path / 'new_config.toml'

    ns = s.duplicate(new_file)

    assert ns.db_path == 'some_path'
    assert ns.worker.some_parset == 'config/some_file.parset'
    assert not (tmp_path / 'new_dir' / 'config' / 'some_file.parset').is_file()

    new_file = tmp_path / 'new_dir' / 'new_config.toml'

    ns = s.duplicate(new_file, copy_parset_files=False)

    assert ns.db_path == 'some_path'
    assert ns.worker.some_parset == str(tmp_path / 'config' / 'some_file.parset')

    new_file = tmp_path / 'new_dir' / 'new_config.toml'

    ns = s.duplicate(new_file, copy_parset_files=True)

    assert ns.db_path == 'some_path'
    assert ns.worker.some_parset == 'config/some_file.parset'
    assert (tmp_path / 'new_dir' / 'config' / 'some_file.parset').is_file()

    ns = s.duplicate(new_file, update_relative_path=True, **{'db_path': 'added_path', 'worker': {'concurrent': 4}})

    assert ns.db_path == 'added_path'
    assert ns.worker.concurrent == 4


def test_get_path(tmp_path):
    c = Settings(None, {'data_dir': 'a'})
    assert c.get_path('data_dir') == str(pathlib.Path.cwd() / 'a')

    c = Settings('/some/file.toml', {'data_dir': 'a'})
    assert c.get_path('data_dir') == '/some/a'

    c = Settings(None, {'data_dir': '/a'})
    assert c.get_path('data_dir') == '/a'

    c = Settings('/some/file.toml', {'data_dir': '/a'})
    assert c.get_path('data_dir') == '/a'

    c = Settings.load_from_string('a.b.data_dir = "/some_dir"')
    assert c.get_path('a.b.data_dir') == '/some_dir'

    c = Settings.load_from_string('a.b.data_dir = "some_dir"')
    assert c.get_path('a.b.data_dir') == str(pathlib.Path.cwd() / 'some_dir')

    c = Settings.load_from_string('a.b.c.data_dir = "/some_dir"')
    assert c.a.b.get_path('c.data_dir') == '/some_dir'


def test_default_type(tmp_path):
    s = '''
    [type1]
    a = 200
    b = 'h'

    [type2]
    c = [1, 2, 3]
    d.k = 2

    [type3]
    pa.b = 3
    pa.c = '2'
    v = [1]

    [type4]
    a = 0

    [type5]
    u = 0
    '''

    filename = tmp_path / 'default.toml'
    with open(str(filename), 'w') as f:
        f.write(s)

    s = '''
    [action1]
    type = 'type1'
    a = 100

    [action2]
    type = 'type1'
    c = 200

    [action3]
    type = 'type2'
    c = [2, 3, 1, 2]
    d = 4

    [type3]
    pa.a = 1
    pa.c = '5'

    [type5]

    '''

    filename2 = tmp_path / 'config.toml'
    with open(str(filename2), 'w') as f:
        f.write(s)

    with mock.patch.object(Settings, 'DEFAULT_SETTINGS', filename):
        c = Settings.load_with_defaults(filename2, with_type_keyword=True)

    assert c.action1.a == 100
    assert c.action1.b == 'h'
    assert c.action2.a == 200
    assert c.action2.c == 200
    assert c.action3.d == 4
    assert c.action3.c == [2, 3, 1, 2]
    assert c.type3.pa.a == 1
    assert c.type3.pa.b == 3
    assert c.type3.pa.c == '5'
    assert c.type3.v == [1]
    assert 'type4' not in c
    assert 'type5' in c
