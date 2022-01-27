from unittest import TestCase
from unittest.mock import patch, MagicMock

from top_hack import cli


class TestCli(TestCase):
    def test_main(self):

        results = [
            {
                "url": "https://google.com",
                "score": 100,
                "title": "Best search",
                "comment_url": "https://google.com/some",
            },
            {
                "url": "https://duck.com",
                "score": 200,
                "title": "Private search",
                "comment_url": "https://duck.com/comments",
            },
        ]

        with patch("top_hack.cli.TopHack") as mock:

            with patch("top_hack.cli.argparse") as _:
                with patch("builtins.print") as mock_print:

                    with patch("builtins.input") as mock_input:

                        with patch("top_hack.cli.webbrowser") as mock_browser:

                            mock_app = MagicMock()
                            mock_app.run.return_value = results
                            mock.return_value = mock_app

                            mock_input.side_effect = ("1", "o", "q")

                            ret_val = cli.main()

                            presentation = ""

                            for idx, result in enumerate(results):
                                presentation += f"[{idx}] {result['title']} ({result['score']})\n"  # noqa: E501

                            mock_print.assert_called_with(presentation)

                            mock_browser.open.assert_called_once()

                            self.assertEqual(ret_val, 0)
