"""
  Implements utility functions for manipulation of .properties files.
"""
import os


def get_properties(file_path):
    # Note that there is a Java properties file read/write library call pyjavaproperties. Unfortunately, it is
    # exactly equivalent to the java.util.Properties class, which has problems as mentioned in seeq-utilities'
    # GlobalProperties.java. That's why we have our own properties parsing code here.
    properties = {}

    if not os.path.exists(file_path):
        return properties

    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()

    for line in lines:
        if '=' not in line:
            continue

        key = line[:line.find("=")]
        value = line[line.find("=") + 1:]

        properties[key.strip()] = value.strip()

    return properties
