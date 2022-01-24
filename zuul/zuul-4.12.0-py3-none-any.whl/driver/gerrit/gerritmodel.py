# Copyright 2017 Red Hat, Inc.
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

import copy
import re
import time
import urllib.parse
import dateutil.parser

from zuul.model import EventFilter, RefFilter
from zuul.model import Change, TriggerEvent
from zuul.driver.util import time_to_seconds
from zuul import exceptions


EMPTY_GIT_REF = '0' * 40  # git sha of all zeros, used during creates/deletes


class GerritChange(Change):
    def __init__(self, project):
        super(GerritChange, self).__init__(project)
        self.id = None
        self.status = None
        self.wip = None
        self.approvals = []
        self.missing_labels = set()
        self.commit = None

    def update(self, data, connection):
        if data.format == data.SSH:
            self.updateFromSSH(data.data, connection)
        else:
            self.updateFromHTTP(data.data, data.files, connection)

    def serialize(self):
        d = super().serialize()
        d.update({
            "id": self.id,
            "status": self.status,
            "wip": self.wip,
            "approvals": self.approvals,
            "missing_labels": list(self.missing_labels),
            "commit": self.commit,
        })
        return d

    def deserialize(self, data):
        super().deserialize(data)
        self.id = data.get("id")
        self.status = data["status"]
        self.wip = data["wip"]
        self.approvals = data["approvals"]
        self.missing_labels = set(data["missing_labels"])
        self.commit = data.get("commit")

    def updateFromSSH(self, data, connection):
        if self.patchset is None:
            self.patchset = str(data['currentPatchSet']['number'])
        if 'project' not in data:
            raise exceptions.ChangeNotFound(self.number, self.patchset)
        self.project = connection.source.getProject(data['project'])
        self.commit_id = str(data['currentPatchSet']['revision'])
        self.branch = data['branch']
        self.url = data['url']
        urlparse = urllib.parse.urlparse(connection.baseurl)
        baseurl = "%s://%s%s" % (urlparse.scheme, urlparse.netloc,
                                 urlparse.path)
        baseurl = baseurl.rstrip('/')
        self.uris = [
            '%s/%s' % (baseurl, self.number),
            '%s/#/c/%s' % (baseurl, self.number),
            '%s/c/%s/+/%s' % (baseurl, self.project.name, self.number),
        ]

        max_ps = 0
        files = []
        for ps in data['patchSets']:
            if str(ps['number']) == self.patchset:
                self.ref = ps['ref']
                self.commit = ps['revision']
                # SSH queries gives us a list of dicts for the files. We
                # convert that to a list of filenames.
                for f in ps.get('files', []):
                    files.append(f['file'])
            if int(ps['number']) > int(max_ps):
                max_ps = str(ps['number'])
        if max_ps == self.patchset:
            self.is_current_patchset = True
        else:
            self.is_current_patchset = False
        if len(data.get('parents', [])) > 1:
            # This is a merge commit, and the SSH query only reports
            # files in this commit's content (not files changed by the
            # underlying merged changes).  Set files to None to
            # instruct Zuul to ask the mergers to get the full file
            # list.
            self.files = None
        self.files = files
        self.id = data['id']
        self.is_merged = data.get('status', '') == 'MERGED'
        self.approvals = data['currentPatchSet'].get('approvals', [])
        self.open = data['open']
        self.status = data['status']
        self.wip = data.get('wip', False)
        self.owner = data['owner'].get('username')
        self.message = data['commitMessage']

        self.missing_labels = set()
        for sr in data.get('submitRecords', []):
            if sr['status'] == 'NOT_READY':
                for label in sr['labels']:
                    if label['status'] in ['OK', 'MAY']:
                        continue
                    elif label['status'] in ['NEED', 'REJECT']:
                        self.missing_labels.add(label['label'])

    def updateFromHTTP(self, data, files, connection):
        urlparse = urllib.parse.urlparse(connection.baseurl)
        baseurl = "%s://%s%s" % (urlparse.scheme, urlparse.netloc,
                                 urlparse.path)
        baseurl = baseurl.rstrip('/')
        current_revision = data['revisions'][data['current_revision']]
        if self.patchset is None:
            self.patchset = str(current_revision['_number'])
        self.project = connection.source.getProject(data['project'])
        self.commit_id = str(data['current_revision'])
        self.id = data['change_id']
        self.branch = data['branch']
        self.url = '%s/%s' % (baseurl, self.number)
        self.uris = [
            '%s/%s' % (baseurl, self.number),
            '%s/#/c/%s' % (baseurl, self.number),
            '%s/c/%s/+/%s' % (baseurl, self.project.name, self.number),
        ]

        if str(current_revision['_number']) == self.patchset:
            self.ref = current_revision['ref']
            self.commit = data['current_revision']
            self.is_current_patchset = True
        else:
            self.is_current_patchset = False

        # HTTP queries give us a dict of files in the form of
        # {filename: { attrs }}. We only want a list of filenames here.
        if files:
            self.files = list(files.keys())
        else:
            self.files = []

        self.is_merged = data['status'] == 'MERGED'
        self.approvals = []
        self.missing_labels = set()
        for label_name, label_data in data.get('labels', {}).items():
            for app in label_data.get('all', []):
                if app.get('value', 0) == 0:
                    continue
                by = {}
                for k in ('name', 'username', 'email'):
                    if k in app:
                        by[k] = app[k]
                self.approvals.append({
                    "type": label_name,
                    "description": label_name,
                    "value": app['value'],
                    "grantedOn":
                    dateutil.parser.parse(app['date']).timestamp(),
                    "by": by,
                })
            if label_data.get('optional', False):
                continue
            if label_data.get('blocking', False):
                self.missing_labels.add(label_name)
                continue
            if 'approved' in label_data:
                continue
            self.missing_labels.add(label_name)
        self.open = data['status'] == 'NEW'
        self.status = data['status']
        self.wip = data.get('work_in_progress', False)
        self.owner = data['owner'].get('username')
        self.message = current_revision['commit']['message']


class GerritTriggerEvent(TriggerEvent):
    """Incoming event from an external system."""
    def __init__(self):
        super(GerritTriggerEvent, self).__init__()
        self.approvals = []
        self.uuid = None
        self.scheme = None
        self.patchsetcomments = None

    def toDict(self):
        d = super().toDict()
        d["approvals"] = self.approvals
        d["uuid"] = self.uuid
        d["scheme"] = self.scheme
        d["patchsetcomments"] = self.patchsetcomments
        return d

    def updateFromDict(self, d):
        super().updateFromDict(d)
        self.approvals = d["approvals"]
        self.uuid = d["uuid"]
        self.scheme = d["scheme"]
        self.patchsetcomments = d["patchsetcomments"]

    def __repr__(self):
        ret = '<GerritTriggerEvent %s %s' % (self.type,
                                             self.canonical_project_name)

        if self.branch:
            ret += " %s" % self.branch
        if self.change_number:
            ret += " %s,%s" % (self.change_number, self.patch_number)
        if self.approvals:
            ret += ' ' + ', '.join(
                ['%s:%s' % (a['type'], a['value']) for a in self.approvals])
        ret += '>'

        return ret

    def isPatchsetCreated(self):
        return self.type in ('patchset-created', 'pending-check')

    def isChangeAbandoned(self):
        return 'change-abandoned' == self.type


class GerritApprovalFilter(object):
    def __init__(self, required_approvals=[], reject_approvals=[]):
        self._required_approvals = copy.deepcopy(required_approvals)
        self.required_approvals = self._tidy_approvals(
            self._required_approvals)
        self._reject_approvals = copy.deepcopy(reject_approvals)
        self.reject_approvals = self._tidy_approvals(self._reject_approvals)

    def _tidy_approvals(self, approvals):
        for a in approvals:
            for k, v in a.items():
                if k == 'username':
                    a['username'] = re.compile(v)
                elif k == 'email':
                    a['email'] = re.compile(v)
                elif k == 'newer-than':
                    a[k] = time_to_seconds(v)
                elif k == 'older-than':
                    a[k] = time_to_seconds(v)
        return approvals

    def _match_approval_required_approval(self, rapproval, approval):
        # Check if the required approval and approval match
        if 'description' not in approval:
            return False
        now = time.time()
        by = approval.get('by', {})
        for k, v in rapproval.items():
            if k == 'username':
                if (not v.search(by.get('username', ''))):
                    return False
            elif k == 'email':
                if (not v.search(by.get('email', ''))):
                    return False
            elif k == 'newer-than':
                t = now - v
                if (approval['grantedOn'] < t):
                    return False
            elif k == 'older-than':
                t = now - v
                if (approval['grantedOn'] >= t):
                    return False
            else:
                if not isinstance(v, list):
                    v = [v]
                if (approval['description'] != k or
                        int(approval['value']) not in v):
                    return False
        return True

    def matchesApprovals(self, change):
        if self.required_approvals or self.reject_approvals:
            if not hasattr(change, 'number'):
                # Not a change, no reviews
                return False
        if self.required_approvals and not change.approvals:
            # A change with no approvals can not match
            return False

        # TODO(jhesketh): If we wanted to optimise this slightly we could
        # analyse both the REQUIRE and REJECT filters by looping over the
        # approvals on the change and keeping track of what we have checked
        # rather than needing to loop on the change approvals twice
        return (self.matchesRequiredApprovals(change) and
                self.matchesNoRejectApprovals(change))

    def matchesRequiredApprovals(self, change):
        # Check if any approvals match the requirements
        for rapproval in self.required_approvals:
            matches_rapproval = False
            for approval in change.approvals:
                if self._match_approval_required_approval(rapproval, approval):
                    # We have a matching approval so this requirement is
                    # fulfilled
                    matches_rapproval = True
                    break
            if not matches_rapproval:
                return False
        return True

    def matchesNoRejectApprovals(self, change):
        # Check to make sure no approvals match a reject criteria
        for rapproval in self.reject_approvals:
            for approval in change.approvals:
                if self._match_approval_required_approval(rapproval, approval):
                    # A reject approval has been matched, so we reject
                    # immediately
                    return False
        # To get here no rejects can have been matched so we should be good to
        # queue
        return True


class GerritEventFilter(EventFilter, GerritApprovalFilter):
    def __init__(self, connection_name, trigger, types=[], branches=[],
                 refs=[], event_approvals={}, comments=[], emails=[],
                 usernames=[], required_approvals=[], reject_approvals=[],
                 uuid=None, scheme=None, ignore_deletes=True):

        EventFilter.__init__(self, connection_name, trigger)

        GerritApprovalFilter.__init__(self,
                                      required_approvals=required_approvals,
                                      reject_approvals=reject_approvals)

        self._types = types
        self._branches = branches
        self._refs = refs
        self._comments = comments
        self._emails = emails
        self._usernames = usernames
        self.types = [re.compile(x) for x in types]
        self.branches = [re.compile(x) for x in branches]
        self.refs = [re.compile(x) for x in refs]
        self.comments = [re.compile(x) for x in comments]
        self.emails = [re.compile(x) for x in emails]
        self.usernames = [re.compile(x) for x in usernames]
        self.event_approvals = event_approvals
        self.uuid = uuid
        self.scheme = scheme
        self.ignore_deletes = ignore_deletes

    def __repr__(self):
        ret = '<GerritEventFilter'
        ret += ' connection: %s' % self.connection_name

        if self._types:
            ret += ' types: %s' % ', '.join(self._types)
        if self.uuid:
            ret += ' uuid: %s' % (self.uuid,)
        if self.scheme:
            ret += ' scheme: %s' % (self.scheme,)
        if self._branches:
            ret += ' branches: %s' % ', '.join(self._branches)
        if self._refs:
            ret += ' refs: %s' % ', '.join(self._refs)
        if self.ignore_deletes:
            ret += ' ignore_deletes: %s' % self.ignore_deletes
        if self.event_approvals:
            ret += ' event_approvals: %s' % ', '.join(
                ['%s:%s' % a for a in self.event_approvals.items()])
        if self.required_approvals:
            ret += ' required_approvals: %s' % ', '.join(
                ['%s' % a for a in self._required_approvals])
        if self.reject_approvals:
            ret += ' reject_approvals: %s' % ', '.join(
                ['%s' % a for a in self._reject_approvals])
        if self._comments:
            ret += ' comments: %s' % ', '.join(self._comments)
        if self._emails:
            ret += ' emails: %s' % ', '.join(self._emails)
        if self._usernames:
            ret += ' usernames: %s' % ', '.join(self._usernames)
        ret += '>'

        return ret

    def matches(self, event, change):
        if not super().matches(event, change):
            return False

        # event types are ORed
        matches_type = False
        for etype in self.types:
            if etype.match(event.type):
                matches_type = True
        if self.types and not matches_type:
            return False

        if event.type == 'pending-check':
            if self.uuid and event.uuid != self.uuid:
                return False
            if self.scheme and event.uuid.split(':')[0] != self.scheme:
                return False

        # branches are ORed
        matches_branch = False
        for branch in self.branches:
            if branch.match(event.branch):
                matches_branch = True
        if self.branches and not matches_branch:
            return False

        # refs are ORed
        matches_ref = False
        if event.ref is not None:
            for ref in self.refs:
                if ref.match(event.ref):
                    matches_ref = True
        if self.refs and not matches_ref:
            return False
        if self.ignore_deletes and event.newrev == EMPTY_GIT_REF:
            # If the updated ref has an empty git sha (all 0s),
            # then the ref is being deleted
            return False

        # comments are ORed
        matches_comment_re = False
        for comment_re in self.comments:
            if (event.comment is not None and
                comment_re.search(event.comment)):
                matches_comment_re = True
            if event.patchsetcomments is not None:
                for comment in event.patchsetcomments:
                    if (comment is not None and
                        comment_re.search(comment)):
                        matches_comment_re = True
        if self.comments and not matches_comment_re:
            return False

        # We better have an account provided by Gerrit to do
        # email filtering.
        if event.account is not None:
            account_email = event.account.get('email')
            # emails are ORed
            matches_email_re = False
            for email_re in self.emails:
                if (account_email is not None and
                        email_re.search(account_email)):
                    matches_email_re = True
            if self.emails and not matches_email_re:
                return False

            # usernames are ORed
            account_username = event.account.get('username')
            matches_username_re = False
            for username_re in self.usernames:
                if (account_username is not None and
                    username_re.search(account_username)):
                    matches_username_re = True
            if self.usernames and not matches_username_re:
                return False

        # approvals are ANDed
        for category, value in self.event_approvals.items():
            matches_approval = False
            for eapp in event.approvals:
                if (eapp['description'] == category and
                        int(eapp['value']) == int(value)):
                    matches_approval = True
            if not matches_approval:
                return False

        # required approvals are ANDed (reject approvals are ORed)
        if not self.matchesApprovals(change):
            return False

        return True


class GerritRefFilter(RefFilter, GerritApprovalFilter):
    def __init__(self, connection_name, open=None, current_patchset=None,
                 statuses=[], required_approvals=[],
                 reject_approvals=[]):
        RefFilter.__init__(self, connection_name)

        GerritApprovalFilter.__init__(self,
                                      required_approvals=required_approvals,
                                      reject_approvals=reject_approvals)

        self.open = open
        self.current_patchset = current_patchset
        self.statuses = statuses

    def __repr__(self):
        ret = '<GerritRefFilter'

        ret += ' connection_name: %s' % self.connection_name
        if self.open is not None:
            ret += ' open: %s' % self.open
        if self.current_patchset is not None:
            ret += ' current-patchset: %s' % self.current_patchset
        if self.statuses:
            ret += ' statuses: %s' % ', '.join(self.statuses)
        if self.required_approvals:
            ret += (' required-approvals: %s' %
                    str(self.required_approvals))
        if self.reject_approvals:
            ret += (' reject-approvals: %s' %
                    str(self.reject_approvals))
        ret += '>'

        return ret

    def matches(self, change):
        if self.open is not None:
            # if a "change" has no number, it's not a change, but a push
            # and cannot possibly pass this test.
            if hasattr(change, 'number'):
                if self.open != change.open:
                    return False
            else:
                return False

        if self.current_patchset is not None:
            # if a "change" has no number, it's not a change, but a push
            # and cannot possibly pass this test.
            if hasattr(change, 'number'):
                if self.current_patchset != change.is_current_patchset:
                    return False
            else:
                return False

        if self.statuses:
            if change.status not in self.statuses:
                return False

        # required approvals are ANDed (reject approvals are ORed)
        if not self.matchesApprovals(change):
            return False

        return True
