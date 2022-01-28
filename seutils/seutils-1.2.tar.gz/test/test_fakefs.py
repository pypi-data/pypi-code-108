import pytest
import random
import seutils
import fakefs

@pytest.fixture
def fs():
    rd = random.Random()
    rd.seed(1006)
    nodes = []
    nodes.append(fakefs.generate_fake_dir(path='/', rd=rd))
    nodes.append(fakefs.generate_fake_dir(path='/foo', rd=rd))
    nodes.append(fakefs.generate_fake_dir(path='/foo/bar', rd=rd))
    nodes.append(fakefs.generate_fake_dir(path='/foo/bar/dira', rd=rd))
    nodes.append(fakefs.generate_fake_dir(path='/foo/bar/dirb', rd=rd))
    nodes.append(fakefs.generate_fake_file(path='/foo/bar/test.file', rd=rd, content='testcontent'))
    return fakefs.FakeFS(nodes)

def test_fakefs_isdir(fs):
    assert (fs.isdir('/foo/bar/dira') is True)

def test_fakefs_isfile(fs):
    assert (fs.isfile('/foo/bar/test.file') is True)

def test_fakefs_stat(fs):
    node = fs.stat('/foo/bar/test.file')
    assert node.path == '/foo/bar/test.file'

def test_fakefs_raises_nosuchpath(fs):
    with pytest.raises(seutils.NoSuchPath):
        fs.stat('/no/such/path')

def test_fakefs_mkdir(fs):
    testdir = '/foo/bar/my/new/directory'
    assert not(fs.isdir(testdir))
    fs.mkdir(testdir)
    assert fs.isdir(testdir)

def test_fakefs_rm(fs):
    fs.rm('/foo/bar/test.file')
    assert not(fs.isfile('/foo/bar/test.file'))
    with pytest.raises(seutils.NoSuchPath):
        fs.rm('/foo/bar/test.file')

def test_fakefs_cat(fs):
    assert fs.cat('/foo/bar/test.file') == 'testcontent'

def test_fakefs_put(fs):
    fs.put(path='/test/path/file.file')
    assert fs.isdir('/test')
    assert fs.isdir('/test/path')
    assert fs.isfile('/test/path/file.file')



def test_iter_parent_dirs():
    path = 'root://foo.bar.gov//foo/bar/test.file'
    parent_dirs = list(seutils.iter_parent_dirs(path))
    assert parent_dirs[0] == 'root://foo.bar.gov//foo/bar'
    assert parent_dirs[1] == 'root://foo.bar.gov//foo'
    assert parent_dirs[2] == 'root://foo.bar.gov//'
    assert len(parent_dirs) == 3
    path = '/foo/bar/test.file'
    parent_dirs = list(seutils.iter_parent_dirs(path))
    assert parent_dirs[0] == '/foo/bar'
    assert parent_dirs[1] == '/foo'
    assert parent_dirs[2] == '/'
    assert len(parent_dirs) == 3


@pytest.fixture
def remotefs():
    seutils.debug()
    fs = fakefs.FakeRemoteFS('root://foo.bar.gov/')
    fs.put('root://foo.bar.gov//foo/bar/test.file', isdir=False, content='testcontent')
    seutils.logger.info('End of setup; fs: %s', fs.nodes)
    return fs

def test_fakeremotefs_stat(remotefs):
    node = remotefs.stat('root://foo.bar.gov//foo/bar/test.file')
    assert node.path == 'root://foo.bar.gov//foo/bar/test.file'

def test_fakeremotefs_isdir(remotefs):
    assert (remotefs.isdir('root://foo.bar.gov//foo/bar') is True)

def test_fakeremotefs_isfile(remotefs):
    assert (remotefs.isfile('root://foo.bar.gov//foo/bar/test.file') is True)

def test_fakeremotefs_raises_nosuchpath(remotefs):
    with pytest.raises(seutils.NoSuchPath):
        remotefs.stat('/no/such/path')

def test_fakeremotefs_mkdir(remotefs):
    testdir = 'root://foo.bar.gov//foo/bar/my/new/directory'
    assert not(remotefs.isdir(testdir))
    remotefs.mkdir(testdir)
    assert remotefs.isdir(testdir)

def test_fakeremotefs_rm(remotefs):
    remotefs.rm('root://foo.bar.gov//foo/bar/test.file')
    assert not(remotefs.isfile('root://foo.bar.gov//foo/bar/test.file'))
    with pytest.raises(seutils.NoSuchPath):
        remotefs.rm('root://foo.bar.gov//foo/bar/test.file')

def test_fakeremotefs_cat(remotefs):
    assert remotefs.cat('root://foo.bar.gov//foo/bar/test.file') == 'testcontent'









# def get_fake_internet():
#     fi = fakefs.FakeInternet()
#     fs1 = fakefs.FakeRemoteFS('root://foo.bar.gov')
#     fs2 = fakefs.FakeRemoteFS('gsiftp://foo.bar.edu')
#     fs1.put('/foo/bar/test.file', isdir=False, content='testcontent')
#     fs2.put('/foo/bar/other.file', isdir=False)
#     fi.fs = {fs1.mgm : fs1, fs2.mgm : fs2}
#     return fi

# def test_fake_internet():
#     fi = get_fake_internet()
#     assert fi.intercept(['xrdfs', 'root://foo.bar.gov', 'ls', '/foo'])[0] == 0



