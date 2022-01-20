"""Posts a preformatted card (aka 'actionable message', or 'MessageCard') to a Microsoft Teams channel.

This script supports specific preformatted messages oriented towards supporting Jenkins build processes."""
import configargparse
import requests
import logging
import sys

import ntsbuildtools.subcommands
import ntsbuildtools.teams.cards

logger = logging.getLogger(__name__)


def config_parser(parser):
    BUILD_STATUSES = ['STARTED', 'SUCCESS',
                      'UNSTABLE', 'FAILURE', 'NOT_BUILD', 'ABORTED']
    parent_parser = configargparse.ArgParser(add_help=False)
    parent_parser.add(
        '--webhook-url', '-u', 
        required=True, 
        env_var='TEAMS_WEBHOOK_URL',
        help='The Teams "Incoming Webhook" URL for a Teams channel (where messages will be posted).'
    )
    parent_parser.add(
        '--bitbucket-url',
        env_var='BITBUCKET_URL', 
        help="URL for Bitbucket."
    )
    parent_parser.add(
        '--message',
        help='Custom messgage to be printed at the bottom of the card.'
    )
    parent_parser.add(
        '--file', 
        help='''Custom message to be printed at the bottom of the card, loaded from the
                file-path indicated by this argument.'''
    )
    parent_parser.add(
        '--diff-markdown', 
        action='store_true',
        help='Wrap the custom message(s) in ```diff\n{message}\n``` markdown.'
    )
    parent_parser.add(
        '--code-markdown', 
        action='store_true',
        help='Wrap the custom message(s) in ```\n{message}\n``` markdown.'
    )
    parent_parser.add(
        '--max-size', 
        '--trim', 
        dest='max_size', 
        type=int, 
        default=24000,  # 28 KB is the limit today -- leave 4 KB for our meta-data + Teams meta-data.
        help='''Truncate the message, to avoid surpassing Teams "Channel conversation post size" limitation 
                (See https://docs.microsoft.com/en-us/microsoftteams/limits-specifications-teams#chat).'''
    )

    subparsers = parser.add_subparsers(
        title="message-type", dest='message_type',
        description="There are built in 'message types' that can be sent."
    )
    subparsers.required = True

    # Subparser for Build Status Cards
    build_status = subparsers.add_parser(
        ntsbuildtools.teams.cards.TeamsMessageTypes.BUILD_STATUS.value, 
        parents=[parent_parser], help='Generate a "Jenkins build status" message.'
    )
    build_status.add('status', choices=BUILD_STATUSES,
                     help='Provide the build status here (from the provided choices).')
    build_status.add('--build-type', default='BUILD', choices=['BUILD', 'DEPLOYMENT'],
                     help="The 'type' of the build (from provided choices).")
    build_status.add('--jenkins-build-url', env_var='BUILD_URL',
                     help='The URL that links directly to the Jenkins build.')
    build_status.add('--pull-request-url', env_var='PR_URL',
                     help='The URL that links directly to the Pull Request to which this build is associated.')
    build_status.add('--pull-request-id', env_var='PR_ID',
                     help='The ID of the Bitbucket pull request.')
    build_status.add('--jenkins-job-name', env_var='JOB_NAME',
                     help='The name of the Job in Jenkins.')
    build_status.add('--jenkins-build-id', env_var='BUILD_ID',
                     help='The ID of this particular build in Jenkins.')
    build_status.add('--playbook-limit', env_var='PLAYBOOK_LIMIT',
                     help='A string indicating the PLAYBOOK_LIMIT for this build.')

    # Subparser for Pull Request Cards
    pull_request = subparsers.add_parser(
        ntsbuildtools.teams.cards.TeamsMessageTypes.BUILD_STATUS.PULL_REQUEST.value, 
        parents=[parent_parser], help='Generate a "Bitbucket Pull Request" message.'
    )
    pull_request.add('--pull-request-id', env_var='PR_ID',
                     help='The ID of the Bitbucket pull request.')
    pull_request.add('--pull-request-update', action='store_true', env_var='PR_UPDATE',
                     # TODO Document the following: Assign "true" to PR_UPDATE env variable, per configargparse docs
                     help='Provide this flag if this is a pull request update (it will produce a much smaller/simpler Teams Card).')
    pull_request.add('--pull-request-author', env_var='PR_AUTHOR',
                     help='The person who submitted the Bitbucket pull request.')
    pull_request.add('--project', env_var='BITBUCKET_PROJECT',
                     help='The Bitbucket project key for the project where the pull request exists.')
    pull_request.add('--repo-slug', env_var='BITBUCKET_REPO',
                     help='The Bitbucket repository slug.')
    pull_request.add('--pull-request-title', env_var='PR_TITLE',
                     help='The title of the Bitbucket pull request.')
    pull_request.add('--pull-request-dest', env_var='PR_DESTINATION',
                     help='The destination branch of the Bitbucket pull request.')
    pull_request.add('--pull-request-description', env_var='PR_DESCRIPTION',
                     help='The description of the Bitbucket pull request.')
    pull_request.add('--playbook-limit', env_var='PLAYBOOK_LIMIT',
                     help='A string indicating the PLAYBOOK_LIMIT for this build.')
    pull_request.add('--build-status', choices=BUILD_STATUSES,
                     help='Provide the build status (from the provided choices).')
    pull_request.add('--jenkins-build-url', env_var='BUILD_URL',
                     help='The URL that links directly to the particular Jenkins build.')


def main(args):
    try:
        card = ntsbuildtools.teams.cards.TeamsCardFactory.build(args, args.message_type)
        response = requests.post(args.webhook_url, json=card.to_json())
        response.raise_for_status()
        _raise_for_http_413(response)
    except (requests.exceptions.HTTPError, ntsbuildtools.exceptions.BTTeamsCardFactoryError) as error:
        logger.exception(error)
        print(error)
        sys.exit(1)


def _raise_for_http_413(response):
    # Teams does not actually set the status_code for HTTP 413... so we parse the response.text to handle for it
    if 'HTTP error 413' in response.text:
        response.status_code = 413
        response.raise_for_status()
