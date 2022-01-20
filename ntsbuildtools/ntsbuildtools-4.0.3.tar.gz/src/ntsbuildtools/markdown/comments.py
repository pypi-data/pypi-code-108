import os


class MarkdownComment:
    def __init__(self, message=None):
        """Generate a 'Markdown formatted' string. 

        Create  for various platforms that require Markdown-formatted messaging.

        Args:
            message (str, optional): The (first) message to be added to the comment. Subsequent messages can be added
            with various 'add_*' methods. Defaults to None.
        """
        self._build_annotation = []
        self._comment_data = []
        if message:
            self.add_mesage(message)

    def add_heading(self, level: int, heading: str):
        heading = f"\n{level * '#'} {heading}\n"
        self.add_message(heading, clean_vert_space=False)

    def add_message(self, message, clean_vert_space=True):
        """The core method that 'adds a message' to this MarkdownComment. 
            (Note to developers: All other MarkdownComment methods that add content to this 
            MarkdownComment *should* call this method instead of directly modifying _comment_data).

        Args:
            message (str): The message to be added.
            clean_vert_space (bool, optional): Allow MarkdownComment to clean vertical space in the message. 
                Defaults to True.

        Returns:
            MarkdownComment: Return self to allow a more fluent API -- i.e. enables chaining methods.
        """
        if clean_vert_space:
            # Remove unnecessary vertical whitespace (via rstrip)
            self._comment_data += [line.rstrip()
                                   for line in message.splitlines()]
        else:
            self._comment_data.append(message)
        return self

    def add_code_markdown(self, text, code_type=''):
        """Add a message in a 'code markdown' block. Customized to enable 'code types', which are available in
        Bitbucket.

        Args:
            text (str): The text to be put in the markdown block.
            code_type (str, optional): The 'code_type' which will be inserted in the Markdown to indicate how the code
            should be rendered. I.e. '```{style}'.

        Returns:
            MarkdownComment: Return self to allow a more fluent API -- i.e. enables chaining methods.
        """
        self.add_message(f'\n```{code_type}')
        self.add_message(text, clean_vert_space=False)
        self.add_message('\n```\n', clean_vert_space=False)
        return self

    def add_diff_markdown(self, text):
        """Add a message in a 'diff code markdown' block. Customized to enable 'code types', which are available in Bitbucket.

        Args:
            text (str): The text to be put in the markdown block.

        Returns:
            MarkdownComment: Return self to allow a more fluent API -- i.e. enables chaining methods.
        """
        self.add_code_markdown(text, code_type='diff')
        return self

    def trim_comment(self, tail, verbose=True):
        """Trim the comment down to the last 'tail' # of lines. E.g. `trim_comment(10)` means 'keep only the last 10
        lines.' NOTE: Code Markdown and any messages added with 'clean_vert_space = False' will not be trimmed --
        effectively they have a 'page break' behavior.

        Args:
            tail (int, optional): The amount of lines to be kept from the end of the comment.
        """
        if len(self._comment_data) > tail:
            self._comment_data = self._comment_data[-tail:]
            if verbose:
                self._comment_data.insert(0, '... trimmed for brevity...')

    def add_build_annotation(self, jenkins_build_id=None, jenkins_build_url=None, playbook_limit=None,
                             build_status=None):
        """Add a (Jenkins) build annotation to the build. All arguments are optional, in which case a very simple
        annotation will be prepended to the comment.

        Args:
            playbook_limit (str): The playbook_limit of this particular build, to be displayed in the build annotation
            (optional).
            jenkins_build_id (str): The build ID of the Jenkins build, to be displayed in the build annotation
            (optional). Only used if the build_url is provided as well.
            jenkins_build_url (str): The build URL of the Jenkins build, to be displayed in the build annotation
            (optional). Only used if the build_id is provided as well.

        Returns:
            MarkdownComment: Return self to allow a more fluent API -- i.e. enables chaining methods.
        """
        # Build up a string in a list -- the 'build annotation list' (aka 'bal')
        self._build_annotation.append(
            '> *This comment was automatically generated from Jenkins.* ')

        if jenkins_build_id and jenkins_build_url:
            self._build_annotation.append(
                f'> *View more details in [Jenkins build {jenkins_build_id} '
                f'(link to jenkins build, requires authorization)]({jenkins_build_url}) '
                f'[(Console Output)]({jenkins_build_url}/console).* ')

        if playbook_limit:
            # Make the playbook_limit a bit easier to read by sorting it and adding space-separation
            as_list = playbook_limit.split(',')
            as_list.sort(key=len)
            playbook_limit = ", ".join(as_list)
            playbook_limit = playbook_limit.strip()
            # Add the build annotation
            self._build_annotation.append(
                "> NOTICE: To adjust the Playbook limit from this pull request, click the '...' menu in the top right "
                "and select 'Build in Jenkins'.")
            self._build_annotation.append(
                f'\n\n Playbook limit: **{playbook_limit}**')

        # if the build status is provided, then print it in bold for all to see!
        if build_status:
            self._build_annotation.append(
                f'\n#### ***BUILD {build_status}***\n')

        # Add a horizontal line
        self._build_annotation.append("\n___\n")
        return self

    def add_text_horizontal_rule(self):
        """Add a horizontal rule (---) to the comment.

        Returns:
            MarkdownComment: Return self to allow a more fluent API -- i.e. enables chaining methods.
        """
        # vertical whitespace is trimmed nicely in Teams, so use generous newlines.
        self.add_message("\n\n___\n\n")
        return self

    def render(self):
        """'Render' this MarkdownComment as a string.

        Returns:
            str: This markdown comment, formatted.
        """
        end_of_comment_newline = ['\n']
        return os.linesep.join(self._build_annotation + self._comment_data + end_of_comment_newline)

    def __str__(self):
        """Convert this MarkdownComment into a string (overridden).

        Returns:
            str: This markdown comment, formatted.
        """
        return self.render()
