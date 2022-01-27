import unittest
import requests
from quickspider.core.nodes import (GetNode, PostNode, ParserNode,
        ParserDomNode, SplitNode, ConcatNode, PrintNode, PageNode, CsvReaderNode,
        ExcelReaderNode, LineReaderNode, JsonWriterNode, CsvWriterNode)
from scrapy import Selector


class TestNodes(unittest.TestCase):

    def test_GetNode(self):
        getnode = GetNode("test")
        getnode._set_input("https://httpbin.org/get")
        status, resp = getnode.activate()
        self.assertTrue(status)
        self.assertEqual(resp.status_code, 200)

    def test_PostNode(self):
        postnode = PostNode("test")
        postnode._set_input("https://httpbin.org/post")
        postnode._set_data({"test": "test_node"})
        status, resp = postnode.activate()
        self.assertTrue(status)
        self.assertEqual(resp.status_code, 200)

    def test_ParserNodeDom(self):
        resp = requests.get("https://baidu.com")
        parsernode = ParserNode("test", "dom")
        parsernode._set_input(resp)
        status, selector =  parsernode.activate()
        self.assertTrue(status)

    def test_ParserNodeJson(self):
        data = {"test": "test_json"}
        resp = requests.post("https://httpbin.org/post", json=data)
        parsernode = ParserNode("test", "json")
        parsernode._set_input(resp)
        status, jsondata =  parsernode.activate()
        self.assertTrue(status)
        self.assertDictEqual(eval(jsondata["data"]), data)

    def get_selector(self):
        test_dom_text = """
        <body>
        <h1>Method Not Allowed</h1>
        <p>The method is not allowed for the requested URL.</p>
        </body>
        """
        test_dom = Selector(text=test_dom_text)
        parserdomnode = ParserDomNode("test", "css", "p::text")
        parserdomnode._set_input(test_dom)
        status, selector = parserdomnode.activate()
        return status, selector

    def test_ParserDomNode(self):
        status, selector = self.get_selector()
        self.assertTrue(status)

    def test_SplitNode(self):
        _, selector = self.get_selector()
        splitnode = SplitNode("test")
        splitnode._set_input(selector)
        status, result = splitnode.activate()
        self.assertTrue(status)
        self.assertEqual(result, "The method is not allowed for the requested URL.")

    def test_ConcatNode(self):
        _, selector = self.get_selector()
        concatnode = ConcatNode("test")
        concatnode._set_input(selector)
        status, result = concatnode.activate()
        self.assertTrue(status)
        self.assertEqual(result, "The method is not allowed for the requested URL.")

    def test_PrintNode(self):
        printnode = PrintNode("test")
        printnode._set_input("test passed")
        status, result = printnode.activate()
        self.assertTrue(status)

    def test_PageNode(self):
        pagenode = PageNode("test", "test/{page}", 1, 4)
        page = 1
        status, output = pagenode.activate()
        while status:
            if not status:
                break
            self.assertEqual(output, "test/{page}".format(page=page))
            page += 1
            try:
                status, output = pagenode.activate()
            except Exception as e:
                break


if __name__ == '__main__':
    unittest.main()
