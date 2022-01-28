import seutils, pytest, fakefs
import sys
from contextlib import contextmanager

if sys.version_info.major == 2:
    from io import BytesIO as StringIO
else:
    from io import StringIO 

class capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

def capture(argv):
    command = argv[0].replace('seu-', '')
    with sys_argv(argv):
        with capturing() as output:
            getattr(seutils.cli, command)()    
    return output

@pytest.fixture
def fake_internet():
    seutils.debug()
    fi = fakefs.FakeInternet()
    fs_local = fakefs.FakeFS()
    fs_remote = fakefs.FakeRemoteFS('root://foo.bar.gov')
    fs_local.put('/foo/bar/local.file', isdir=False, content='localcontent')
    fs_remote.put('/foo/bar/test.file', isdir=False, content='testcontent')
    fi.fs = {fs_remote.mgm : fs_remote, '<local>': fs_local}
    fakefs.activate_command_interception(fi)
    yield fi
    fakefs.deactivate_command_interception()

@contextmanager
def sys_argv(argv):
    try:
        _sys_argv = sys.argv
        sys.argv = argv
        yield argv
    finally:
        sys.argv = _sys_argv


# implementations = ['xrd', 'gfal']
implementations = ['xrd']
# implementations = ['gfal']

def test_version():
    assert capture(['seu-version']) == [seutils.version()]

def test_parser_implementation():
    with sys_argv(['some_cl', '-i', 'gfal']):
        args = seutils.cli.Parser().parse_args()
    assert args.implementation is seutils.gfal
    with sys_argv(['some_cl', '-i', 'xrd']):
        args = seutils.cli.Parser().parse_args()
    assert args.implementation is seutils.xrd


@pytest.mark.parametrize('implementation', implementations)
def test_cat(fake_internet, implementation):
    assert capture(
        ['seu-cat', 'root://foo.bar.gov//foo/bar/test.file', '-i', implementation]
        ) == ['testcontent']

@pytest.mark.parametrize('implementation', implementations)
def test_ls(fake_internet, implementation):
    assert capture(
        ['seu-ls', 'root://foo.bar.gov//foo/bar/', '-i', implementation]
        ) == ['root://foo.bar.gov//foo/bar/test.file']
    assert capture(
        ['seu-ls', 'root://foo.bar.gov//foo/bar', '-i', implementation]
        ) == ['root://foo.bar.gov//foo/bar/test.file']
    assert capture(
        ['seu-ls', 'root://foo.bar.gov//foo/*/*', '-i', implementation]
        ) == ['root://foo.bar.gov//foo/bar/test.file']
    long = capture(
        ['seu-ls', 'root://foo.bar.gov//foo/*/*', '-i', implementation, '-l']
        )[0]
    assert len(long.split()) == 5 and long.split()[-1] == 'root://foo.bar.gov//foo/bar/test.file'

@pytest.mark.parametrize('implementation', implementations)
def test_du(fake_internet, implementation):
    fs = fake_internet.fs['root://foo.bar.gov']
    dir1 = fs.stat('root://foo.bar.gov//foo/bar')
    node1 = fs.stat('root://foo.bar.gov//foo/bar/test.file')
    node2 = fs.put('root://foo.bar.gov//foo/bar/test.file2', isdir=False, size=node1.size*2)

    def extract_size_path(captured):
        ret = []
        for line in captured:
            comps = line.split()
            ret.append((comps[0] + ' ' + comps[1], comps[2]))
        return ret

    assert extract_size_path(capture(
        ['seu-du', 'root://foo.bar.gov//foo/bar/', '-i', implementation]
        )) == [(dir1.size_human, dir1.path)]
    assert extract_size_path(capture(
        ['seu-du', 'root://foo.bar.gov//foo/bar/*', '-i', implementation, '-s']
        )) == [(node2.size_human, node2.path), (node1.size_human, node1.path)]


@pytest.mark.parametrize('implementation', implementations)
def test_rm(fake_internet, implementation):
    capture(['seu-rm', 'root://foo.bar.gov//foo/bar/test.file', '-i', implementation, '-y'])
    assert not fake_internet.fs['root://foo.bar.gov'].exists('root://foo.bar.gov//foo/bar/test.file')
    with pytest.raises(Exception):
        capture(['seu-rm', 'root://foo.bar.gov//foo/bar', '-i', implementation, '-y'])
    capture(['seu-rm', 'root://foo.bar.gov//foo/bar', '-i', implementation, '-y', '-r'])
    assert not fake_internet.fs['root://foo.bar.gov'].exists('root://foo.bar.gov//foo/bar')


@pytest.mark.parametrize('implementation', implementations)
def test_mkdir(fake_internet, implementation):
    capture(['seu-mkdir', 'root://foo.bar.gov//foo/new/dir', '-i', implementation])
    fs = fake_internet.fs['root://foo.bar.gov']
    assert fs.isdir('root://foo.bar.gov//foo/new')
    assert fs.isdir('root://foo.bar.gov//foo/new/dir')
