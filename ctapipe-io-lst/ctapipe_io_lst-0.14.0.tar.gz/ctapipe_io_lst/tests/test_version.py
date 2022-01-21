def test_version():
    from ctapipe_io_lst import __version__

    assert __version__ != 'unknown'
