import unittest
import requests
from quickspider.core.nodes import (GetNode, PostNode, ParserNode,
        ParserDomNode, ExtractNode, ConcatNode, PrintNode, PageNode, CsvReaderNode,
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
        self.assertIsInstance(selector, Selector)

    def test_ParserNodeJson(self):
        data = {"test": "test_json"}
        resp = requests.post("https://httpbin.org/post", json=data)
        parsernode = ParserNode("test", "json")
        parsernode._set_input(resp)
        status, jsondata =  parsernode.activate()
        self.assertTrue(status)
        self.assertDictEqual(jsondata["data"], data)

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
        self.assertIsInstance(selector, Selector)
        return selector

    def test_ExtractNode(self):
        _, selector = self.get_selector()
        extractnode = ExtractNode("test")
        extractnode._set_input(selector)
        status, result = extractnode.activate()
        self.assertTrue(status)
        self.assertEqual(result, ["The method is not allowed for the requested URL."])

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
        print(result)

    def test_PageNode(self):
        pagenode = PageNode("test", "test/{page}", 1, 4)
        page = 1
        status, output = pagenode.activate()
        while status:
            status, output = pagenode.activate()
            if not status:
                break
            self.assertEqual(output, f"test/{page}")
            page += 1


