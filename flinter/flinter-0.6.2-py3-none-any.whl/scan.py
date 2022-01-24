
from pathlib import Path

import lizard

from flinter._lizard import FlintExtension
from flinter.nesting_utils import remove_keys_from_nested
from flinter.nesting_utils import nest_data
from flinter.utils import get_all_analysable_files
from flinter.rules import init_languages_specs


def _get_reader(path):
    Reader = lizard.get_reader_for(path)
    if Reader is None:
        raise Exception('No reader available.')

    return Reader


def _load_content(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

        return content

    except UnicodeDecodeError:
        print(f"File {filename} is not encoded in UTF-8")

    return None


def _get_default_rule_sets():
    return init_languages_specs()


def scan_dir(dirname, keep_content=False, rule_sets=None, nest=True):
    if rule_sets is None:
        rule_sets = _get_default_rule_sets()

    files_to_scan = get_all_analysable_files(dirname, rule_sets)

    raw_data_ls = []
    for filename in files_to_scan:
        rules = rule_sets.get_from_fname(filename)
        info = scan_file(filename, rules, keep_content=keep_content,
                         dirname=dirname)
        if info is not None:
            raw_data_ls.append(info)

    if nest:
        return nest_data(raw_data_ls)

    return raw_data_ls


def scan_file(filename, rules=None, keep_content=False, dirname=None):
    Reader = _get_reader(filename)

    if rules is None:
        rules = _get_default_rule_sets().get_from_fname(filename)

    # load content
    content = _load_content(filename)
    if content is None:  # unable to read file
        return None

    # get relative path
    if dirname is not None:
        dirpath = Path(dirname)
        filepath = Path(filename)
        path = filepath.relative_to(dirpath.parent).as_posix()
    else:
        path = filename

    return scan_content(path, content, rules, keep_content=keep_content,
                        Reader=Reader)


def scan_content(path, content, rules, keep_content=False, Reader=None):
    if Reader is None:
        Reader = _get_reader(path)

    ext = FlintExtension(path, rules["syntax"], rules["struct-rules"],
                         rules["regexp-rules"])
    processors = lizard.get_extensions([ext, ext.down_stream])

    context = lizard.FileInfoBuilder(path)
    reader = Reader(context)
    tokens = reader.generate_tokens(content, "", lambda match: match)
    for processor in processors:
        tokens = processor(tokens, reader)

    # TODO: should try be kept? why?
    for _ in reader(tokens, reader):
        pass

    # clean output
    out = ext.struct[0]
    key_names = ['handle']
    if not keep_content:
        key_names.extend(['content', 'clean_content'])
    remove_keys_from_nested(out, key_names)

    return out
