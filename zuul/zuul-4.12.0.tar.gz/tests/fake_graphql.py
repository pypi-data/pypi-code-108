# Copyright 2019 BMW Group
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

from graphene import Boolean, Field, Int, List, ObjectType, String


class FakePageInfo(ObjectType):
    end_cursor = String()
    has_next_page = Boolean()

    def resolve_end_cursor(parent, info):
        return 'testcursor'

    def resolve_has_next_page(parent, info):
        return False


class FakeMatchingRef(ObjectType):
    name = String()

    def resolve_name(parent, info):
        return parent


class FakeMatchingRefs(ObjectType):
    nodes = List(FakeMatchingRef)

    def resolve_nodes(parent, info):
        # To simplify tests just return the pattern and a bogus ref that should
        # not disturb zuul.
        return [parent.pattern, 'bogus-ref']


class FakeBranchProtectionRule(ObjectType):
    pattern = String()
    requiredStatusCheckContexts = List(String)
    requiresApprovingReviews = Boolean()
    requiresCodeOwnerReviews = Boolean()
    matchingRefs = Field(FakeMatchingRefs, first=Int())

    def resolve_pattern(parent, info):
        return parent.pattern

    def resolve_requiredStatusCheckContexts(parent, info):
        return parent.required_contexts

    def resolve_requiresApprovingReviews(parent, info):
        return parent.require_reviews

    def resolve_requiresCodeOwnerReviews(parent, info):
        return parent.require_codeowners_review

    def resolve_matchingRefs(parent, info, first=None):
        return parent


class FakeBranchProtectionRules(ObjectType):
    nodes = List(FakeBranchProtectionRule)

    def resolve_nodes(parent, info):
        return parent.values()


class FakeActor(ObjectType):
    login = String()


class FakeStatusContext(ObjectType):
    state = String()
    context = String()
    creator = Field(FakeActor)

    def resolve_state(parent, info):
        state = parent.state.upper()
        return state

    def resolve_context(parent, info):
        return parent.context

    def resolve_creator(parent, info):
        return parent.creator


class FakeStatus(ObjectType):
    contexts = List(FakeStatusContext)

    def resolve_contexts(parent, info):
        return parent


class FakeCheckRun(ObjectType):
    name = String()
    conclusion = String()

    def resolve_name(parent, info):
        return parent.name

    def resolve_conclusion(parent, info):
        if parent.conclusion:
            return parent.conclusion.upper()
        return None


class FakeCheckRuns(ObjectType):
    nodes = List(FakeCheckRun)

    def resolve_nodes(parent, info):
        return parent


class FakeApp(ObjectType):
    slug = String()
    name = String()


class FakeCheckSuite(ObjectType):
    app = Field(FakeApp)
    checkRuns = Field(FakeCheckRuns, first=Int())

    def resolve_app(parent, info):
        if not parent:
            return None
        return parent[0].app

    def resolve_checkRuns(parent, info, first=None):
        # We only want to return the latest result for a check run per app.
        # Since the check runs are ordered from latest to oldest result we
        # need to traverse the list in reverse order.
        check_runs_by_name = {
            "{}:{}".format(cr.app, cr.name): cr for cr in reversed(parent)
        }
        return check_runs_by_name.values()


class FakeCheckSuites(ObjectType):

    nodes = List(FakeCheckSuite)

    def resolve_nodes(parent, info):
        # Note: we only use a single check suite in the tests so return a
        # single item to keep it simple.
        return [parent]


class FakeCommit(ObjectType):

    class Meta:
        # Graphql object type that defaults to the class name, but we require
        # 'Commit'.
        name = 'Commit'

    status = Field(FakeStatus)
    checkSuites = Field(FakeCheckSuites, first=Int())

    def resolve_status(parent, info):
        seen = set()
        result = []
        for status in parent._statuses:
            if status.context not in seen:
                seen.add(status.context)
                result.append(status)
        # Github returns None if there are no results
        return result or None

    def resolve_checkSuites(parent, info, first=None):
        # Tests only utilize one check suite so return all runs for that.
        return parent._check_runs


class FakePullRequest(ObjectType):
    isDraft = Boolean()
    reviewDecision = String()

    def resolve_isDraft(parent, info):
        return parent.draft

    def resolve_reviewDecision(parent, info):
        if hasattr(info.context, 'version') and info.context.version:
            if info.context.version < (2, 21, 0):
                raise Exception('Field unsupported')

        # Check branch protection rules if reviews are required
        org, project = parent.project.split('/')
        repo = info.context._data.repos[(org, project)]
        rule = repo._branch_protection_rules.get(parent.branch)
        if not rule or not rule.require_reviews:
            # Github returns None if there is no review required
            return None

        approvals = [r for r in parent.reviews
                     if r.data['state'] == 'APPROVED']
        if approvals:
            return 'APPROVED'

        return 'REVIEW_REQUIRED'


class FakeRepository(ObjectType):
    name = String()
    branchProtectionRules = Field(FakeBranchProtectionRules, first=Int())
    pullRequest = Field(FakePullRequest, number=Int(required=True))
    object = Field(FakeCommit, expression=String(required=True))

    def resolve_name(parent, info):
        org, name = parent.name.split('/')
        return name

    def resolve_branchProtectionRules(parent, info, first):
        return parent._branch_protection_rules

    def resolve_pullRequest(parent, info, number):
        return parent.data.pull_requests.get(number)

    def resolve_object(parent, info, expression):
        return parent._commits.get(expression)


class FakeGithubQuery(ObjectType):
    repository = Field(FakeRepository, owner=String(required=True),
                       name=String(required=True))

    def resolve_repository(root, info, owner, name):
        return info.context._data.repos.get((owner, name))
