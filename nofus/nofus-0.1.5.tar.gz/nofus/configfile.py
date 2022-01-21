"""
****************************************************************************************
NOFUS Config File Parser for Python
****************************************************************************************
Copyright 2019 Nathan Collins. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Nathan Collins ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Nathan Collins OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Nathan Collins.

*****************************************************************************************

****************************************
* Config file line examples
****************************************

# Pound sign is a line comment
# Variable assignment is done with an "=" sign
var1 = 42
var2 = 94                                           # comments can appear at the end of a line
name = Example
longname = John Doe                                 # would parse as "John Doe"
name2 = " Jane Doe "                                # to prevent whitespace trimming, add double
                                                    # quotes; would parse as " Jane Doe "
name3 = 'Jerry'                                     # single quotes parse as normal characters;
                                                    # this last line would parse as "'Jerry'"
words = "Quotes \"inside\" a string"                # can use double quotes inside double quotes,
                                                    # but must be escaped
specials = "This has #, \\, and = inside of it"     # can use special characters in a quoted value
                                                    # (escape character must be escaped)
badquoted = this is "NOT" a quoted string           # value doesn't start with a quote, so quotes
                                                    # are treated as normal chars
oddquote = "not a quoted value" cause extra         # value will parse as:
                                                    #  "\"not a quoted value\" cause extra"
novalue =                                           # values can be left blank
enable_keys                                         # no assignment delimiter given (aka '='),
                                                    # variable is assigned boolean value true
multi_valued = abc
multi_valued = xyz                                  # variables can be defined multiple times and
                                                    # retrieved as an array

// Alternate line comment style

# variables can have a scope by placing a dot in their identifier
marbles.green = 2
marbles.blue = 4
marbles.red = 3

# alternatively, you can set scope on variables by making a section using []
[marbles]
white = 6
clear = 8
yellow = 1

[sql.maria]                         # scopes can have sub-scopes as well (and comments)
auth.server = sql.example.com
auth.user = apache                  # e.g. full scope is: sql.maria.auth.user
auth.pw = secure
auth.db = website

**************************************
* Invalid examples
**************************************

my var = my val         # spaces are not allowed in variable identifiers
[]#.$ = something       # only a-zA-Z0-9_- are allow for var identifier (. is allowed for scope)
[my.scope]  = val       # scopes cannot have values
a..b = c                # scopes cannot be blank
.d. = e                 # start and end scope can't be blank


**************************************
* Use examples
**************************************

cf = ConfigFile("test.conf");
if (cf.load()) {
    # can preload default values, even after loading
    cf.preload( {
            "var1": 12,
            "name": "none",
            "enable_keys": false,
            "marbles.green": 0
        } );

    v1 = cf.get("var1");         # get value from var1, or null if doesn't exist
    v9 = cf.get("var9", 123);    # get value from var9, or 123 if doesn't exist

    arr = cf.get_list("multi_valued");   # get all values for multi_valued as an array

    mw = cf.get("marbles.white", 1);     # get marbles.white, or 1 if doesn't exist
    pw = cf.get("sql.maria.auth.pw");    # get sql.maria.auth.pw, or null if doesn't exist

    sql = cf.get('sql.maria');           # get a scope
    svr = sql.get('auth.server');        # get auth.server (in sql.maria scope)
                                         # or null if doesn't exist

    bad = cf.get('does.not.exist');      # attempt to get a non-existant scope, returns null

    subscopes = cf.enumerate_scope("sql.maria.auth"); # return array of ['server','user','pw','db']
"""
import os
import re
from collections.abc import Mapping

class ConfigFile:
    """
    The main ConfigFile class
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, file_to_open=None):
        # File Info
        self.file_path = None
        self.loaded = False

        # Static parse values
        self.line_comment_start = [r'#', r'//']
        self.var_val_delimiter = '='
        self.scope_delimiter = '.'
        self.quote_char = '"'
        self.escape_char = "[\\\\]"
        self.scope_char_set = r"a-zA-Z0-9_\-"
        self.varname_char_set = r"a-zA-Z0-9_\-"

        # Dynamic parse values
        self.current_scope = ""

        # Errors
        self._errors = []

        # Keys with preloaded values
        self.preloaded = {}

        # Parsed Content
        self.values = {}

        # Parse file_to_open
        if file_to_open is not None and isinstance(file_to_open, str):
            self.file_path = file_to_open

    def _override_comment_starts(self, line_comment_start):
        """
        Change what strings indicate the start of a comment.
        WARNING: Change this at your own risk. Setting unusual values here may break parsing.
        :type list_or_string: Union[list, string]
        :param line_comment_start list_or_string
                An array containing strings which indicate the start of a comment
                OR a string that indicates the start of a comment
        """
        if not isinstance(line_comment_start, list) and isinstance(line_comment_start, str):
            self.line_comment_start = [line_comment_start]
        self.line_comment_start = line_comment_start

    def _override_variable_delimiter(self, var_val_delimiter):
        """
        Change the delimiter used between variable name and values.
        WARNING: Change this at your own risk. Setting unusual values here may break parsing.
        :param var_val_delimiter string The string to indicate the delimiter between variable
            name and value
        """
        self.var_val_delimiter = var_val_delimiter

    def _override_scope_delimiter(self, scope_delimiter):
        """
        Change the string used as a delimiter between scopes.
        WARNING: Change this at your own risk. Setting unusual values here may break parsing.
        :param scope_delimiter string The string to indicate the delimiter between scopes
        """
        self.scope_delimiter = scope_delimiter

    def _override_quote_character(self, quote_char):
        """
        Change the character used to quote variable values.
        WARNING: Change this at your own risk. Setting unusual values here may break parsing.
        :param quote_char string The character to indicate the start and end of a quoted value
        """
        self.quote_char = quote_char

    def _override_escape_character(self, escape_char):
        """
        Change the character used to escape other characters in a variable value
        WARNING: Change this at your own risk. Setting unusual values here may break parsing.
        :param escape_char string The character to indicate an excaped character follows
        """
        self.escape_char = fr"[{escape_char}]"

    def _override_scope_characters(self, scope_char_set):
        """
        Change the regular expression patterned used to verify valid scope names.
        WARNING: Change this at your own risk. Setting unusual values here may break parsing.
        :param scope_char_set string A regexp patterns to indicate allowed characters in scope name
        """
        self.scope_char_set = scope_char_set

    def _override_variable_name_characters(self, varname_char_set):
        """
        Change the regular expression patterned used to verify valid variable names.
        WARNING: Change this at your own risk. Setting unusual values here may break parsing.
        :param varname_char_set string A regexp patterns to indicate allowed characters in
            variable name
        """
        self.varname_char_set = varname_char_set

    def preload(self, defaults):
        """
        Load in default values for certain variables/scopes. If a variable already
        exists (e.g. from a file that was already loaded), then this will NOT overwrite
        the value.
        :param defaults dict A dictionary of "scope.variable": "default value" pairs
                         OR dict value may also be another dict of values
        """
        for name, value in defaults.items():
            if not name in self.values:
                self.preloaded[name] = True
                if isinstance(value, (list, Mapping)):
                    self.values[name] = value
                else:
                    self.values[name] = [value]

    def reset(self):
        """
        Reset the config file object, basically "unloading" everything so it can be reloaded.
        """
        self.loaded = False
        self._errors = []
        self.values = {}

    def load(self):
        """
        Attempt to open and parse the config file.
        :returns boolean True if the file loaded without errors, false otherwise
        """
        # If we've successfully loaded this file before, skip the load and return success
        if self.loaded is True:
            return True

        # If file is null, then this is a scope query result, do nothing
        if self.file_path is None:
            self._errors.append("Cannot load file; no file was given. "
                                "(Note: you cannot load() a query result.)")
            return False

        if not os.path.isfile(self.file_path) or not os.access(self.file_path, os.R_OK):
            self._errors.append("Cannot load file; file does not exist or is not readable.")
            return False

        lines = []
        try:
            with open(self.file_path, encoding='utf8') as cfile:
                lines = cfile.readlines()
        except OSError:
            self._errors.append("Cannot load file; unknown file error.")
        lines = [line.rstrip('\r\n') for line in lines]

        # Process lines
        for line_num, line in enumerate(lines):
            self._process_line(line_num, line)

        # If parsing lines generated errors, return false
        if len(self._errors) > 0:
            return False

        # Make it past all error conditions, so return true
        self.loaded = True
        return True

    def _find_line_comment_position(self, line, search_offset=0):
        """
        Find the position of the first line comment (ignoring all other rules)
        :param line string The line to search over
        :param search_offset int Offset from start of line in characters to skip before searching
        :returns int|false The position of line comment start or false if no line comment found
        """
        start = False
        for comment_start in self.line_comment_start:
            start_check = line.find(comment_start, search_offset)
            if start_check != -1 and (start is False or start_check < start):
                start = start_check

        return start

    def _find_assignment_delimiter_position(self, line):
        """
        Find the position of the first assignment delimiter (ignoring all other rules)
        :param line string The line to search over
        :returns int|false The position of the assignment delimiter or false if no delimiter found
        """
        pos = line.find(self.var_val_delimiter)
        return pos if pos != -1 else False

    def _find_open_quote_position(self, line):
        """
        Find the position of the opening double quote character (ignoring all other rules)
        :param line string The line to search over
        :returns int|false The position of the double quote, or false is not found
        """
        pos = line.find(line, self.quote_char)
        return pos if pos != -1 else False

    def _is_valid_scope_definition(self, line):
        """
        Given a line, check to see if it is a valid scope definition
        :param line string The line to check
        :return boolean Returns true if well formed and valid, false otherwise
        """
        valid_char_set = self.scope_char_set
        scope_char = re.escape(self.scope_delimiter)
        esc_comment_starts = ''
        for comment_start in self.line_comment_start:
            if esc_comment_starts != '':
                esc_comment_starts += '|'
            esc_comment_starts += re.escape(comment_start)

        scope_pattern = fr'^\s*\[\s*(?:[{valid_char_set}]+' + \
                        fr'(?:{scope_char}[{valid_char_set}]+)*)?\s*\]' + \
                        fr'\s*(?:({esc_comment_starts}).*)?$'

        # default to not a scope
        valid = False
        # check for validity
        patt = re.compile(scope_pattern)
        if patt.search(line):
            valid = True

        return valid

    def _set_scope(self, line):
        """
        Set the current scope (assumes the line is a scope definition) while parsing the file.
        Does nothing if line is not a scope definition.
        :param line string The line to get the scope from
        """
        valid_char_set = self.scope_char_set
        scope_char = re.escape(self.scope_delimiter)
        esc_comment_starts = ''
        for comment_start in self.line_comment_start:
            if esc_comment_starts != '':
                esc_comment_starts += '|'
            esc_comment_starts += re.escape(comment_start)

        scope_pattern = fr'^\s*\[\s*([{valid_char_set}]+' + \
                        fr'(?:{scope_char}[{valid_char_set}]+)*)?\s*\]' + \
                        fr'\s*(?:({esc_comment_starts}).*)?$'

        # check for invalid characters
        patt = re.compile(scope_pattern)
        match = patt.search(line)
        if match and len(match.groups()) == 2:
            self.current_scope = "" if match.group(1) is None else match.group(1)

    def _has_value_delimiter(self, line):
        """
        Check if line has a value delimiter. Can only return true if the line
        also has a valid variable name.
        :param line string The line to check against
        :returns boolean Returns true if line has a delimiter after a valid variable name
        """
        has_delim = False
        if self._has_valid_variable_name(line):
            esc_delim = re.escape(self.var_val_delimiter)
            delim_pattern = re.compile(fr'^[^{esc_delim}]+{esc_delim}')
            match = re.search(delim_pattern, line)
            if match:
                has_delim = True

        return has_delim

    def _has_quoted_value(self, line, line_for_error=None):
        """
        Checks if the line has a valid quoted value.
        :param line string $sLine The line to check
        :param line_for_error int|none If a line number is provided, will add error
            messages if invalidly quoted
        :return boolean Returns true if a quoted value exist, false otherwise
        """
        # pylint: disable=unused-argument
        # TODO line_for_error
        #################################################
        # - Variable name must be valid
        # - Assignment delimiter must exist after variable name (allowing for whitespace)
        # - First character after assignment delimiter must be a quote (allowing for whitespace)
        # - Assignment delimiter and open quote must not be in a comment
        # - A matching quote character must exist to close the value
        # - The closing quote has no other chars are after it (other than whitespace and comments)
        #################################################
        quoted_value = False
        if self._has_valid_variable_name(line):
            esc_delim = re.escape(self.var_val_delimiter)
            esc_quote = re.escape(self.quote_char)
            esc_escape = self.escape_char
            esc_comment_starts = ""

            for comment_start in self.line_comment_start:
                if esc_comment_starts != '':
                    esc_comment_starts += '|'
                esc_comment_starts += re.escape(comment_start)

            quote_val_patterns = re.compile(fr'^[^{esc_delim}]+{esc_delim}\s*{esc_quote}' + \
                                            fr'(?:{esc_escape}{esc_quote}|[^{esc_quote}])*' + \
                                            fr'(?<!{esc_escape}){esc_quote}\s*' + \
                                            fr'(?:({esc_comment_starts}).*)?$')

            match = quote_val_patterns.search(line)
            if match and len(match.groups()) == 1:
                quoted_value = True

        return quoted_value

    def _get_quoted_value(self, line):
        """
        Returns the content from inside a properly quoted value string given a whole line.
        The content from inside the string may still have escaped values.
        :param line string The line to operate from
        :return string The value between the opening and closed quote of the value
            (does NOT include open/closing quotes); on failure, returns empty string.
        """
        value = ""
        if self._has_valid_variable_name(line):
            esc_delim = re.escape(self.var_val_delimiter)
            esc_quote = re.escape(self.quote_char)
            esc_escape = self.escape_char
            esc_comment_starts = ""

            for comment_start in self.line_comment_start:
                if esc_comment_starts != '':
                    esc_comment_starts += '|'
                esc_comment_starts += re.escape(comment_start)

            quote_val_patterns = re.compile(fr'^[^{esc_delim}]+{esc_delim}\s*{esc_quote}' + \
                                            fr'((?:{esc_escape}{esc_quote}|[^{esc_quote}])*)' + \
                                            fr'(?<!{esc_escape}){esc_quote}\s*' + \
                                            fr'(?:({esc_comment_starts}).*)?$')

            match = quote_val_patterns.search(line)
            if match and len(match.groups()) == 2:
                value = match.group(1)

        return value

    def _get_variable_value(self, line, line_for_error=None):
        """
        Get the processed value for the given line. Handles quotes, comments,
            and unescaping characters.
        :param line string The line to operate from
        :param line_for_error int|null If a line number is provided, will add error messages
            if invalidly quoted
        :return string The value processed variable value
        """
        value = False
        if self._has_valid_variable_name(line):
            value = True
            if self._has_value_delimiter(line):
                value = ""
                if self._has_quoted_value(line, line_for_error):
                    # getting the quoted value will strip off comments automatically
                    value = self._get_quoted_value(line)
                else:
                    value = self._get_post_delimiter(line)
                    # handle comments
                    comment_start = self._find_line_comment_position(value)
                    if comment_start is not False:
                        value = value[0:comment_start]
                    value = value.strip()

                # handle escaped chars
                unescape_pattern = fr'{self.escape_char}(.)'
                unescape_replace = r'\1'
                value = re.sub(unescape_pattern, unescape_replace, value)

        return value

    def _get_pre_delimiter(self, line):
        """
        Returns the trimmed string before any delimiter on a line.
         - Removes comments from line
         - If no delimiter is present, returns the whole line (minus any comment)
        :param line string The line to operate from
        :return string The value before any delimiter
        """
        assign_delim_pos = self._find_assignment_delimiter_position(line)
        line_comment_pos = self._find_line_comment_position(line)

        # if comment starts before the delimiter, then the delimiter is commented out; ignore it
        if line_comment_pos is not False and \
          (assign_delim_pos is False or line_comment_pos < assign_delim_pos):
            line = line[0:line_comment_pos]

        # if the delimiter exists (non-commented)
        if assign_delim_pos is not False:
            line = line[0:assign_delim_pos]

        return line.strip()

    def _get_post_delimiter(self, line):
        """
        Returns the trimmed string after any delimiter on a line.
         - If no delimiter is present (or if delimiter is commented out) returns empty string
         - Does NOT remove comments from post delimiter content
        :param line string The line to operate from
        :return string The value after any delimiter
        """
        assign_delim_pos = self._find_assignment_delimiter_position(line)

        # if comment starts before the delimiter, then the delimiter is
        # commented out; no post delim content
        if assign_delim_pos is not False:
            line = line[1+assign_delim_pos:]

        line = line.strip()
        return line

    def _has_valid_variable_name(self, line, line_for_error=None):
        """
        Checks if the line has a variable name and that it's valid
        :param line string The line to check
        :param line_for_error int|null If provided, will add an error
            on invalid variable name characters
        :return boolean Returns true if variable name exists and is valid, false otherwise
        """
        valid_char_set = self.varname_char_set
        scope_char = re.escape(self.scope_delimiter)
        var_name_pattern = re.compile(fr'^\s*(?:[{valid_char_set}]+' + \
                                      fr'(?:{scope_char}[{valid_char_set}]+)*)\s*$')
        var_name_check = self._get_pre_delimiter(line)

        # default to not a valid name
        valid = False
        # check for invalid characters
        match = var_name_pattern.search(var_name_check)
        if match:
            valid = True
        # don't error for empty line
        elif var_name_check != "" and line_for_error is not None:
            self._add_error(line_for_error, "Invalid variable name.")

        return valid

    def _get_variable_name(self, line, line_for_error=None):
        """
        Gets a valid variable name for a line, or false if no valid variable name exists.
        :param line string The line to check
        :param line_for_error int|null If provided, will add an error
            on invalid variable name characters
        :return string|false The variable name, or false if no valid variable name existed
        """
        valid_var = False
        if self._has_valid_variable_name(line, line_for_error):
            valid_var = self._get_pre_delimiter(line)

        return valid_var

    def _process_line(self, line_num, line):
        """
        Process a line into the store values array.
        :param line_num int The line number processing (for use in error reporting)
        :param line string The full line from the file to process
        """
        if self._is_valid_scope_definition(line):
            self._set_scope(line)
        else:
            var_name = self._get_variable_name(line, line_num)
            if var_name is not False:
                adjusted_name = self.current_scope + \
                                ("" if self.current_scope == "" else self.scope_delimiter) + \
                                var_name
                # initialize variable name array if doesn't exist (or if it was a preloaded value)
                if adjusted_name not in self.values or adjusted_name in self.preloaded:
                    self.values[adjusted_name] = []
                    if adjusted_name in self.preloaded:
                        del self.preloaded[adjusted_name]
                self.values[adjusted_name].append(self._get_variable_value(line, line_num))

    def _add_error(self, line, message):
        """
        Store an error for retrieval with errors() function.
        :param line int The line on which the error occured (0 based count)
        :param message string The error message associated with the line
        """
        line += 1   # due to base 0 line indexing
        self._errors.append(f"ConfigFile parse error on line {line}: {message}")

    def errors(self):
        """
        Get a list of errors when attempting to load() the file
        :return array And array of errors; can be empty if no errors were encountered or the
            file has not been loaded yet
        """
        return self._errors

    def get(self, query, default=None):
        """
        Query the config for a scope/variable. Returns the first value or scope on success,
        or 'default' (default: none) if the query was not found.
        :param query string The query string. e.g. "variable", "scope", "scope.variable", etc
        :param default mixed The return value should the query not find anything.
        :return string|ConfigFile|null The matching value from the query, or mDefault if not found
        """
        val = default
        # try to get value match first
        if query in self.values and len(self.values[query]) > 0:
            val = self.values[query][0]
        else:
            # check if this matches any scopes
            scope_char = re.escape(self.scope_delimiter)
            query_str = re.escape(query)
            # must match a scope exactly ( "my.scope" should not match "my.scopeless" )
            scope_pattern = re.compile(fr'^{query_str}{scope_char}(.+)$')

            scope_matches = {}
            for name, value in self.values.items():
                match = scope_pattern.search(name)
                if match and len(match.groups()) == 1:
                    scope_matches[match.group(1)] = value

            if len(scope_matches) > 0:
                val = ConfigFile()
                val.preload(scope_matches)

        return val


    def get_list(self, query):
        """
        Query the config for a variable. Returns all values for the given query as a list.
        If no value for the query exists, returns an empty list.
        :param query string The query string. e.g. "variable", "scope.variable", etc
        :return list A list containing all matching values from the query or empty list if not found
        """
        val = []
        if query in self.values:
            val = self.values[query]
        return val

    def get_all(self):
        """
        Get all name/value pairs that have been parsed from the file.
        :return array An associative array containing name=>value pairs will full scope names.
        """
        return self.values

    def enumerate_scope(self, query=""):
        """
        Query to return all avaialble scopes/variables for a given scope level. An empty
        string (the default) will return top level scopes/variables.
        :param query string A scope level to match, or empty string to query for top level scopes
        :return array An array of available scopes/variables for the given scope level
        """
        scope_values = []
        all_scopes = self.values.keys()
        if query != "":
            query += "."
        for scope in all_scopes:
            if query == "" or scope.find(query) == 0:
                sub_scope = scope[len(query):]
                scope_end = sub_scope.find(".")
                val = sub_scope[0:]
                # Grab only the next level of scope
                if scope_end != -1:
                    val = sub_scope[0:scope_end]
                scope_values.append(val)

        return list(set(scope_values))
