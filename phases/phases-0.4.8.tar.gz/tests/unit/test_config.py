import unittest

from phases.commands.Base import Base


class TestRun(unittest.TestCase):
    projectFolder = "tests/data-gen"
    configFile = "tests/data/min.yaml"
    configFileFull = "tests/importFull.yaml"

    def testLoadConfigMain(self):
        base = Base({})
        fullConfig = base.loadConfig(self.configFile, root=True)
        projectConfig = fullConfig["config"]
        assert projectConfig["before"] == "before"
        assert projectConfig["test"] == "main"
        assert projectConfig["after"] == "after"
        assert projectConfig["overwrite"] == "after"
        assert projectConfig["overwriteMain"] == "main"

        assert projectConfig["beforeF"] == "before"
        assert projectConfig["afterF"] == "after"
        assert projectConfig["overwriteF"] == "after"
        assert projectConfig["overwriteMainF"] == "main"

    def testLoadConfigWithSub(self):
        base = Base({})
        fullConfig = base.loadConfig(self.configFile, root=True)
        subConfig = base.loadConfig(self.configFileFull)
        fullConfig = base.overwriteConfig(fullConfig, subConfig)

        projectConfig = fullConfig["config"]
        assert projectConfig["before"] == "before"
        assert projectConfig["test"] == "main"
        assert projectConfig["after"] == "after"
        assert projectConfig["overwrite"] == "after"
        assert projectConfig["overwriteMain"] == "main"

        assert projectConfig["beforeF"] == "before"
        assert projectConfig["afterF"] == "after"
        assert projectConfig["overwriteF"] == "after"
        assert projectConfig["overwriteMainF"] == "main"
