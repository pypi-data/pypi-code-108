from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if (attr[0] == "var" and attr[1] == "integrationPath"):
                return True

    # def handle_endtag(self, tag):
    #     print("Encountered an end tag :", tag)

    # def handle_data(self, data):
    #     print("Encountered some data  :", data)