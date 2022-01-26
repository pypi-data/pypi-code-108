def test_package_import():
    import botcity.plugins.captcha as plugin
    assert plugin.__file__ != ""
