import requests
import unittest
from unittest.mock import patch, MagicMock

from top_hack import top_hack


class TestTopHack(unittest.TestCase):
    def test_get_html(self):

        with patch("top_hack.top_hack.requests") as mock:

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = ""

            mock_session = MagicMock()
            mock_session.get.return_value = mock_response
            mock.Session.return_value = mock_session

            app = top_hack.TopHack()

            html = app._get_html()

            self.assertIsInstance(html, str)

    def test_init(self):

        app = top_hack.TopHack()

        self.assertEqual(app.url, "https://news.ycombinator.com")
        self.assertIsInstance(app.session, requests.Session)
        self.assertIsInstance(app.amount, int)
        self.assertIsInstance(app.min_score, int)
        self.assertIsInstance(app.results, list)
        self.assertIsInstance(app.sleep, int)

    def test_get_urls(self):

        title = "Best search engine"
        url = "https://google.com"
        score = 100
        html = f"""
<div class="athing">
    <div class="title">
        <a
            class="titlelink"
            href="{url}">{title}</a>
    </div>
</div>
<span class="score">{score} points</span>
        """

        app = top_hack.TopHack(min_score=100)

        app._get_urls(html)

        self.assertEqual(len(app.results), 1)

        result = app.results[0]

        self.assertEqual(result["title"], title)
        self.assertEqual(result["url"], url)
        self.assertEqual(result["score"], score)

    def test_filter(self):

        title = "Best search engine"
        url = "https://google.com"
        score = 1
        html = f"""
<div class="athing">
    <div class="title">
        <a
            class="titlelink"
            href="{url}">{title}</a>
    </div>
</div>
<span class="score">{score} points</span>
        """

        app = top_hack.TopHack(min_score=100)

        app._get_urls(html)

        app._filter()

        self.assertEqual(len(app.results), 0)

        score = 100
        html = f"""
<div class="athing">
    <div class="title">
        <a
            class="titlelink"
            href="{url}">{title}</a>
    </div>
</div>
<span class="score">{score} points</span>
        """

        app._get_urls(html)

        app._filter()
        self.assertEqual(len(app.results), 1)

    def test_sort(self):

        html = f"""
<div class="athing">
    <div class="title">
        <a
            class="titlelink"
            href="https://googlle.com">Foo</a>
    </div>
</div>
<span class="score">100 points</span>

<div class="athing">
    <div class="title">
        <a
            class="titlelink"
            href="https://duck.com">Duck</a>
    </div>
</div>
<span class="score">200 points</span>
        """

        app = top_hack.TopHack(min_score=100)

        app._get_urls(html)

        app._sort()

        self.assertEqual(app.results[0]["title"], "Duck")

    def test_run(self):

        with patch("top_hack.top_hack.requests") as mock:

            html = f"""
    <div class="athing">
        <div class="title">
            <a
                class="titlelink"
                href="https://googlle.com">Foo</a>
        </div>
    </div>
    <span class="score">100 points</span>

    <div class="athing">
        <div class="title">
            <a
                class="titlelink"
                href="https://duck.com">Duck</a>
        </div>
    </div>
    <span class="score">200 points</span>
            """

            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html
            mock_session.get.return_value = mock_response

            mock.Session.return_value = mock_session
            app = top_hack.TopHack(min_score=100, amount=2, sleep=0)
            results = app.run()

            self.assertTrue(len(results), 2)
