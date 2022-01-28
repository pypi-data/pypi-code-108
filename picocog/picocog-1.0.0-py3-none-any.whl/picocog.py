# Copyright 2021, Felipe Michels Fontoura
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# This code is based on the Java version of picocog by Chris Ainsley.
# The original library is also licensed under Apache License 2.0.

import sys

if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO

SEP = "\n"
DI = "    "

class IndentedLine:
    def __init__(self, line, indent):
        self._line = line
        self._indent = indent

    def get_line(self):
        return self._line

    def get_indent(self):
        return self._indent

    def __repr__(self):
        return self._indent + ":" + self._line

class PicoWriter:
    def __init__(self, indent_text = DI, initial_indent = 0):
        self._indents = 0 if initial_indent < 0 else initial_indent
        self._num_lines = 0
        self._generate_if_empty = True
        self._generate = True
        self._normalize_adjacent_blank_rows = False
        self._is_dirty = False
        self._rows = [] # Used for aligning columns in the multi string writeln method.
        self._content = []
        self._sb = StringIO()
        self._ident_chars = DI if indent_text is None else indent_text

    def indent_right(self):
        """
        Increases the indentation level of following lines.

        @return This object.
        """
        self._flush_rows()
        self._indents += 1
        return self

    def indent_left(self):
        """
        Decreases the indentation level of following lines.

        @return This object.
        """
        if self._indents <= 0:
            raise ValueError("Local indent cannot be less than zero")
        self._flush_rows()
        self._indents -= 1
        return self

    def writeln(self, arg):
        """
        Writes a line using the current indentation.

        If the parameter is another PicoWriter, this method appends all its lines to this one.

        It the parameter is a list, this method appends to the current sequence of column-aligned lines.

        @param string A string, list of PicoWriter.
        @return This object.
        """
        if isinstance(arg, PicoWriter):
            if self._sb.tell() > 0:
                self._flush()
                self._num_lines += 1

            self._adjust_indents(arg, self._indents, self._ident_chars)

            self._content.append(arg)
            self._num_lines += 1
        elif isinstance(arg, list):
            self._rows.append(arg)
            self._is_dirty = True
            self._num_lines += 1
        else:
            self._num_lines += 1
            self._sb.write(arg)
            self._flush()

        return self

    def writeln_r(self, string):
        """
        Writes a line and increases the indentation level of following lines.

        @param string The string to write.
        @return This object.
        """
        self.writeln(string)
        self.indent_right()
        return self

    def writeln_l(self, string):
        """
        Decreases the indentation level of following lines and writes a line. 

        @param string The string to write.
        @return This object.
        """
        self._flush_rows()
        self.indent_left()
        self.writeln(string)
        return self

    def writeln_lr(self, string):
        """
        Decreases the indentation level, writes a line and increases the identation level back again.

        @param string The string to write.
        @return This object.
        """
        self._flush_rows()
        self.indent_left()
        self.writeln(string)
        self.indent_right()
        return self

    def write(self, string):
        """
        Appends text to the last line.

        @param string The string to write.
        @return This object.
        """
        self._num_lines += 1
        self._is_dirty = True
        self._sb.write(string)
        return self

    def create_deferred_writer(self):
        """
        Creates a writer at the current position of this writer.

        @return The deferred writer.
        """
        if self._sb.tell() > 0:
            self._flush()
            self._num_lines += 1

        inner = PicoWriter(self._ident_chars, self._indents)
        self._content.append(inner)
        self._num_lines += 1

        return inner

    def create_deferred_indented_writer(self, start_line, end_line):
        """
        Writes a line, increases the indentation level and creates a deferred writer. Then decreases the indentation level back again and writes another line.

        @param start_line The first line to write.
        @param end_line The last line to write.
        @return The deferred writer.
        """
        self.writeln(start_line)
        self.indent_right()
        ggg = self.create_deferred_writer()
        self.indent_left()
        self.writeln(end_line)
        self._is_dirty = True
        self._num_lines += 2
        return ggg

    def is_empty(self):
        return self._num_lines == 0

    def is_method_body_empty(self):
        return len(self._content) == 0 and self._sb.tell() == 0

    def is_generate_if_empty(self):
        return self._generate_if_empty

    def set_generate_if_empty(self, generate_if_empty):
        self._generate_if_empty = generate_if_empty

    def is_generate(self):
        return self._generate

    def set_generate(self, generate):
        self._generate = generate

    def set_normalize_adjacent_blank_rows(self, normalize_adjacent_blank_rows):
        self._normalize_adjacent_blank_rows = normalize_adjacent_blank_rows

    def to_string(self, indent_base = 0):
        sb = StringIO()
        self._render(sb, indent_base, self._normalize_adjacent_blank_rows, False)
        return sb.getvalue()
    
    def __str__(self):
        return self.to_string()

    def _adjust_indents(self, inner, indents, ic):
        if inner is not None:
            for item in inner._content:
                if isinstance(item, PicoWriter):
                    self._adjust_indents(item, indents, ic)
                elif isinstance(item, IndentedLine):
                    item._indent = item._indent + indents
            inner._ident_chars = ic

    def _write_indented_line(self, sb, indent_base, indent_text, line):
        sb.write(indent_text * indent_base)
        sb.write(line)
        sb.write(SEP)

    def _render(self, sb, indent_base, normalize_adjacent_blank_rows, last_row_was_blank):
        if self._is_dirty:
            self._flush()

        if (not self.is_generate()) or ((not self.is_generate_if_empty()) and self.is_method_body_empty()):
            return last_row_was_blank

        for item in self._content:
            if isinstance(item, IndentedLine):
                line_text = item.get_line()
                indent_level_here = indent_base + item.get_indent()
                this_row_is_blank = (len(line_text) == 0)

                if normalize_adjacent_blank_rows and last_row_was_blank and this_row_is_blank:
                    # Don't write the line if we already had a blank line
                    pass
                else:
                    self._write_indented_line(sb, indent_level_here, self._ident_chars, line_text)

                last_row_was_blank = this_row_is_blank
            elif isinstance(item, PicoWriter):
                last_row_was_blank = item._render(sb, indent_base, normalize_adjacent_blank_rows, last_row_was_blank)
            else:
                sb.write(str(item))

        return last_row_was_blank

    def _flush(self):
        self._flush_rows()
        self._content.append(IndentedLine(self._sb.getvalue(), self._indents))
        self._sb.seek(0)
        self._sb.truncate()
        self._is_dirty = False

    def _flush_rows(self):
        if len(self._rows) > 0:
            max_width = []
            for columns in self._rows:
                num_columns = len(columns)
                for i in range(0, num_columns):
                    current_column_string_value = columns[i]
                    current_column_string_value_length = 0 if current_column_string_value is None else len(current_column_string_value)
                    if len(max_width) < i + 1:
                        max_width.append(current_column_string_value_length)
                    else:
                        if max_width[i] < current_column_string_value_length:
                            max_width[i] = current_column_string_value_length

            row_s_b = StringIO()

            for columns in self._rows:
                num_columns = len(columns)
                for i in range(0, num_columns):
                    current_column_string_value = columns[i]
                    current_item_width = 0 if current_column_string_value is None else len(current_column_string_value)
                    max_width1 = max_width[i]
                    row_s_b.write("" if current_column_string_value is None else current_column_string_value)

                    if current_item_width < max_width1:
                        row_s_b.write(" " * (max_width1 - current_item_width)) # right pad
                self._content.append(IndentedLine(row_s_b.getvalue(), self._indents))
                row_s_b.seek(0)
                row_s_b.truncate()
            self._rows.clear()
