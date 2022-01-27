class StringTokenizer:
    def __init__(self, text, delim, return_delims):
        """
        Constructs a string tokenizer for the specified string. All characters in the delim argument are the delimiters
        for separating tokens. If the return_delims flag is true, then the delimiter characters are also returned as tokens.
        Each delimiter is returned as a string of length one. If the flag is false, the delimiter characters are skipped
        and only serve as separators between tokens.

        :param text: a string to be parsed
        :param delim: the delimiters
        :param return_delims: flag indicating whether to return the delimiters as tokens
        """

        self.current_position = 0
        self.new_position = -1
        self.text = text
        self.max_position = len(text)
        self.delimiters = delim
        self.ret_delims = return_delims

    def skip_delimiters(self, start_pos):
        """
        Skips delimiters starting from the specified position. If self.ret_delims is false,
        returns the index of the first non-delimiter character at or after start_pos.
        If self.ret_delims is true, start_pos is returned.
        """

        if self.delimiters is None:
            raise TypeError

        position = start_pos
        while not self.ret_delims and position < self.max_position:
            c = self.text[position]
            if not self.is_delimiter(c):
                break
            position += 1

        return position

    def scan_token(self, start_pos):
        """
        Skips ahead from start_pos and returns the index of the next delimiter character encountered,
        or self.max_position if no such delimiter is found.
        """

        position = start_pos
        while position < self.max_position:
            c = self.text[position]
            if self.is_delimiter(c):
                break
            position += 1

        if self.ret_delims and start_pos == position:
            c = self.text[position]
            if self.is_delimiter(c):
                position += 1

        return position

    def is_delimiter(self, char):
        return char in self.delimiters

    def has_more_tokens(self):
        """
        Tests if there are more tokens available from this tokenizer's string. If this method returns true,
        then a subsequent call to next_token with no argument will successfully return a token.

        :return: true if and only if there is at least one token in the string after the current position; false otherwise
        """

        # Temporarily store this position and use it in the following next_token() method
        # only if the delimiters haven't been changed in that next_token() invocation.
        self.new_position = self.skip_delimiters(self.current_position)
        return self.new_position < self.max_position

    def next_token(self, delim=None):
        """
        Returns the next token from this string tokenizer
        """
        delims_changed = False
        if delim is not None:
            # First, the set of characters considered to be delimiters by this StringTokenizer object is changed
            # to be the characters in delim.
            # Then the next token in the string after the current position is returned.
            # The current position is advanced beyond the recognized token.
            # The new delimiter set remains the default after this call.
            self.delimiters = delim
            delims_changed = True

        # If next position already computed in has_more_tokens()
        # and delimiters have changed between the computation and this invocation,
        # then use the computed value
        self.current_position = self.new_position if self.new_position >= 0 and not delims_changed else self.skip_delimiters(self.current_position)

        # Reset these anyway
        self.new_position = -1

        if self.current_position >= self.max_position:
            raise ValueError

        start = self.current_position
        self.current_position = self.scan_token(self.current_position)
        return self.text[start:self.current_position]
