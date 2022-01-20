import enum

import ntsbuildtools.io
from ntsbuildtools.teams.card_template import TeamsCardTemplate
from ntsbuildtools.markdown.comments import MarkdownComment
from ntsbuildtools.util import hasattr_nonempty_str

class TeamsMessageTypes(enum.Enum):
    PULL_REQUEST = 'pull-request'
    BUILD_STATUS = 'build-status'

    @classmethod
    def values(cls):
        return [member.value for member in cls]

class PullRequestCard(TeamsCardTemplate):
    def __init__(self, args):
        required_arguments = {'bitbucket_url', 'project', 'repo_slug', 'pull_request_id', 'pull_request_author', 'pull_request_title', 'pull_request_dest'}
        optional_arguments = {'pull_request_description', 'playbook_limit', 'jenkins_build_url', 'build_status'}
        super().__init__(required_arguments, optional_arguments, args)

    def build(self, args):
        # Calculate URLs for the pull request, based on args
        pull_request_url = f'{args.bitbucket_url}/projects/{args.project}/repos/{args.repo_slug}/pull-requests/{args.pull_request_id}'
        pull_request_diff_url = pull_request_url + "/diff"

        # Set the title using a (module-level) helper method
        self.set_title(f"Pull Request {args.pull_request_id}: {args.pull_request_title}")
        # Section with pull request facts
        pr_facts = self.add_section()
        pr_facts.add_fact("Requested by", args.pull_request_author)
        if hasattr_nonempty_str(args, 'playbook_limit'):  # playbook_limit is optional
            pretty_playbook_limit = args.playbook_limit.replace(',', ' ︙ ')
            pr_facts.add_fact("Playbook limit", pretty_playbook_limit)
        if hasattr_nonempty_str(args, 'build_status'):  # build_status is optional
            if args.build_status == 'FAILURE':  # Add emphasis if this is a failure.
                pr_facts.add_fact("Build Status", f'***{args.build_status}***')
            else:
                pr_facts.add_fact("Build Status", args.build_status)

        pr_facts.add_fact("Destination branch", args.pull_request_dest)

        # Section with the pull request description (optional)
        if hasattr_nonempty_str(args, 'pull_request_description'): 
            self.add_section().add_text(args.pull_request_description)

        # Actions that you should take now (buttons at the bottom)!
        self.add_button(f"Review PR #{args.pull_request_id}", pull_request_url)
        self.add_button("See proposed changes!", pull_request_diff_url)
        if hasattr_nonempty_str(args, 'jenkins_build_url'):
            self.add_button("Jenkins build", args.jenkins_build_url)
            # TODO: Add a 'Rebuild in Jenkins' button also (which will be possible only if ditch our 'buildWithParameters' pipelines so we can use the '/build' endpoint )


class PullRequestUpdateCard(TeamsCardTemplate):
    def __init__(self, args):
        required_arguments = {'pull_request_id'}
        optional_arguments = {'pull_request_author'}
        super().__init__(required_arguments, optional_arguments, args)

    def build(self, args):
        self.set_title(f"Pull Request {args.pull_request_id} [update]")
        # This simple card only shows the 'PR requestor' fact.
        if hasattr_nonempty_str(args, 'pull_request_author'):
            self.add_section().add_fact("Requested by", args.pull_request_author)


class BuildFailCard(TeamsCardTemplate):
    def __init__(self, args): 
        required_arguments = {'jenkins_build_id', 'jenkins_build_url', 'status', 'build_type'}
        optional_arguments = {'jenkins_job_name', 'pipeline_name', 'playbook_limit', 'pull_request_id', 'pull_request_url'}
        super().__init__(required_arguments, optional_arguments, args)

    def build(self, args):
        self.set_title(f'{args.build_type} {args.status.capitalize()}')
        build_facts = self.add_section()
        build_facts.add_fact("Jenkins Build", f'[Build #{args.jenkins_build_id}]({args.jenkins_build_url})')
        if hasattr_nonempty_str(args, 'pull_request_id') and hasattr_nonempty_str(args, 'pull_request_url'):
            build_facts.add_fact("Pull Request", f"[PR #{args.pull_request_id}]({args.pull_request_url})")
        if hasattr_nonempty_str(args, 'playbook_limit'):  # Optional
            build_facts.add_fact("Playbook limit", args.playbook_limit)
        if hasattr_nonempty_str(args, 'jenkins_job_name'):  # Optional
            pipeline_url = args.jenkins_build_url.rsplit('/',2)[0]
            pipeline_name = args.jenkins_job_name.replace('/',' ︙ ')
            build_facts.add_fact("Jenkins Pipeline", f"[{pipeline_name}]({pipeline_url})")
        self.add_button(f'Review {args.status} {args.build_type}', args.jenkins_build_url)
        self.add_button('Review Console Text', args.jenkins_build_url + "/console")


class BuildSuccessCard(TeamsCardTemplate):
    def __init__(self, args):
        required_arguments = {'build_type', 'status'}
        optional_arguments = {'pull_request_id', 'pull_request_url', 'playbook_limit'}
        super().__init__(required_arguments, optional_arguments, args)

    def build(self, args):
        self.set_title(f'{args.build_type} {args.status.capitalize()}')
        build_facts = self.add_section()    
        if hasattr_nonempty_str(args, 'pull_request_id') and hasattr_nonempty_str(args, 'pull_request_url'):
            build_facts.add_fact("Pull Request", f"[PR #{args.pull_request_id}]({args.pull_request_url})")
        elif hasattr_nonempty_str(args, 'pull_request_id'):
            build_facts.add_fact("Pull Request", f"PR #{args.pull_request_id}")
        if hasattr_nonempty_str(args, 'playbook_limit'):  # playbook_limit is optional
            pretty_playbook_limit = args.playbook_limit.replace(',', ' ︙ ')
            build_facts.add_fact("Playbook limit", pretty_playbook_limit)


class TeamsCardFactory:
    """Generates preformatted TeamsCard objects. This class is just a container for a bunch of static
    methods that parse 'args' (generally provided from python argparse) and determine what type of 
    TeamsCardTemplate should be built.
    """
    # TODO Could have a 'def register_card(message_type,additional_condition=foo())' 
    @staticmethod
    def build(args, message_type: TeamsMessageTypes):
        """Create a preformatted card -- the type of card built is based args provided.

        Args:
            args (argparse.Namespace): An 'arguments' object that contains all of the details required to 
            build a particular TeamsCard.  
            message_type (TeamsMessageTypes): Determines which type of TeamsCard to return -- depending
            on the message type, additional arguments will be required as well.

        Raises:
            ValueError: If the message_type specified is invalid.
            TypeError: If there are missing arguments from `args`

        Returns:
            TeamsCardTemplate: A Teams Card, built based on the arguments provided.
        """
        card = TeamsCardFactory._build(args, message_type)
        TeamsCardFactory._add_messages(args, card)
        return card

    @staticmethod
    def _add_messages(args, card):
        """Add 'messages' that are found in `args` to `card`.

        :param args: The args to be scanned for `message` or `file`.
        :param card: The card that will be updated with any 'messages' found in `args`.
        :return: The card.
        """
        if hasattr_nonempty_str(args, 'message') and len(args.message) > 0:
            TeamsCardFactory._add_message(args, card, args.message)
        if hasattr_nonempty_str(args, 'file') and len(args.file) > 0:
            TeamsCardFactory._add_message(args, card, ntsbuildtools.io.readfile(args.file))
        return card

    @staticmethod
    def _add_message(args, card, message):
        """Add the message to the card. Formatting details may be specified in args.

        :param args: The args to be scanned for formatting details, e.g. `max_size`, and `code_markdown`
        :param card: The card that will be updated with the `message`.
        :param message: The message to be added to the `card`.
        :return: The card.
        """
        content = MarkdownComment()

        trimmed = False
        if args.max_size and len(message) > args.max_size:
            message = message[0:args.max_size]
            trimmed = True

        if hasattr(args, 'code_markdown') and args.code_markdown:
            content.add_code_markdown(message)
        else:
            content.add_message(message)

        if trimmed:
            content.add_message("\n> *Message trimmed. **See Pull Request** for full message...*")

        card.add_section(str(content))

    @staticmethod
    def _build(args, message_type):
        # Handle the 'build status' message types
        if message_type == TeamsMessageTypes.BUILD_STATUS.value: 
            return TeamsCardFactory._build_build_status_card(args)
        # Handle the 'pull request' message types
        if message_type == TeamsMessageTypes.PULL_REQUEST.value:
            return TeamsCardFactory._build_pull_request_card(args)
        # If the message type doesn't align with what we've got, should we just return an empty card or throw an error?
        raise ValueError(f'Expected message_type to be one of: {", ".join(TeamsMessageTypes.values())}')

    @staticmethod
    def _build_build_status_card(args):
        # Check that we have required args to at least execute this factory method.
        if not hasattr_nonempty_str(args, 'status'):
            raise TypeError(f'To create a Card with message-type={TeamsMessageTypes.BUILD_STATUS}, the `status` arg must be provided.')
        # Set the 'build_type' string based on the message_type
        if args.status.upper() == 'SUCCESS':
            return BuildSuccessCard(args)
        else:
            return BuildFailCard(args)

    @staticmethod
    def _build_pull_request_card(args):
        if hasattr(args, 'pull_request_update') and args.pull_request_update is True:
            return PullRequestUpdateCard(args)
        else: 
            return PullRequestCard(args)
