'''Posts a comment to a Bitbucket pull request, with optional arguments for 'Jenkins build 
annotations', indicating build status, encasing content in 'diff markdown', and more!
'''
import configargparse
import mdfrag
import requests

import ntsbuildtools.io
from ntsbuildtools.markdown.comments import MarkdownComment


def main(args):
    # Get the core comment message from args -- these options are mutually exclusive (see config_parser)
    comment = MarkdownComment()
    if args.comment_message:
        comment.add_message(args.comment_message)
    elif args.comment_file:
        message_data = ntsbuildtools.io.readfile(args.comment_file)
        comment.add_message(message_data)
    if args.build_annotation:
        comment.add_build_annotation(args.build_id, args.build_url, args.playbook_limit, args.build_status)
    if args.trim:
        comment.trim_comment(args.trim)

    if len(str(comment).strip()) == 0:
        raise ValueError("Some comment contents must be provided -- the comment to be sent was an empty string.")

    # Actually make the request
    try:
        # If the comment will exceed the max comment size, do fragmentation instead!
        if args.max_comment_size and len(str(comment)) > args.max_comment_size:
            comment_fragments = mdfrag.split_markdown(str(comment), args.max_comment_size)
            # Comments are in reverse chronological, so we should render the fragments in reverse.
            comment_fragments.reverse()
            # cp_i => "Comment Part Index"
            cp_i = len(comment_fragments)
            for comment_part in comment_fragments:
                pagination_str = f'> Comment __{cp_i}__ of __{len(comment_fragments)}__.'
                msg = f'{pagination_str}\n{comment_part}'
                cp_i -= 1
                response = requests.post(
                    f'{args.bitbucket_url}/rest/api/1.0/projects/{args.project}/repos/{args.repo}/pull-requests/{args.pull_request_id}/comments',
                    json={'text': msg},
                    auth=(args.user, args.password)
                )
                response.raise_for_status()
        else:
            response = requests.post(
                f'{args.bitbucket_url}/rest/api/1.0/projects/{args.project}/repos/{args.repo}/pull-requests/{args.pull_request_id}/comments',
                json={'text': str(comment) if comment else '*Empty string provided.*'},
                auth=(args.user, args.password)
            )
            response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(f"[ERROR] HTTP Error ({error.response.status_code}): {error.response.text}")
        exit(-1)

def config_parser(parser: configargparse.ArgParser):
    # Parse the 'comment type' with mutex logic -- don't allow user to provide more than one type of message from the provided options.
    possible_inputs = parser.add_mutually_exclusive_group(required=True)
    possible_inputs.add('--message', '-m', dest='comment_message',
                        help='Provide the comment as a message on the command line.')
    possible_inputs.add('--file', '-f', dest='comment_file',
                        help='Provide the comment in a file.')
    # Core parsing bits.
    parser.add('--bitbucket-url', env_var='BITBUCKET_URL', help="URL for Bitbucket.")
    parser.add('--user', required=True, env_var='BITBUCKET_USER',
               help="Bitbucket user that will be used to authenticate to Bitbucket.")
    parser.add('--password', required=True, env_var='BITBUCKET_PASSWORD',
               help="Bitbucket password (or Personal Access Token) for the Bitbucket user.")
    parser.add('--project', required=True, env_var='BITBUCKET_PROJECT',
               help='The Bitbucket project key for the project where the pull request exists.')
    parser.add('--repo', required=True, env_var='BITBUCKET_REPO',
               help='The Bitbucket repository slug for the repository where the pull request exists.')
    parser.add('--pull-request-id', required=True, env_var='PR_ID',
               help='The ID of the Bitbucket pull request to be commented on.')
    # Group of arguments to do with formatting.
    formatting = parser.add_argument_group('formatting')
    formatting.add(
        '--max-comment-size', 
        type=int,
        default=32767,  # Default max comment size in Bitbucket is 32768 bytes
        help='Fragment the comment into chunks smaller than this, in bytes.')
    formatting.add(
        '--trim', '--tail',
        type=int,
        help='Only print the last `TRIM` lines of the provided message/file.'
    )
    # Build Annotation (aka 'ba') parser.
    ba_parser = parser.add_argument_group('Build Annotation')
    ba_parser.add('--build-annotation', action='store_true',
                  help='Provide a "build annotation" in the comment, with information about a Jenkins build.')
    ba_parser.add('--playbook-limit', env_var='PLAYBOOK_LIMIT',
                  help='A string indicating the PLAYBOOK_LIMIT for this build. (Optional)')
    ba_parser.add('--build-id', env_var='BUILD_ID',
                  help='Jenkins build ID. (Optional)')
    ba_parser.add('--build-url', env_var='BUILD_URL',
                  help="Direct-URL to the Jenkins build. (Optional)")
    ba_parser.add('--build-status', choices=['SUCCESS', 'UNSTABLE', 'FAILURE', 'NOT_BUILD', 'ABORTED'],
                  help='The build status to be reported in the comment. Accepts Jenkins build statuses.')
