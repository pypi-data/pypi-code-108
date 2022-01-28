import pytest
import fakefs
import seutils
import os, os.path as osp
import copy

# _______________________________________________________________________
# Test rm safety on actual storage element

@pytest.mark.real_integration
def test_rm_safety_xrd():
    run_rm_safety_test(seutils.XrdImplementation())

@pytest.mark.real_integration
def test_rm_safety_gfal():
    run_rm_safety_test(seutils.GfalImplementation())

def run_rm_safety_test(impl):
    if not impl.isdir('root://cmseos.fnal.gov//store/user/klijnsma/foo/bar'):
        impl.mkdir('root://cmseos.fnal.gov//store/user/klijnsma/foo/bar')
    bl_backup = copy.copy(seutils.RM_BLACKLIST)
    seutils.RM_BLACKLIST.extend(['/store/user/klijnsma/foo', '/store/user/klijnsma/foo/*'])
    try:
        with pytest.raises(seutils.RmSafetyTrigger):
            impl.rm('root://cmseos.fnal.gov//store/user/klijnsma/foo')
        with pytest.raises(seutils.RmSafetyTrigger):
            impl.rm('root://cmseos.fnal.gov//store/user/klijnsma/foo/bar')
    finally:
        seutils.RM_BLACKLIST = bl_backup
    if impl.isdir('root://cmseos.fnal.gov//store/user/klijnsma/foo/bar'):
        impl.rm('root://cmseos.fnal.gov//store/user/klijnsma/foo/bar', recursive=True)
        impl.rm('root://cmseos.fnal.gov//store/user/klijnsma/foo', recursive=True)
    assert not impl.isdir('root://cmseos.fnal.gov//store/user/klijnsma/foo')

# _______________________________________________________________________
# Test other functionality in one go

def activate_fake_internet():
    seutils.debug()
    seutils.logger.debug('Setting up fake internet')
    fi = fakefs.FakeInternet()
    fs = fakefs.FakeRemoteFS('root://cmseos.fnal.gov')
    fs.put('/store/user/klijnsma', isdir=True)
    fs_local = fakefs.FakeFS()
    fs_local.put(osp.join(os.getcwd(), 'seutils_tmpfile'), isdir=False, content='testcontent')
    fi.fs = {'root://cmseos.fnal.gov' : fs, '<local>' : fs_local }
    seutils.logger.debug('Setup; test nodes: %s', fi.fs['root://cmseos.fnal.gov'].nodes)
    fakefs.activate_command_interception(fi)

def test_fake_integration_xrd():
    activate_fake_internet()
    run_implementation_tests(seutils.XrdImplementation(), 'root://cmseos.fnal.gov//store/user/klijnsma/seutils_testdir')
    fakefs.deactivate_command_interception()

def test_fake_integration_xrd():
    activate_fake_internet()
    run_implementation_tests(seutils.GfalImplementation(), 'root://cmseos.fnal.gov//store/user/klijnsma/seutils_testdir')
    fakefs.deactivate_command_interception()

@pytest.mark.real_integration
def test_real_integration_xrd():
    run_implementation_tests(seutils.XrdImplementation(), 'root://cmseos.fnal.gov//store/user/klijnsma/seutils_testdir')

@pytest.mark.real_integration
def test_real_integration_gfal():
    run_implementation_tests(seutils.GfalImplementation(), 'root://cmseos.fnal.gov//store/user/klijnsma/seutils_testdir')

def run_implementation_tests(impl, remote_test_dir):
    '''Run integration tests in one order to not overload the SE'''
    # Setup and testing contents
    impl.mkdir(remote_test_dir)
    assert impl.isdir(remote_test_dir)
    remote_test_file = osp.join(remote_test_dir, 'test.file')
    seutils.put(remote_test_file, contents='testcontent', implementation=impl)
    assert impl.isfile(remote_test_file)
    assert not impl.isdir(remote_test_file)
    assert impl.listdir(remote_test_dir) == [remote_test_file]
    assert impl.cat(remote_test_file) == 'testcontent'
    # Copying
    remote_test_file_copy = remote_test_file + '.copy'
    impl.cp(remote_test_file, remote_test_file_copy)
    assert impl.isfile(remote_test_file_copy)
    assert impl.cat(remote_test_file_copy) == 'testcontent'
    # Cleanup
    seutils.RM_WHITELIST = [seutils.split_mgm(remote_test_dir)[1]]
    impl.rm(remote_test_file)
    assert not impl.isfile(remote_test_file)
    impl.rm(remote_test_file_copy)
    assert not impl.isfile(remote_test_file_copy)
    impl.rm(remote_test_dir, recursive=True)
    assert not impl.isdir(remote_test_dir)
    seutils.RM_WHITELIST = []


@pytest.mark.real_integration
def test_diff_gfal():
    def put_if_not_exists(path, contents):
        if not seutils.isfile(path, implementation=seutils.gfal):
            seutils.put(path,contents=contents, implementation=seutils.gfal)
    put_if_not_exists(
        'gsiftp://hepcms-gridftp.umd.edu//mnt/hadoop/cms/store/user/thomas.klijnsma/difftest/file1.txt',
        contents='contents1'
        )
    put_if_not_exists(
        'gsiftp://hepcms-gridftp.umd.edu//mnt/hadoop/cms/store/user/thomas.klijnsma/difftest/file2.txt',
        contents='contents2'
        )
    put_if_not_exists(
        'root://cmseos.fnal.gov//store/user/klijnsma/difftest/file1.txt',
        contents='contents1'
        )
    if seutils.gfal.isfile('root://cmseos.fnal.gov//store/user/klijnsma/difftest/file2.txt'):
        seutils.gfal.rm('root://cmseos.fnal.gov//store/user/klijnsma/difftest/file2.txt')
    d = seutils.diff(
            'gsiftp://hepcms-gridftp.umd.edu//mnt/hadoop/cms/store/user/thomas.klijnsma/difftest',
            'root://cmseos.fnal.gov//store/user/klijnsma/difftest',
            implementation=seutils.gfal
            )
    assert d == (
        ['gsiftp://hepcms-gridftp.umd.edu//mnt/hadoop/cms/store/user/thomas.klijnsma/difftest/file1.txt'],
        ['root://cmseos.fnal.gov//store/user/klijnsma/difftest/file1.txt'],
        ['gsiftp://hepcms-gridftp.umd.edu//mnt/hadoop/cms/store/user/thomas.klijnsma/difftest/file2.txt'],
        []
        )
