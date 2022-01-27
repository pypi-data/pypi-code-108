from datetime import date
import seutils, pytest

def test_normpath():
    assert seutils.normpath('/foo/.//bar/../.') == '/foo'
    assert seutils.normpath('root://foo.bar.gov//foo/.//bar/../.') == 'root://foo.bar.gov//foo'
    assert seutils.normpath('root://foo.bar.gov//foo/.//bar/../.') == 'root://foo.bar.gov//foo'
    
def test_split_mgm():
    path = 'root://foo.bar.gov//foo/bar'
    assert seutils.split_mgm(path) == ('root://foo.bar.gov', '/foo/bar')
    with pytest.raises(ValueError):
        seutils.split_mgm(path, mgm='root://other.bar.gov/')
    assert seutils.split_mgm('root://foo.bar.gov//') == ('root://foo.bar.gov', '/')
    with pytest.raises(ValueError):
        seutils.split_mgm('root://foo.bar.gov/')

def test_dirname():
    assert seutils.dirname('/foo/bar') == '/foo'
    assert seutils.dirname('root://foo.bar.gov//foo/bar') == 'root://foo.bar.gov//foo'
    assert seutils.dirname('root://foo.bar.gov//foo/.//bar//.') == 'root://foo.bar.gov//foo'
    assert seutils.dirname('root://foo.bar.gov//foo') == 'root://foo.bar.gov//'
    assert seutils.dirname('root://foo.bar.gov//') == 'root://foo.bar.gov//'
    with pytest.raises(ValueError):
        seutils.split_mgm('root://foo.bar.gov/')

def test_iter_parent_dirs():
    assert list(seutils.iter_parent_dirs('/foo/bar')) == ['/foo', '/']
    assert list(seutils.iter_parent_dirs('root://foo.bar.gov//foo/bar')) == ['root://foo.bar.gov//foo', 'root://foo.bar.gov//']
    assert list(seutils.iter_parent_dirs('root://foo.bar.gov//foo/.//bar//.')) == ['root://foo.bar.gov//foo', 'root://foo.bar.gov//']

def test_inode_equality():
    from datetime import datetime
    left = seutils.Inode('/bla', datetime(2019, 10, 10, 10, 10, 10), True, 1001)
    right = seutils.Inode('/bla', datetime(2019, 10, 10, 10, 10, 10), True, 1001)
    assert left == right
    right.size = 1002
    assert left != right

def test_relpath():
    assert seutils.relpath('/foo/bar/bla.txt', '/foo/') == 'bar/bla.txt'
    assert seutils.relpath('/foo/bar/bla.txt', '/foo') == 'bar/bla.txt'
    assert seutils.relpath('root://foo.bar.gov//foo/bar/bla.txt', 'root://foo.bar.gov//foo/') == 'bar/bla.txt'
    assert seutils.relpath('root://foo.bar.gov//foo/bar/bla.txt', 'root://foo.bar.gov//foo') == 'bar/bla.txt'
    with pytest.raises(TypeError):
        seutils.relpath('root://foo.bar.gov//foo/bar', '/foo')
    with pytest.raises(TypeError):
        seutils.relpath('root://foo.bar.gov//foo/bar', 'gsiftp://foo.bar.edu//foo')
