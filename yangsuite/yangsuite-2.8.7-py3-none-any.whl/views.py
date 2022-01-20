# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

"""Baseline views provided by yangsuite itself."""

import os
import json
import logging
import re
import configparser
import hashlib
from collections import OrderedDict

from django.apps import apps
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import site as my_admin_site
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import escape as html_escape
from django.contrib.staticfiles import finders

from yangsuite.application import read_prefs, write_prefs, check_eula
from yangsuite.logs import get_logger
from yangsuite.paths import get_path
from yangsuite.plugins import (
    get_plugin_versions, check_for_plugin_updates,
    python_report, update_plugins,
)
from ysdevices.devprofile import YSDeviceProfile

log = get_logger(__name__)


def json_request(decoratee):
    """View decorator for views that expect a request in JSON format."""
    def decorated(request, *args, **kwargs):
        jsondata = {}
        if request.body:
            try:
                jsondata = json.loads(request.body.decode('utf-8'),
                                      object_pairs_hook=OrderedDict)
                if 'csrfmiddlewaretoken' in jsondata:
                    del jsondata['csrfmiddlewaretoken']
            except json.decoder.JSONDecodeError:
                return JsonResponse({}, status=400,
                                    reason="Malformed JSON request")
        return decoratee(request, *args, jsondata=jsondata, **kwargs)
    decorated.__doc__ == decoratee.__doc__
    return decorated


@login_required
@user_passes_test(check_eula, redirect_field_name='eula')
def user_profile_view(request):
    """Display details of logged-in user."""
    return render(request, "yangsuite/user_profile.html",
                  {'user': User.objects.get(username=request.user.username)})


@login_required
@user_passes_test(check_eula, login_url='eula')
def enable_gtm(request):
    """Disable Google Tag Manager for developer accounts."""
    # Check for the hashed userid.
    user_hash = os.environ.get('USER_HASH', None)
    if user_hash is None:
        # hash the username
        salt = os.urandom(10)
        hash_obj = hashlib.pbkdf2_hmac('sha256',
                                       request.user.username.encode('utf-8'),
                                       salt, 100000)
        hex_dig = hash_obj.hex()
        hashed_id = hex_dig + request.user.password
        os.environ['USER_HASH'] = hashed_id
        user_hash = os.environ['USER_HASH']

    gtmid = 'GTM-D2TQZX2'
    gtm_file_path = os.path.join(os.path.dirname(__file__), 'data/gtm.txt')
    # Pick the gtm id for production install
    if os.path.exists(gtm_file_path):
        with open(gtm_file_path, 'r') as fd:
            gtmid = fd.read()
    # Get the device count per user
    devcount = 0
    ysdevlist = YSDeviceProfile.list()
    if ysdevlist:
        devcount = len(ysdevlist)
    company = ''
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'mode.py')) or \
       request.user.username == 'yangsuite-developer':
        # to check if its a Demo package or developer account
        return JsonResponse(
            {
                'enable_gtm': False
            }
        )
    elif request.user.email:
        email_pattern = "^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"
        if (re.search(email_pattern, request.user.email)):
            company = request.user.email.split('@')[1].split('.')[0]
            if company != 'gmail':
                return JsonResponse(
                    {
                        'enable_gtm': True,
                        'gtmid': gtmid,
                        'userid': user_hash,
                        'company': company,
                        'device_count': devcount,
                    }
                )
            else:
                return JsonResponse(
                    {
                        'error': 'company'
                    }
                )
        else:
            return JsonResponse(
                {
                    'error': 'invalid_email'
                }
            )
    else:
        return JsonResponse(
            {
                'error': 'no_email'
            }
        )


@login_required
@user_passes_test(check_eula, login_url='eula')
def save_email(request):
    """Save User email id to database"""
    user = User.objects.get(username=request.user.username)
    result = {}
    try:
        email = request.POST.get('email')
        regex = "^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"
        if (re.search(regex, email)):
            if "@gmail" not in email:
                user.email = request.POST.get('email')
                user.save()
                result['reply'] = "Email Saved successfully"
                return JsonResponse(result)
            else:
                return JsonResponse({}, status=500,
                                    reason='Please enter a valid ' +
                                    'company email ID')
        else:
            return JsonResponse({}, status=500,
                                reason='Invalid email!!.' +
                                'Please enter a valid email ID')
    except Exception as e:
        return JsonResponse({}, status=500, reason=str(e))


@staff_member_required
def log_view(request):
    """Admin-only view of the yang-suite log file."""
    context = my_admin_site.each_context(request)
    context['title'] = 'YANG Suite logs'
    context['is_popup'] = False
    return render(request, 'yangsuite/logs.html', context)


@user_passes_test(check_eula, login_url='eula')
@staff_member_required
def get_log(request):
    """Admin-only get log contents as JSON."""
    verbosity = logging.getLevelName(request.GET.get('levelname', 'INFO'))
    maxlines = int(request.GET.get('maxlines', '100'))

    data = _get_log_from_file(get_path('logfile',
                                       filename='yangsuite.log.json'),
                              maxlines, verbosity)
    for record in data:
        # Make the 'message' field HTML-safe (escaping &"'<> characters)
        record['message'] = html_escape(record['message'])
        # If there are newlines in the message, split it into paragraphs
        if "\n" in record['message']:
            record['message'] = (
                "<p>" + "</p><p>".join(record['message'].split("\n")) + "</p>")

    # 'asctime' and 'msecs' are two separate fields, but it's more useful
    # to merge these under a single 'timestamp' key as well:
    for record in data:
        record['timestamp'] = "{0}.{1:03d}".format(
            record.get('asctime', '????-??-?? ??:??:??'),
            int(record.get('msecs', 0)))
    return JsonResponse({'result': data})


def _get_log_from_file(basename, maxlines, verbosity):
    """Due to log rotation we may not get everything we need from a single file.

    This function will loop as needed until running out of files or getting
    the requested maxlines.

    Args:
      basename (str): Base log name, e.g. "yangsuite.log.json". Rotated older
        logs are presumed to be basename.1, basename.2, etc.
      maxlines (int): Maximum number of lines to retrieve
      verbosity (int): Maximum logging level to filter by
    Returns:
      list: List of no more than maxlines dicts, each representing a single
        log entry
    """
    number = 0
    data = []
    filename = basename

    #
    # Generating log messages while retrieving log entries is likely a problem.
    #
    # log.debug("maxlines: {0} verbosity: {1}".format(maxlines, verbosity))

    while os.path.exists(filename):
        # log.debug("Checking file {0}".format(filename))
        new_data = []
        with open(filename, 'r') as logfile:
            for line in logfile:
                try:
                    new_data.append(json.loads(line))
                except ValueError:
                    new_data.append({
                        'levelname': 'ERROR',
                        'message': 'Malformed JSON entry:\n' + str(line)})

        # log.debug("Got {0} lines from {1}".format(len(new_data), filename))

        # Filter the data by verbosity
        new_data = [entry for entry in new_data if
                    logging.getLevelName(entry['levelname']) >= verbosity]

        # log.debug("After filtering by verbosity, {0} lines remain".format(
        #               len(new_data)))

        data = (new_data + data)[-maxlines:]

        if len(data) >= maxlines:
            break

        # log.debug("Still have only {0}/{1} lines, continuing".format(
        #               len(data), maxlines))

        number += 1
        filename = "{0}.{1}".format(basename, number)

    return data


@user_passes_test(check_eula, login_url='eula')
@login_required
def plugins(request):
    """Page to display installed plugins.

    Returns:
      django.http.HttpResponse: rendered plugins.html page
    """
    return render(request, 'yangsuite/plugins.html')


@user_passes_test(check_eula, login_url='eula')
@login_required
def list_plugins(request):
    """List the installed YANG Suite plugins.

    Returns:
      django.http.JsonResponse: {'plugins': [list of dicts]}
    """
    return JsonResponse({'plugins': get_plugin_versions()})


@user_passes_test(check_eula, login_url='eula')
@login_required
def check_plugins(request):
    """Check upstream repository for new versions of installed plugins.

    Since this involves network operations it can be somewhat slow,
    which is why this should be invoked as an AJAX call rather than
    as part of the page load in :func:`plugins` above.

    Returns:
      django.http.JsonResponse: {'apps': [{'package_name': 'yangsuite', ...}]}
    """
    return JsonResponse({'apps': check_for_plugin_updates()})


@user_passes_test(check_eula, login_url='eula')
@staff_member_required
def update_plugins_view(request):
    """Update the requested plugin(s).

    Args:
      request (django.http.HttpRequest): with key 'plugins' describing a list
        of {plugin, version} dictionaries.

    Returns:
      django.http.JsonResponse:
      ``{'result': {'plugins': {'pluginname': 'updated'}, 'message': ''}}``
    """
    plugins = json.loads(request.POST.get('plugins', '[]'))
    if not plugins:
        return JsonResponse({}, status=400, reason="No plugin(s) specified")
    update_result = update_plugins(plugins)
    result = {'plugins': update_result}
    if any(status == 'updated' for status in update_result.values()):
        # What mode are we running in?
        if os.environ.get("DOCKER_RUN") == 'true':
            result['message'] = "Docker container must be restarted."
        elif os.environ.get("RUN_MAIN") == 'true':
            result['message'] = "YANG Suite server will automatically restart."
        else:
            result['message'] = ("You will need to restart the YANG Suite "
                                 "server for these changes to take effect.")
    else:
        result['message'] = 'Check YANG Suite logs for details.'

    return JsonResponse({'result': result})


@user_passes_test(check_eula, login_url='eula')
@login_required
def report_modules(request):
    """Report on all installed Python modules and the Python version."""
    return JsonResponse({'report': python_report()})


@user_passes_test(check_eula, login_url='eula')
@login_required
def mode(request):
    """Check if mode.py file exists, which means this is a demo package."""
    mode = False
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'mode.py')):
        mode = ('<p><strong>Demo Version Copyright (c) 2017-2019'
                ' by Cisco Systems, Inc.</strong></p>')

    return JsonResponse({'mode': mode})


def eula(request):
    """Process EULA decision."""
    if request.method == 'POST':
        cisco_eula = request.POST.get('cisco-eula')
        cisco_privacy = request.POST.get('cisco-privacy')
        if cisco_eula == 'accepted' and cisco_privacy == 'accepted':
            cfg = read_prefs()
            prefs = cfg[configparser.DEFAULTSECT]
            prefs['eula_agreement'] = 'accepted'
            write_prefs(cfg)
            return HttpResponseRedirect(reverse('help'))
        else:
            return render(
                request, 'yangsuite/eula.html', {'user': request.user}
            )
    else:
        return render(request, 'yangsuite/eula.html', {'user': request.user})


@user_passes_test(check_eula, login_url='eula')
@login_required
def help_view(request, section=None, document=None):
    """Display a given help page, or the index if none is requested."""
    doc_content = {}
    if section is None:
        section = "yangsuite"
    if document is None:
        document = "index"
    path = finders.find(str(section) + "/docs/" + str(document) + ".fjson")
    if path:
        with open(path, 'r') as fd:
            doc_content = json.load(fd)
        # Fixup relative paths to embedded images
        doc_content['body'] = re.sub(
            r'src="(?:\.\./)?_images/',
            'src="/static/' + section + '/docs/_images/',
            doc_content['body'])
    else:
        doc_content['body'] = "Help file not found"

    toctree = {}
    # toctree is structured as:
    #
    # {
    #   'ysnetconf': {
    #     'title': 'Using NETCONF with YANG Suite',
    #     'items': [
    #       {
    #         'title': 'Using NETCONF RPCs',
    #         'content': 'rpcs',
    #       },
    #       ...
    #     ],
    #   },
    #   'ysyangtree': {...},
    # }
    finders.find("nonexistent/path")
    for staticdir in finders.searched_locations:
        for root, dirs, files in os.walk(staticdir):
            if '_modules' in dirs:
                dirs.remove('_modules')
            if not os.path.basename(root) == 'docs':
                continue

            section = os.path.basename(os.path.dirname(root))

            # If the plugin has specified a preferred order for its help pages,
            # get that order now.
            page_order = []
            try:
                ac = apps.get_app_config(section)
                # ac.help_pages is (suggested_title, pagename.html)
                # we just want the pagename
                page_order = [os.path.splitext(entry[1])[0]
                              for entry in ac.help_pages]
            except (LookupError, AttributeError):
                pass

            for filename in files:
                if not filename.endswith('.fjson'):
                    continue
                if filename in ['genindex.fjson',
                                'py-modindex.fjson',
                                'search.fjson']:
                    continue

                path = os.path.join(root, filename)
                page = os.path.splitext(filename)[0]
                with open(path, 'r') as fd:
                    doc = json.load(fd)

                if section not in toctree:
                    toctree[section] = {'items': []}

                if page == 'index':
                    toctree[section]['title'] = doc['title']
                else:
                    toctree[section]['items'].append({
                        'title': doc['title'],
                        'content': page,
                    })

            if section in toctree and 'items' in toctree[section]:
                # Sort the pages into the order suggested by the app. Any pages
                # not specifically suggested go at the end of the list,
                # in alphabetical order by filename.
                def ordering(entry):
                    if entry['content'] in page_order:
                        return (0, page_order.index(entry['content']))
                    return (1, entry['content'])
                toctree[section]['items'] = sorted(toctree[section]['items'],
                                                   key=ordering)
                log.debug("Sorted pages based on page_order %s: %s",
                          page_order, toctree[section]['items'])

    # Sort the sections so that built in apps are first, followed by all
    # other apps in alphabetical order.
    section_order = ['yangsuite', 'ysdevices', 'ysfilemanager', 'ysyangtree']

    def ordering(entry):
        if entry[0] in section_order:
            return (0, section_order.index(entry[0]))
        return (1, entry[0])

    newtoctree = OrderedDict()
    for key, value in sorted(toctree.items(), key=ordering):
        newtoctree[key] = value
    toctree = newtoctree

    return render(request, "yangsuite/help.html", {
        'toctree': toctree,
        'document': doc_content,
    })


@user_passes_test(check_eula, login_url='eula')
@login_required
def help_search(request):
    """Display the "search help" page and populate it with the search index."""
    finders.find("nonexistent/path")
    searchindex = {
        'docnames': [],
        'filenames': [],
        'titles': [],
        'terms': {},
        'titleterms': {},
    }

    # Each plugin provides its own "docs/searchindex.json" file, which is an
    # index of the documentation pages provided by this plugin.
    # We walk across all plugins to build a single global search index.
    for staticdir in finders.searched_locations:
        for root, dirs, files in os.walk(staticdir):
            if '_modules' in dirs:
                dirs.remove('_modules')
            if not os.path.basename(root) == 'docs':
                continue
            if 'searchindex.json' not in files:
                continue

            section = os.path.basename(os.path.dirname(root))
            path = os.path.join(root, 'searchindex.json')

            with open(path, 'r') as fd:
                newindex = json.load(fd)

            # Each searchindex dictionary references its documents by a
            # integer index. We need to modify this index to avoid collisions,
            # i.e. if plugin A has docs [0..4] and plugin B has docs [0..3],
            # we need to remap plugin B to use [5..8] instead.
            offset = len(searchindex['docnames'])

            for key, value in newindex.items():
                if key in ['titles']:
                    # List of document titles - just append to existing list
                    searchindex[key] += value
                elif key in ['docnames', 'filenames']:
                    # Prepend section to each name, then add to existing list
                    searchindex[key] += [section + '/' + n for n in value]
                elif key in ['terms', 'titleterms']:
                    # Dictionary of term: matching document index(es)
                    # To add complexity, the matches can either be a single
                    # page index (int) or a list of such indices, so we have to
                    # handle both cases when combining pages
                    for term, matches in value.items():
                        # Apply previously calculated offset to all indices.
                        if isinstance(matches, int):
                            matches += offset
                        else:
                            matches = [m + offset for m in matches]

                        if term not in searchindex[key]:
                            searchindex[key][term] = matches
                        else:
                            # Combine entries into a single list
                            base_matches = searchindex[key][term]
                            if isinstance(base_matches, int):
                                base_matches = [base_matches]
                            if isinstance(matches, int):
                                matches = [matches]
                            searchindex[key][term] = base_matches + matches

    return render(request, "yangsuite/help_search.html", {
        'searchindex': json.dumps(searchindex),
    })
