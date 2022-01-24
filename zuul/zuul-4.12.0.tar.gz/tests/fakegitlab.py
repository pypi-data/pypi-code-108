# Copyright 2016 Red Hat, Inc.
# Copyright 2021 Acme Gating, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections import defaultdict
import http.server
import json
import logging
import re
import socketserver
import threading
import urllib.parse

from git.util import IterableList


class GitlabWebServer(object):

    def __init__(self, merge_requests):
        super(GitlabWebServer, self).__init__()
        self.merge_requests = merge_requests
        self.fake_repos = defaultdict(lambda: IterableList('name'))
        # A dictionary so we can mutate it
        self.options = dict(community_edition=False)

    def start(self):
        merge_requests = self.merge_requests
        fake_repos = self.fake_repos
        options = self.options

        class Server(http.server.SimpleHTTPRequestHandler):
            log = logging.getLogger("zuul.test.GitlabWebServer")

            branches_re = re.compile(r'.+/projects/(?P<project>.+)/'
                                     r'repository/branches\\?.*$')
            branch_re = re.compile(r'.+/projects/(?P<project>.+)/'
                                   r'repository/branches/(?P<branch>.+)$')
            mr_re = re.compile(r'.+/projects/(?P<project>.+)/'
                               r'merge_requests/(?P<mr>\d+)$')
            mr_approvals_re = re.compile(
                r'.+/projects/(?P<project>.+)/'
                r'merge_requests/(?P<mr>\d+)/approvals$')

            mr_notes_re = re.compile(
                r'.+/projects/(?P<project>.+)/'
                r'merge_requests/(?P<mr>\d+)/notes$')
            mr_approve_re = re.compile(
                r'.+/projects/(?P<project>.+)/'
                r'merge_requests/(?P<mr>\d+)/approve$')
            mr_unapprove_re = re.compile(
                r'.+/projects/(?P<project>.+)/'
                r'merge_requests/(?P<mr>\d+)/unapprove$')

            mr_merge_re = re.compile(r'.+/projects/(?P<project>.+)/'
                                     r'merge_requests/(?P<mr>\d+)/merge$')

            def _get_mr(self, project, number):
                project = urllib.parse.unquote(project)
                mr = merge_requests.get(project, {}).get(number)
                if not mr:
                    # Find out what gitlab does in this case
                    raise NotImplementedError()
                return mr

            def do_GET(self):
                path = self.path
                self.log.debug("Got GET %s", path)

                m = self.mr_re.match(path)
                if m:
                    return self.get_mr(**m.groupdict())
                m = self.mr_approvals_re.match(path)
                if m:
                    return self.get_mr_approvals(**m.groupdict())
                m = self.branch_re.match(path)
                if m:
                    return self.get_branch(**m.groupdict())
                m = self.branches_re.match(path)
                if m:
                    return self.get_branches(path, **m.groupdict())
                self.send_response(500)
                self.end_headers()

            def do_POST(self):
                path = self.path
                self.log.debug("Got POST %s", path)

                data = self.rfile.read(int(self.headers['Content-Length']))
                if (self.headers['Content-Type'] ==
                    'application/x-www-form-urlencoded'):
                    data = urllib.parse.parse_qs(data.decode('utf-8'))

                self.log.debug("Got data %s", data)

                m = self.mr_notes_re.match(path)
                if m:
                    return self.post_mr_notes(data, **m.groupdict())
                m = self.mr_approve_re.match(path)
                if m:
                    return self.post_mr_approve(data, **m.groupdict())
                m = self.mr_unapprove_re.match(path)
                if m:
                    return self.post_mr_unapprove(data, **m.groupdict())
                self.send_response(500)
                self.end_headers()

            def do_PUT(self):
                path = self.path
                self.log.debug("Got PUT %s", path)

                data = self.rfile.read(int(self.headers['Content-Length']))
                if (self.headers['Content-Type'] ==
                    'application/x-www-form-urlencoded'):
                    data = urllib.parse.parse_qs(data.decode('utf-8'))

                self.log.debug("Got data %s", data)

                m = self.mr_merge_re.match(path)
                if m:
                    return self.put_mr_merge(data, **m.groupdict())
                self.send_response(500)
                self.end_headers()

            def send_data(self, data, code=200):
                data = json.dumps(data).encode('utf-8')
                self.send_response(code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(data))
                self.end_headers()
                self.wfile.write(data)

            def get_mr(self, project, mr):
                mr = self._get_mr(project, mr)
                data = {
                    'target_branch': mr.branch,
                    'title': mr.subject,
                    'state': mr.state,
                    'description': mr.description,
                    'author': {
                        'name': 'Administrator',
                        'username': 'admin'
                    },
                    'updated_at':
                    mr.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    'sha': mr.sha,
                    'labels': mr.labels,
                    'merged_at': mr.merged_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    if mr.merged_at else mr.merged_at,
                    'diff_refs': {
                        'base_sha': 'c380d3acebd181f13629a25d2e2acca46ffe1e00',
                        'head_sha': '2be7ddb704c7b6b83732fdd5b9f09d5a397b5f8f',
                        'start_sha': 'c380d3acebd181f13629a25d2e2acca46ffe1e00'
                    },
                    'merge_status': mr.merge_status,
                }
                self.send_data(data)

            def get_mr_approvals(self, project, mr):
                mr = self._get_mr(project, mr)
                if not options['community_edition']:
                    self.send_data({
                        'approvals_left': 0 if mr.approved else 1,
                    })
                else:
                    self.send_data({
                        'approved': mr.approved,
                    })

            def get_branch(self, project, branch):
                project = urllib.parse.unquote(project)
                branch = urllib.parse.unquote(branch)
                owner, name = project.split('/')
                if branch in fake_repos[(owner, name)]:
                    protected = fake_repos[(owner, name)][branch].protected
                    self.send_data({'protected': protected})
                else:
                    return self.send_data({}, code=404)

            def get_branches(self, url, project):
                project = urllib.parse.unquote(project).split('/')
                req = urllib.parse.urlparse(url)
                query = urllib.parse.parse_qs(req.query)
                per_page = int(query["per_page"][0])
                page = int(query["page"][0])

                repo = fake_repos[tuple(project)]
                first_entry = (page - 1) * per_page
                last_entry = min(len(repo), (page) * per_page)

                if first_entry >= len(repo):
                    branches = []
                else:
                    branches = [{'name': repo[i].name,
                                 'protected': repo[i].protected}
                                for i in range(first_entry, last_entry)]
                self.send_data(branches)

            def post_mr_notes(self, data, project, mr):
                mr = self._get_mr(project, mr)
                mr.addNote(data['body'][0])
                self.send_data({})

            def post_mr_approve(self, data, project, mr):
                assert 'sha' in data
                mr = self._get_mr(project, mr)
                if data['sha'][0] != mr.sha:
                    return self.send_data(
                        {'message': 'SHA does not match HEAD of source '
                         'branch: <new_sha>'}, code=409)
                mr.approved = True
                self.send_data({})

            def post_mr_unapprove(self, data, project, mr):
                mr = self._get_mr(project, mr)
                mr.approved = False
                self.send_data({})

            def put_mr_merge(self, data, project, mr):
                mr = self._get_mr(project, mr)
                mr.mergeMergeRequest()
                self.send_data({'state': 'merged'})

            def log_message(self, fmt, *args):
                self.log.debug(fmt, *args)

        self.httpd = socketserver.ThreadingTCPServer(('', 0), Server)
        self.port = self.httpd.socket.getsockname()[1]
        self.thread = threading.Thread(name='GitlabWebServer',
                                       target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.thread.join()
