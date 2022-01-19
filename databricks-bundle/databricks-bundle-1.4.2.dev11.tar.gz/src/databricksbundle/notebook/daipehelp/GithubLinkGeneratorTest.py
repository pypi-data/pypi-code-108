import unittest

from pyfonycore.bootstrap import bootstrapped_container
from databricksbundle.notebook.daipehelp.DaipeHelp import DaipeHelp


class GithubLinkGeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.daipe_help = DaipeHelp()

    def test_daipe_import_exists(self):
        from daipecore.widgets.Widgets import Widgets  # noqa: F401

        self.assertEqual(
            self.daipe_help._get_module_github_url(
                Widgets), "https:/github.com/daipe-ai/daipe-core/blob/v1.2.0/src/daipecore/widgets/Widgets.py"
        )

    # def test_daipe_import_not_exists(self):
    #     with self.assertRaises(Exception) as error:
    #         self.daipe_help.daipe_help()

    #     self.assertEqual(
    #         "Specified module could not be found, make sure the the module is imported and developed by DAIPE",
    #         str(error.exception),
    #     )


if __name__ == "__main__":
    unittest.main()
