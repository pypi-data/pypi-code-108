from xml.etree.ElementTree import iterparse


def parse_xml(filename, path):
    path_parts = path.split('/')
    doc = iterparse(filename, ('start', 'end'))

    # # Skip the root element
    next(doc)

    tag_stack = []

    for event, elem in doc:
        if event == 'start':
            tag_stack.append(elem.tag)
        elif event == 'end':
            if tag_stack == path_parts:
                yield elem

            try:
                tag_stack.pop()
            except IndexError:
                pass


data = parse_xml('xunitresults.xml', 'testcase')

print(data)
for d in data:
    system_out = d.findtext("system-out")
    print("--- system-out:\n")
    print(system_out)
    print("===" * 30)
    failure = d.findtext("failure")
    print("--- failure:\n")
    print(failure)
    print("---" * 30)
    print("\n")

import xml.etree.cElementTree as ET

tree = ET.ElementTree(file="xunitresults.xml")
root = tree.getroot()
# print(root.tag)
print(root.attrib)


#todo: not save the logs into db after each execution done?
# how about: scan the output folder and fetch all the info then genreate the xml file than conver the xml into DB ?
#  benifit: if there are 100 testcases need to be run, but the execution interruped when 90 testcases's execution done,
#  than we can only run the left 10 testcases, and conver the xml into DB.(set the execution_id manually for the second run?)
