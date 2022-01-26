"""Displays the ElementTree instances created as a response from a **PSquared** server.
"""

from __future__ import print_function

PADDING = len('  1970-01-01T00:00:000000-00:00 SUBMITTED ')

def configurations(application):
    """Displays all the configurations contained in an application document

    :param ElementTree application: the application document whose configurations should be displayed.
    """

    c = application.findall('configurations/configuration')
    print('Currently active configurations:')
    for config in c:
         if None == config.find('description') or None == config.find('description').text:
             descriptionToUse = ""
         else:
             descriptionToUse = ': ' + config.find('description').text
         print("  " + config.find('name').text + descriptionToUse)
    print()


def versions(configuration):
    """Displays all the versions of a named configuration

    :param ElementTree configuration: the configuration document whose versions should be displayed.
    """

    v = configuration.find('default-version')
    if None == v or None == v.text:
        defaultUrl = None
        defaultNote = ''
    else:
        defaultUrl = v.text
        defaultNote = " (* indicates the default version)"
    v = configuration.findall('known-versions/known-version')
    print('Currently active version for configuration "' + configuration.find('name').text + '"' + defaultNote)
    for vers in v:
        if defaultUrl == vers.find('uri').text:
            header = "* "
        else:
            header = "  "
        if None == vers.find('description') or None == vers.find('description').text:
            descriptionToUse = ""
        else:
            descriptionToUse = ': ' + vers.find('description').text
        print(header + vers.find('name').text + descriptionToUse)
    print()


def entry(e, name = None, max = 0, changed = False):
    """Displays the state of the specified entry.

    :param str name: the name
    :param int max: the maximum print width of the label of the entry.
    :param bool changed: True if the entry should be maked a having changed.
    """

    if None == name:
        label = ''
    else:
        padding = max - len(name)
        if 0 > padding:
            label = name + ' ' * padding
        else:
            label = name[0:max]
        label = label + ' : '
    if None == changed:
        status = 'C    '
    else:
        status = '    '
    header = status + label + e.find('completed').text + ' ' + e.find('state').text
    message = e.find('message')
    if None == message or None == message.text:
        messageToUse = ''
    else:
        messageToUse = message.text.replace('\n', '\n' + ' ' * (PADDING) )
    print(header +  ' ' * (PADDING + (max + 3) - len(header)) + messageToUse)


def info(name, version, report, items = None, note = None):
    """Displays the state of items as contained in the specified report.

    :param str name: the name of the configuration whose items are being supplied.
    :param str version: the version of the named configuration whose items are being supplied.
    :param ElementTree report: the report document containing the states to be displayed.
    :param list[str] items: the subset of items in the report to be display, any not in the report will be ignored.
    :param str note: the alternate note to be printed before each entry.
    """

    item_element = 'realized-state'
    item_entry = 'entry'
    states = report.findall(item_element)
    if None == states or 0 == len(states):
        item_element = 'synopsis'
        item_entry = '.'
        states = report.findall(item_element)
    item_xpath = item_element + '/item'
    if None == items:

        # This is the case when there was no set of items explicitly requested.
        if 0 == len(states):
            print('There are no items to report on for version "' + version + '" of configuration "' + name + '"')
            return
        print('Results for version "' + version + '" of configuration "' + name + '"')
        names = report.findall(item_xpath)
        max = 0
        for n in names:
            name = n.text
            if len(name) > max:
                max = len(name)
        for state in states:
            entry(state.find(item_entry), state.find('item').text, max)
        return

    if 0 == len(items):
        print('There are no items to report on for version "' + version + '" of configuration "' + name + '"')
        return

    index = 0
    if index == len(states):
        state = None
    else:
        state = states[index]
    for item in items:
        if None != state and item == state.find('item').text:
            if None == note:
                print('Current state of of "' + item + '" with version "' + version + '" of configuration "' + name + '"')
            else:
                print(note)
            entry(state.find(item_entry), changed = (None == state.find('unchanged')))
            print
            index += 1
            if index == len(states):
                state = None
            else:
                state = states[index]
        else:
            print('There has been no processing of "' + item + '" with version "' + version + '" of configuration "' + name + '"')
            print()


def histories(configuration, version, report, items):
    """Displays the histories of items as contained in the specified report.

    :param str name: the name of the configuration whose items are being supplied.
    :param str version: the version of the named configuration whose items are being supplied.
    :param ElementTree report: the report document containing the states to be displayed.
    :param list[str] items: the subset of items in the report to be display, any not in the report will be ignored.
    """

    histories = report.findall('history')
    index = 0
    if index == len(histories):
        history = None
        print('There is no History for the requested item with version "' + version + '" of configuration "' + configuration + '"')
        return
    else:
        history = histories[index]
    for item in items:
        if None != history and item == history.find('current-state/item').text:
            print('History of "' + item + '" with version "' + version + '" of configuration "' + configuration + '"')
            entries=history.findall('.//entry')
            entries.reverse()
            for e in entries:
                entry(e)
            print
            index += 1
            if index == len(histories):
                history = None
            else:
                history = histories[index]
        else:
            print('There is no History of "' + item + '" with version "' + version + '" of configuration "' + configuration + '"')
            print()
