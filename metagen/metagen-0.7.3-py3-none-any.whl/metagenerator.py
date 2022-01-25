#!/usr/bin/python3
import sys
from xml.dom import minidom

from lxml import etree
from lxml.etree import Element, SubElement
from portage.output import red


class MyMetadata:

    """Create Gentoo Linux metadata.xml"""

    class _Maintainer:
        def __init__(self, type_=None, email=None, name=None, description=None):
            self.type_ = type_
            self.email = email
            self.name = name
            self.description = description

    def __init__(self):
        self._maintainers = []
        self._long_description = None

    def set_maintainer(self, emails, names, descs, types):
        """Set maintainer(s)'s email, name, desc"""
        if len(types) != len(emails):
            if len(types) != 1:
                print(red("!!! Nbr maintainer types != nbr emails"))
                sys.exit(1)
            types = [types[0] for _ in emails]

        i = 0
        for e in emails:
            maintainer = self._Maintainer(type_=types[i], email=e)
            if names:
                if len(names) > len(emails):
                    print(red("!!! Nbr names > nbr emails"))
                    sys.exit(1)
                if i <= len(names) -1:
                    maintainer.name = names[i]
            if descs:
                if len(descs) > len(emails):
                    print(red("!!! Nbr descs > nbr emails"))
                    sys.exit(1)
                if i <= len(descs) -1:
                    maintainer.description = descs[i]
            i += 1
            self._maintainers.append(maintainer)

    def set_longdescription(self, longdesc):
        """Set package's long description."""
        self._long_description = longdesc

    def __str__(self):
        doctype = '<!DOCTYPE pkgmetadata SYSTEM "https://www.gentoo.org/dtd/metadata.dtd">'
        root = Element('pkgmetadata')

        for maintainer_data in self._maintainers:
            maintainer_element = SubElement(root, 'maintainer')
            maintainer_element.set('type', maintainer_data.type_)
            if maintainer_data.email:
                SubElement(maintainer_element, 'email').text = maintainer_data.email
            if maintainer_data.name:
                SubElement(maintainer_element, 'name').text = maintainer_data.name
            if maintainer_data.description:
                SubElement(maintainer_element, 'description').text = maintainer_data.description

        if self._long_description:
            long_description = SubElement(root, 'longdescription')
            long_description.text = self._long_description

        xml_text = etree.tostring(root, xml_declaration=True, doctype=doctype)

        # Re-write indentation to tabulators
        # (for backwards compatibility and smaller diffs with existing files)
        reparsed = minidom.parseString(xml_text)
        xml_text = reparsed.toprettyxml(indent='\t', encoding='UTF-8').decode()

        # Get doctype back on a single line
        # - for compatibility with output produced by metagen <0.7
        # - to make pkgcheck stop from warning about PkgMetadataXmlIndentation
        return xml_text.replace('<!DOCTYPE pkgmetadata\n  SYSTEM',
                                '<!DOCTYPE pkgmetadata SYSTEM')


def do_tests():
    from metagen import meta_unittest
    fails = 0
    for func in dir(meta_unittest):
        if func[0:4] == "test":
            try:
                exec("print(meta_unittest.%s.__name__ + ':', end='')" % func)
                exec("print(meta_unittest.%s.__doc__)" % func)
                exec("print(meta_unittest.%s())" % func)
            except:
                fails += 1
                print("Test %s failed:" % func)
                print(sys.exc_info()[0], sys.exc_info()[1])
    print("%s tests failed." % fails)

if __name__ == "__main__":
    do_tests()
