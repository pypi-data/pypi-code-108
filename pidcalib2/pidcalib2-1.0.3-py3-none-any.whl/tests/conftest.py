def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "xrootd: tests requiring xrootd EOS auth. (deselect with '-m \"not xrootd\"')",
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "pyroot: tests requiring PyROOT (deselect with '-m \"not pyroot\"')"
    )
