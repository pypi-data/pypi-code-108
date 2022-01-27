import seutils, fakefs, pytest, os, os.path as osp

def get_fake_internet():
    fi = fakefs.FakeInternet()
    fs_local = fakefs.FakeFS()
    fs1 = fakefs.FakeRemoteFS('root://foo.bar.gov')
    fs2 = fakefs.FakeRemoteFS('gsiftp://foo.bar.edu')
    fs_local.put('/foo/bar/local.file', isdir=False, content='localcontent')
    fs1.put('/foo/bar/test.file', isdir=False, content='testcontent')
    fs2.put('/foo/bar/other.file', isdir=False)
    fi.fs = {fs1.mgm : fs1, fs2.mgm : fs2, '<local>': fs_local}
    return fi

@pytest.fixture
def impl(request):
    seutils.debug()
    fi = get_fake_internet()
    seutils.logger.debug('Setup; test nodes: %s', fi.fs['root://foo.bar.gov'].nodes)
    fakefs.activate_command_interception(fi)
    yield request.getfixturevalue(request.param)
    fakefs.deactivate_command_interception()

@pytest.fixture
def gfal_impl():
    return seutils.GfalImplementation()

@pytest.fixture
def xrd_impl():
    return seutils.XrdImplementation()

@pytest.fixture
def globalscope_impl():
    # Disable all implementations except xrd, ensuring that the heuristic
    # to determine the implementation always returns xrd
    for name, impl in seutils.implementations.items():
        if name == 'xrd': continue
        impl._is_installed_BACKUP = impl._is_installed
        impl._is_installed = False
    yield seutils
    impl._is_installed = impl._is_installed_BACKUP


implementations = ['gfal_impl', 'xrd_impl', 'globalscope_impl']
# implementations = ['gfal_impl']
# implementations = ['xrd_impl']


@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_stat(impl):
    node = impl.stat('root://foo.bar.gov//foo/bar/test.file')
    assert node.path == 'root://foo.bar.gov//foo/bar/test.file'

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_isdir(impl):
    assert impl.isdir('root://foo.bar.gov//foo/bar') is True

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_isfile(impl):
    assert impl.isfile('root://foo.bar.gov//foo/bar/test.file') is True

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_raises_nosuchpath(impl):
    with pytest.raises(seutils.NoSuchPath):
        impl.stat('root://foo.bar.gov//no/such/path')

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_mkdir(impl):
    testdir = 'root://foo.bar.gov//foo/bar/my/new/directory'
    assert not(impl.isdir(testdir))
    impl.mkdir(testdir)
    assert impl.isdir(testdir)

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_rm(impl):
    impl.rm('root://foo.bar.gov//foo/bar/test.file')
    assert not(impl.isfile('root://foo.bar.gov//foo/bar/test.file'))
    with pytest.raises(Exception):
        impl.rm('root://foo.bar.gov//foo/bar/test.file')

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_rm_safety_blacklist(impl):
    for path in [
        'root://foo.bar.gov//',
        'root://foo.bar.gov//store',
        'root://foo.bar.gov//store/user',
        'root://foo.bar.gov//store/user/klijnsma',
        ]:
        with pytest.raises(seutils.RmSafetyTrigger):
            impl.rm(path)
    bl_backup = seutils.RM_BLACKLIST
    seutils.RM_BLACKLIST = ['/foo/bar/*']
    try:
        with pytest.raises(seutils.RmSafetyTrigger):
            impl.rm('root://foo.bar.gov//foo/bar/test.file')
    finally:
        seutils.RM_BLACKLIST = bl_backup

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_rm_safety_whitelist(impl):
    fs = seutils.active_fake_internet.fs['root://foo.bar.gov']
    fs.put('root://foo.bar.gov//store/user/someuser/okay_to_remove', isdir=False)
    fs.put('root://foo.bar.gov//store/user/someuser/notokay_to_remove', isdir=False)
    wl_backup = seutils.RM_WHITELIST
    seutils.RM_WHITELIST = ['/store/user/someuser/okay_to_remove']
    try:
        with pytest.raises(seutils.RmSafetyTrigger):
            impl.rm('root://foo.bar.gov//store/user/someuser/notokay_to_remove')
    finally:
        seutils.RM_WHITELIST = wl_backup

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_cat(impl):
    assert impl.cat('root://foo.bar.gov//foo/bar/test.file') == 'testcontent'

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_listdir(impl):
    assert impl.listdir('root://foo.bar.gov//foo/') == ['root://foo.bar.gov//foo/bar']
    with pytest.raises(Exception):
        impl.listdir('root://foo.bar.gov//foo/bar/test.file')

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_listdir_stat(impl):
    assert impl.listdir('root://foo.bar.gov//foo/', stat=True)[0].path == 'root://foo.bar.gov//foo/bar'

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_cp(impl):
    # remote -> remote, same SE
    impl.cp('root://foo.bar.gov//foo/bar/test.file', 'root://foo.bar.gov//foo/bar/copy.file')
    assert impl.isfile('root://foo.bar.gov//foo/bar/copy.file')
    assert impl.cat('root://foo.bar.gov//foo/bar/copy.file') == impl.cat('root://foo.bar.gov//foo/bar/test.file')

    # remote -> remote, different SE
    impl.cp('root://foo.bar.gov//foo/bar/test.file', 'gsiftp://foo.bar.edu//foo/bar/copy.file')
    assert impl.isfile('gsiftp://foo.bar.edu//foo/bar/copy.file')
    assert impl.cat('gsiftp://foo.bar.edu//foo/bar/copy.file') == impl.cat('root://foo.bar.gov//foo/bar/test.file')

    # local -> remote
    impl.cp('/foo/bar/local.file', 'gsiftp://foo.bar.edu//foo/bar/local.file')
    assert impl.isfile('gsiftp://foo.bar.edu//foo/bar/local.file')
    assert impl.cat('gsiftp://foo.bar.edu//foo/bar/local.file') == 'localcontent'

    # remote -> local
    impl.cp('root://foo.bar.gov//foo/bar/test.file', '/foo/bar/fromremote.file')
    assert seutils.active_fake_internet.fs['<local>'].cat('/foo/bar/fromremote.file') == impl.cat('root://foo.bar.gov//foo/bar/test.file')

    with pytest.raises(seutils.HostUnreachable):
        impl.cp('root://nosuch.host.gov//foo/bar/test.file', '/foo/bar/fromremote.file')
    with pytest.raises(seutils.HostUnreachable):
        impl.cp('/foo/bar/local.file', 'root://nosuch.host.gov//foo/bar/test.file')

    with pytest.raises(seutils.NoSuchPath):
        impl.cp('/no/such/local.file', 'root://foo.bar.gov//foo/bar/dst.file')


# __________________________________________________
# Algos

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_put(impl):
    # Make sure the tempfile exists in the fake local fs, so the `put` does not throw an error
    seutils.active_fake_internet.fs['<local>'].put(
        osp.join(os.getcwd(), 'seutils_tmpfile'), isdir=False, content='localcontent'
        )
    seutils.put('root://foo.bar.gov//foo/bar/new.file', contents='localcontent', implementation=impl)
    assert impl.cat('root://foo.bar.gov//foo/bar/new.file') == 'localcontent'

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_ls(impl):
    seutils.ls('root://foo.bar.gov//foo', implementation=impl) == ['root://foo.bar.gov//foo/bar']

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_walk(impl):
    assert list(seutils.walk('root://foo.bar.gov//foo', implementation=impl)) == [
        ('root://foo.bar.gov//foo', ['root://foo.bar.gov//foo/bar'], []),
        ('root://foo.bar.gov//foo/bar', [], ['root://foo.bar.gov//foo/bar/test.file']),
        ]

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_ls_wildcard(impl):
    seutils.ls_wildcard('root://foo.bar.gov//foo/*/*', implementation=impl) == ['root://foo.bar.gov//foo/bar/test.file']
    seutils.ls_wildcard('root://foo.bar.gov//foo', implementation=impl) == ['root://foo.bar.gov//foo']
    seutils.ls_wildcard('root://foo.bar.gov//foo/', implementation=impl) == ['root://foo.bar.gov//foo']


@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_listdir_recursive(impl):
    fs = seutils.active_fake_internet.fs['root://foo.bar.gov']
    fs.put('root://foo.bar.gov//foo/bla/new.file', isdir=False)
    assert seutils.listdir_recursive('root://foo.bar.gov//foo') == [
        'root://foo.bar.gov//foo/bar',
        'root://foo.bar.gov//foo/bla',
        'root://foo.bar.gov//foo/bar/test.file',
        'root://foo.bar.gov//foo/bla/new.file'
        ]

@pytest.mark.parametrize('impl', implementations, indirect=True)
def test_diff(impl):
    fs1 = seutils.active_fake_internet.fs['root://foo.bar.gov']
    fs1.put('root://foo.bar.gov//foo/bla/new.file', isdir=False)
    fs2 = seutils.active_fake_internet.fs['gsiftp://foo.bar.edu']
    fs2.put('gsiftp://foo.bar.edu//foo/bar/test.file', isdir=False)
    assert seutils.diff('root://foo.bar.gov//foo', 'gsiftp://foo.bar.edu//foo', implementation=impl) == (
        ['root://foo.bar.gov//foo/bar', 'root://foo.bar.gov//foo/bar/test.file'],
        ['gsiftp://foo.bar.edu//foo/bar', 'gsiftp://foo.bar.edu//foo/bar/test.file'],
        ['root://foo.bar.gov//foo/bla', 'root://foo.bar.gov//foo/bla/new.file'],
        ['gsiftp://foo.bar.edu//foo/bar/other.file'],
        )
    # Local paths not yet supported!
    # assert seutils.diff('root://foo.bar.gov//foo', '/foo', implementation=impl) == (
    #     ['root://foo.bar.gov//foo/bar', 'root://foo.bar.gov//foo/bar/test.file'],
    #     ['/foo/bar', '/foo/bar/test.file'],
    #     ['root://foo.bar.gov//foo/bla', 'root://foo.bar.gov//foo/bla/new.file'],
    #     ['/foo/bar/local.file']
    #     )
    with pytest.raises(NotImplementedError):
        seutils.diff('root://foo.bar.gov//foo', '/foo')
    with pytest.raises(NotImplementedError):
        seutils.diff('/foo', 'root://foo.bar.gov//foo')
