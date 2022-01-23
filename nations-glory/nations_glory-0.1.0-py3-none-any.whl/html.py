import re
from typing import Tuple
import requests as https
import json as JSON
from html_to_json import convert as html_to_json

class Element():

    def feed(self, parent, tag: str, data: dict):
        if type(data) is not dict:
            return None

        self.parent: Element = parent
        self.tag: str = tag
        self.attributes: dict = data.get('_attributes')

        if data.get('_values') != None:
            self.innerHTML: str = '\n'.join(data.get('_values'))
        elif data.get('_value') != None:
            self.innerHTML: str = data.get('_value')
        else:
            self.innerHTML = None

        self.children: list[Element] = []

        for tag in data:
            if tag != '_attributes' and tag != '_values' and tag != '_value':
                for child in data.get(tag):
                    self.children.append(Element().feed(self, tag, child))
        
        return self

    def as_html(self, indent: str = '    ', margin: int = 0):
        left = ''
        for i in range(0, margin):
            left += indent

        attributes = ''
        for key in (self.attributes or {}).keys():
            attributes += ' %s="%s"' % (
                key, 
                ' '.join(self.attributes[key]) if isinstance(self.attributes[key], list) else self.attributes[key]
            )

        lines = ["%s<%s%s>" % (left, self.tag, attributes)]


        if len(self.children) > 0:
            if self.innerHTML != None:
                lines.append(left + self.innerHTML)
            for child in self.children:
                lines.append(child.as_html(indent, 1))
        else:
            return lines[0] + self.innerHTML + "</%s>" % self.tag

        lines.append("</%s>" % self.tag)

        return ('\n' + left).join(lines)

    def find(
        self, 
        tag: str = None, 
        id: str = None, 
        classes: list[str] = [], 
        attributes: dict = None, 
        innerMatch: Tuple[str, str] = None
    ):
        for child in self.children:
            if child == None:
                continue

            if (
                (tag == None or child.tag == tag) and 
                (id == None or child.id == id) and
                (innerMatch == None or (
                    child.innerHTML != None and
                    re.match(innerMatch[0], child.innerHTML, innerMatch[1] or 0)
                ))
            ):
                classesMatch = True
                for class_ in classes:
                    if child.classes == None or not class_ in child.classes:
                        classesMatch = False

                attributesMatch = True
                if type(attributes) is dict: 
                    for attr in attributes:
                        if child.get_attr(attr) != attributes.get(attr):
                            attributesMatch = False

                if classesMatch and attributesMatch:
                    return child

            child_found = child.find(tag, id, classes, attributes, innerMatch)
            if child_found != None:
                return child_found

        return None

    def get_classes(self) -> list[str]:
        return self.get_attr('class')

    def set_classes(self, classes: list[str]):
        self.set_attr('class', classes)

    classes: list[str] = property(get_classes, set_classes)

    def get_id(self) -> str:
        return self.get_attr('id')

    def set_id(self, id: str):
        self.set_attr('id', id)

    id: str = property(get_id, set_id)

    def get_attr(self, key: str) -> str:
        return self.attributes.get(key)

    def set_attr(self, key: str, value: str):
        self.attributes.set(key, value)

class Dom(Element):
    def from_url(url: str):
        html = https.get(url).text
        doc = html_to_json(html)
        return Dom(doc)

    def __init__(self, doc: dict):
        self.feed(None, 'document', doc)