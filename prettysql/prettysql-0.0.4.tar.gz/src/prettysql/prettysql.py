"""Pretty sql."""
import os
import re

import fire

START_WORDS = ['select', 'from', 'join', 'left join', 'right join', 'group', 'with', 'where', 'order', 'having',
               'create', '--']
SPECIAL_WORDS = ['select', 'from', 'group', 'with', 'as', 'on', 'where', 'and', 'between', 'having',
                 'order', 'by', 'then', 'using', 'except', 'numeric', 'partition','INTERVAL']

NEWLINE_WORDS = ['select distinct', 'select']
TWOTABS_WORDS = ['else', 'when', 'end']
NO_NEWLINE_CHARACTERS = [')', '(', '[', ']', "'", 'GROUP BY']
WORD_AS_FUNCS = ['using', 'except']

# SPECIAL_FUNCS = ['date', 'cast', 'nullif']
NEWLINE_CHARACTERS = [' AS (', ' EXCEPT (']
TAB = '    '

SPECIAL_WORDS = SPECIAL_WORDS + START_WORDS + NEWLINE_WORDS + TWOTABS_WORDS


def prettysql(filename=None, filename_out=None):
    """Make sql files pretty."""
    if filename is None and filename_out is None:
        filenames = os.listdir()
        filenames = [v for v in filenames if v.endswith('.sql')]
        for filename in filenames:
            prettysql_file(filename)
    else:
        prettysql_file(filename, filename_out)


def prettysql_file(filename, filename_out=None):
    """Make sql file pretty."""
    if filename_out is None:
        filename_out = filename
    print(f"{filename} -> {filename_out}")
    with open(filename, 'r') as f:
        sql = f.read()
    special_words = [v.upper() for v in SPECIAL_WORDS]
    start_words = [v.upper() for v in START_WORDS]
    # special_funcs = [v.upper() for v in SPECIAL_FUNCS]
    newline_words = [v.upper() for v in NEWLINE_WORDS]
    newline_characters = [v.upper() for v in NEWLINE_CHARACTERS]
    twotabs_words = [v.upper() for v in TWOTABS_WORDS]
    word_as_funcs = [v.upper() for v in WORD_AS_FUNCS]

    sql = sql.replace('--', '\n-- ')
    # sql = sql.replace('(', ' (')
    while '  ' in sql:
        sql = sql.replace('  ', ' ')
    # sql = sql.replace('\n', ' \n ')
    sql_lines = sql.split('\n')
    sql_lines_tmp = []
    for index, sql_line in enumerate(sql_lines):
        if sql_line.startswith('--'):
            sql_lines_tmp += [sql_line]
        elif index > 0 and sql_lines[index - 1] == '-- noqa':
            sql_lines_tmp += [sql_line]
        else:
            sql_line = f' {sql_line} '
            sql_line = sql_line.replace('(', '( ')
            sql_line = sql_line.replace(')', ' )')
            for special_word in special_words:
                pattern = re.compile(f" {special_word} ", re.IGNORECASE)
                sql_line = pattern.sub(f" {special_word} ", sql_line)

            for word_as_func in word_as_funcs:
                pattern = re.compile(f" {word_as_func}\(", re.IGNORECASE)
                sql_line = pattern.sub(f" {word_as_func} (", sql_line)

            for start_word in start_words + twotabs_words:
                if sql_line.endswith(f" {start_word} "):
                    sql_line += '__delete__'

            def upper_re(match):
                return match.group().upper()

            sql_line = re.sub(" [a-zA-Z]+ \(", upper_re, sql_line)
            sql_line = re.sub(" [a-zA-Z]+\(", upper_re, sql_line)

            pattern = re.compile(" \abc \(", re.IGNORECASE)
            sql_line = pattern.sub(" \abc.upper() \(", sql_line)
            for newline_word in newline_words:
                sql_line = sql_line.replace(f" {newline_word} ", f" {newline_word}\n")

            for newline_character in newline_characters:
                sql_line = sql_line.replace(newline_character, f'{newline_character}\n')

            for twotabs_word in twotabs_words:
                sql_line = sql_line.replace(f" {twotabs_word} ", f"\n {twotabs_word} ")

            if not any([v in sql_line for v in NO_NEWLINE_CHARACTERS]):
                sql_line = sql_line.replace(",", ",\n")

            sql_line = sql_line.replace('* EXCEPT', '*\nEXCEPT')
            sql_line = sql_line.replace(' )', ')')
            sql_line = sql_line.replace('( ', '(')
            # sql_line = sql_line.replace(')', ' )')
            while ' ,' in sql_line:
                sql_line = sql_line.replace(' ,', ',')
            sql_line = sql_line.replace(',', ', ')
            sql_lines_tmp += [sql_line]
    sql = '\n'.join(sql_lines_tmp)
    sql = sql.replace('__delete__\n', ' ')
    while '  ' in sql:
        sql = sql.replace('  ', ' ')

    # ToDo: split on ',' only on select - from
    # indent lines
    sql_lines = sql.split('\n')
    sql_lines_tmp = []
    for index, sql_line in enumerate(sql_lines):
        while sql_line.startswith(' '):
            sql_line = sql_line[1:]
        if any([sql_line.startswith(s) for s in twotabs_words]):
            sql_line = TAB + sql_line
        startwith_startword = any([sql_line.startswith(s) for s in start_words])
        if ' AS (' in sql_line:
            startwith_startword = True
        if not startwith_startword:
            sql_line = TAB + sql_line

        if sql_line.split() != []:
            sql_lines_tmp += [sql_line]
    sql_lines = sql_lines_tmp
    sql_lines_tmp = []
    for index, sql_line in enumerate(sql_lines):
        if index < len(sql_lines) - 1 and sql_line.startswith('--'):
            for i in range(4, 0, -1):
                if sql_lines[index + 1].startswith(i * TAB):
                    sql_line = i * TAB + sql_line
                    break
        else:
            pass
        sql_lines_tmp += [sql_line]
    sql = '\n'.join(sql_lines_tmp)

    # indent comments

    sql = sql.replace(f'{TAB}END ', 'END ')
    while ' \n' in sql:
        sql = sql.replace(' \n', '\n')

    with open(filename_out, 'w') as f:
        f.write(sql)


def main():
    """Execute main program."""
    fire.Fire(prettysql)


if __name__ == "__main__":
    main()
