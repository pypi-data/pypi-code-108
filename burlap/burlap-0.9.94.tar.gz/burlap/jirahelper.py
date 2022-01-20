import sys
import re
import traceback
from datetime import date
from pprint import pprint

from burlap import ContainerSatchel
from burlap.constants import *
from burlap.decorators import task


class JiraHelperSatchel(ContainerSatchel):

    name = 'jirahelper'
    _jira = None

    def set_defaults(self):

        self.env.server = None
        self.env.basic_auth_username = None
        self.env.basic_auth_password = None
        self.env.update_from_git = False
        self.env.ticket_update_message_template = 'This has been deployed to {role}.'

        # A map of status->transition to follow when making deployments.
        self.env.deploy_workflow = {}

        # A map of the new-status->new-assignee to auto-assign.
        self.env.assignee_by_status = {}

        # The regex used to search the commit messages for a ticket number.
        self.env.ticket_pattern = None

        # If True, update release (fixVersion field) for all deployed issues in update_tickets_from_git().
        self.env.update_ticket_release = False
        self.env.release_format = '%Y.%m.%d'

    @property
    def project(self):
        """
        'PROJECT-1234' -> 'PROJECT'
        """
        return self.env.ticket_pattern.split('-', maxsplit=1)[0]

    @property
    def jira(self):
        """
        Attach a JIRA instance to JiraHelperSatchel class to prevent unnecessary re-initialization.
        """
        from jira import JIRA

        if self._jira is None:
            self.vprint('Connecting to %s with user %s...' % (self.env.server, self.env.basic_auth_username))
            self._jira = JIRA({
                'server': self.env.server
            }, basic_auth=(self.env.basic_auth_username, self.env.basic_auth_password))
        return self._jira

    def get_tickets_from_str(self, s):
        """
        From a string, get all Jira issue keys matching a pattern.

        Args:
            s (str): String containing zero or more Jira issue keys

        Returns:
            tickets (set): Jira issue key strings
        """
        if self.env.ticket_pattern:
            pattern = re.compile(self.env.ticket_pattern, flags=re.IGNORECASE)
            tickets = pattern.findall(s)
        else:
            tickets = []
        return {ticket.strip().upper() for ticket in tickets}

    @task
    def get_tickets_between_commits(self, old_commit, new_commit):
        """
        Retrieve all Jira issue linked to commits between the given commit numbers on the current branch.

        Args:
            old_commit (str): Hash of ancestor git commit
            new_commit (str): Hash of descendant git commit

        Returns:
            tickets (set): Jira issue key strings corresponding to the new commits
        """
        from burlap.git import gittracker

        if self.env.ticket_pattern:
            commit_logs = gittracker.get_logs_between_commits(old_commit, new_commit)
            tickets = self.get_tickets_from_str(commit_logs)
        else:
            tickets = set()
        self.vprint(tickets)
        return tickets

    @task
    def test_connection(self):
        from burlap.common import print_success, print_fail

        try:
            result = self.jira.search_issues('status=resolved')
            self.vprint('result:', result)
            print_success('OK')
        except Exception as exc:
            print_fail('ERROR: %s' % exc)

    def get_release(self):
        """
        Get or create current Jira release for project, using env.release_format.

        Returns:
            release (str): Name of release.
        """
        release = date.today().strftime(self.env.release_format)
        self.vprint('Looking for release %s...' % release)
        if not self.jira.get_project_version_by_name(self.project, release):
            self.vprint('Creating release %s...' % release)
            self.jira.create_version(release, project=self.project, releaseDate=date.today().strftime('%Y-%m-%d'))

        return release

    @task
    def update_ticket_from_git(self, ticket, release=None):
        """
        Update ticket status and release in Jira.

        Args:
            ticket (str): Jira issue key
            release (str or None): Name of release to associate with issue
        """
        from jira import JIRA, JIRAError

        r = self.local_renderer

        # Mention this Jira update.
        r.env.role = r.genv.ROLE.lower()
        comment = r.format(self.env.ticket_update_message_template)
        print('Commenting on ticket %s: %s' % (ticket, comment))
        if not self.dryrun:
            self.jira.add_comment(ticket, comment)

        print('Looking up Jira ticket %s...' % ticket)
        issue = self.jira.issue(ticket)
        self.vprint('Ticket %s retrieved.' % ticket)

        # Update ticket release.
        if self.env.update_ticket_release:
            try:
                if not release:
                    release = self.get_release()
                self.vprint('Updating issue %s to release %s.' % (issue, release))
                issue.update(fields={'fixVersions': [{'name': release}]})
            except JIRAError as exc:
                print(exc)

        # Update ticket status.
        recheck = False
        for i in range(10):
            transition_to_id = {t['name']: t['id'] for t in self.jira.transitions(issue)}
            self.vprint('%i allowable transitions found:' % len(transition_to_id))
            if self.verbose:
                pprint(transition_to_id)
            self.vprint('issue.fields.status.id:', issue.fields.status.id)
            self.vprint('issue.fields.status.name:', issue.fields.status.name)
            jira_status_name = issue.fields.status.name
            self.vprint('jira_status_name:', jira_status_name)
            next_transition_name = self.env.deploy_workflow.get(jira_status_name)
            self.vprint('next_transition_name:', next_transition_name)
            next_transition_id = transition_to_id.get(next_transition_name)
            self.vprint('next_transition_id:', next_transition_id)
            if next_transition_name:
                # Note: assignment should happen after transition, since the assignment may
                # remove transitions that we need.
                print('Updating ticket %s to status %s (%s).' % (ticket, next_transition_name, next_transition_id))
                if next_transition_id and not self.dryrun:
                    try:
                        self.jira.transition_issue(issue, next_transition_id)
                        recheck = True
                    except AttributeError as e:
                        print('Unable to transition ticket %s to %s: %s' % (ticket, next_transition_name, e),
                              file=sys.stderr)
                        traceback.print_exc()

                # Get new assignee by status.
                new_assignee = self.env.assignee_by_status.get(next_transition_name)
                if new_assignee == 'reporter':
                    new_assignee = issue.fields.reporter

                if new_assignee:
                    print('Assigning ticket %s to %s.' % (ticket, new_assignee.displayName))
                    if not self.dryrun:
                        try:
                            self.jira.assign_issue(issue, new_assignee)
                        except JIRAError as e:
                            print('Unable to reassign ticket %s to %s: %s' % (ticket, new_assignee.displayName, e),
                                  file=sys.stderr)
                else:
                    print('No new assignee found.')
            else:
                recheck = False
                print(
                    'No transitions found for ticket %s currently in status "%s".' % (ticket, issue.fields.status.name)
                )

            if not recheck:
                break

    @task
    def update_tickets_from_git(self, from_commit=None, to_commit=None):
        """
        Find all ticket numbers and update their status in Jira.

        Run during a deployment.
        Looks at all commits between now and the last deployment.
        """
        from burlap.git import gittracker, CURRENT_COMMIT

#         get_current_commit = gittracker.get_current_commit
#         GITTRACKER = gittracker.name.upper()

        # Ensure this is only run once per role.
        if self.genv.host_string != self.genv.hosts[-1]:
            self.vprint('Not first server. Aborting.')
            return

        self.vprint('self.env.update_from_git:', self.env.update_from_git)
        self.vprint('self.genv.jirahelper_update_from_git:', self.genv.jirahelper_update_from_git)
        if not self.env.update_from_git:
            self.vprint('Update from git disabled. Aborting.')
            return

        if not self.env.ticket_pattern:
            self.vprint('No ticket pattern defined. Aborting.')
            return

        if not self.env.basic_auth_username or not self.env.basic_auth_password:
            self.vprint('Username or password not given. Aborting.')
            return

        # During a deployment, we should be given these, but for testing, look up the diffs dynamically.
        last = gittracker.last_manifest
        current = gittracker.current_manifest

        last_commit = from_commit or last.current_commit#[CURRENT_COMMIT]
        print('last_commit:', last_commit)
        current_commit = to_commit or current[CURRENT_COMMIT]
        print('current_commit:', current_commit)

        if not last_commit or not current_commit:
            print('Missing commit ID. Aborting.')
            return

        self.vprint('-'*80)
        self.vprint('last.keys:', last.keys())
        self.vprint('-'*80)
        self.vprint('current.keys:', current.keys())

#         try:
#             last_commit = last['GITTRACKER']['current_commit']
#         except KeyError:
#             return
#         current_commit = current['GITTRACKER']['current_commit']

        # Find all tickets deployed between last deployment and now.
        tickets = self.get_tickets_between_commits(last_commit, current_commit)
        self.vprint('tickets:', tickets)

        if not tickets:
            return

        # Get or create Jira release for tickets.
        if self.env.update_ticket_release:
            release = self.get_release()
        else:
            release = None

        # Update all tickets in Jira.
        for ticket in tickets:
            try:
                self.update_ticket_from_git(ticket, release=release)
            except Exception:
                traceback.print_exc()

        # Mark Jira release as released.
        if self.env.update_ticket_release:
            self.vprint('Releasing version %s...:', release)
            release_obj = self.jira.get_project_version_by_name(self.project, release)
            release_obj.update(released=True)

jirahelper = JiraHelperSatchel()
