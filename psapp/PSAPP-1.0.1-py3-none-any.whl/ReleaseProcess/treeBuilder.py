import xml.etree.ElementTree as ET


class MyTreeBuilder(ET.TreeBuilder):
   
   def comment(self, data):
       self.start(ET.Comment, {})
       self.data(data)
       self.end(ET.Comment)