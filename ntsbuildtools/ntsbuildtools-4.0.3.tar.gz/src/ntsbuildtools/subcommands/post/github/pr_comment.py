'''Posts a comment to a GitHub pull request.

If a comment is too large to fit as a single comment in github, this solution can 
fragment a comment into pieces (via the `--max-comment-size` argument).
'''
import mdfrag
import requests

import ntsbuildtools.io
from ntsbuildtools.markdown.comments import MarkdownComment


def config_parser(parser):
    # Parse the 'comment type' with mutex logic -- don't allow user to provide more than one type of message from the provided options.
    message_parser = parser.add_mutually_exclusive_group(required=True)
    message_parser.add('--message', '-m', dest='comment_message',
                       help='Provide the comment as a message on the command line.')
    message_parser.add('--file', '-f', dest='comment_file',
                       help='Provide the comment in a file.')
    # Core parsing bits
    parser.add('--user', required=True, env_var='BITBUCKET_USER',
               help="GitHub user that will be used to authenticate to GitHub.")
    parser.add('--password', required=True, env_var='BITBUCKET_PASSWORD',
               help="GitHub password (or Personal Access Token) for the GitHub user.")
    parser.add('--project', required=True, env_var='GITHUB_PROJECT',
               help='The GitHub "owner" or "organization" for the repository.')
    parser.add('--repo', required=True, env_var='GITHUB_REPO',
               help='The GitHub repository slug for the repository.')
    parser.add('--pull-request-id', required=True, env_var='PR_ID',
               help='The ID of the GitHub pull request to be commented on.')
    # Group of arguments to do with formatting.
    formatting = parser.add_argument_group('formatting')
    formatting.add('--max-comment-size', type=int,
                   help='Fragment the comment into based on the maximum comment size.')
    ba_parser = formatting.add_argument_group('Build Annotation')
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

    if len(str(comment).strip()) == 0:
        raise ValueError(
            "Some comment contents must be provided -- the comment to be sent was an empty string.")

    # Actually make the HTTP Post request to publish the comment
    try:
        post_url = f'https://api.github.com/repos/{args.project}/{args.repo}/issues/{args.pull_request_id}/comments'
        # If the comment will exceed the max comment size, do fragmentation instead!
        if args.max_comment_size and len(str(comment)) > args.max_comment_size:
            _split_and_post(post_url, args.user, args.password, comment, args.max_comment_size)
        else:
            _post_comment(post_url, args.user, args.password, comment)
    except requests.exceptions.HTTPError as error:
        print(f"[ERROR] HTTP Error ({error.response.status_code}): {error.response.text}")
        exit(-1)

def _post_comment(url, user, password, comment):
    response = requests.post(
        url, 
        json={'body': str(comment) if comment else '*Empty string provided.*'},
        auth=(user, password)
    )
    response.raise_for_status()

def _split_and_post(url, user, password, comment, max_comment_size):
    comment_fragments = mdfrag.split_markdown(str(comment), max_comment_size)
    # Comments are in reverse chronological, so we should render the fragments in reverse.
    comment_fragments.reverse()
    # cp_i => "Comment Part Index"
    cp_i = len(comment_fragments)
    for comment_part in comment_fragments:
        pagination_str = f'> Comment __{cp_i}__ of __{len(comment_fragments)}__.'
        msg = f'{pagination_str}\n{comment_part}'
        cp_i -= 1
        response = requests.post(url, json={'text': msg}, auth=(user, password))
        response.raise_for_status()
