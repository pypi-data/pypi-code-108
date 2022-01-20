import unittest
from catswalk.scraping.request import CWRequest


class TestCWRequest(unittest.TestCase):
    def test_get(self):
        """[python -m unittest tests.scraping.test_request.TestCWRequest.test_get]
        """
        #request = CWRequest()
        #responseHtml = request.get(url="https://yahoo.co.jp", response_content_type="html")
        #print(responseHtml)
        #request.close()
        with CWRequest() as request:
            responseHtml = request.get(url="https://yahoo.co.jp", response_content_type="html")
            print(responseHtml)
        

if __name__ == "__main__":
    unittest.main()