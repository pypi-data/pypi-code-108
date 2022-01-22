import copy
import glob
import re

from enum import Enum
from pathlib import Path
from typing import Tuple, Optional, List, Union, Dict


class LineTypeRegex(str, Enum):

    COMMENT = r'^//.*'
    EMPTY_LINE = r'^\n$'
    KEY_LINE = r'(?P<key>^\".*\")\s?=\s?(?P<value>\".*\";$)'


def find_lang_folders(path: str, main_lang='en') -> Tuple[Path, Optional[List[Path]]]:
    lang_folders = glob.glob(path + '/**/*.lproj', recursive=True)
    main_folder_idx = [i for i, s in enumerate(lang_folders) if s.endswith(main_lang + '.lproj')]
    if len(main_folder_idx) > 1:
        raise ValueError(f'There are {len(main_folder_idx)} folders with {main_lang} lang')
    if len(main_folder_idx) < 1:
        raise ValueError(f'There are no folders with {main_lang} lang')

    main_folder = Path(lang_folders.pop(main_folder_idx[0]))
    other_folders = [Path(folder) for folder in lang_folders]

    return main_folder, other_folders


def parse_localizable_file(path: Path) -> Tuple[List[str], Dict[str, str]]:
    result_meta: List[str] = []
    result_strings: Dict[str, str] = {}
    with open(path, 'rt') as localizable_file:
        lines = localizable_file.readlines()
        for i, line in enumerate(lines):
            if result_line := re.search(LineTypeRegex.COMMENT.value, line):
                result_meta.append(result_line.group())
            elif result_line := re.search(LineTypeRegex.EMPTY_LINE.value, line):
                result_meta.append(result_line.group())
            elif result_line := re.search(LineTypeRegex.KEY_LINE.value, line):
                key = result_line.group('key')
                value = result_line.group('value')
                result_meta.append(key)
                result_strings[key] = value
            else:
                print(f'{path.absolute()}:{i + 1}:1: error: String format error.')
                exit(0)

    return result_meta, result_strings


def compare(main_strings: Dict[str, str], other_strings: Dict[str, str]) -> Tuple[bool, Dict[str, str]]:
    new_other_strings = copy.deepcopy(other_strings)
    dirty_flag = False
    # добавим недостающие ключи
    for key in main_strings.keys():
        if key not in new_other_strings:
            new_other_strings[key] = '"";'
            dirty_flag = True

    # уберем ключи, которых нет в главном языке
    for key in list(new_other_strings.keys()):
        if key not in main_strings:
            del new_other_strings[key]
            dirty_flag = True

    return dirty_flag, new_other_strings


def update_lang_file(meta: List[str], strings: Dict[str, str], path: Path):
    with open(path, 'w') as lang_file:
        for i, line in enumerate(meta):
            if line in strings:
                lang_file.write(' = '.join([line, strings[line]]))
                # кидать варнинг если нет перевода
                if strings[line] == '"";':
                    lang = path.parent.name.split('.')[0]
                    print(f'{path.absolute()}:{i + 1}:{len(line) + 4}: '
                          f'warning: Translation for key {line} in language \"{lang}\" not found.')
                lang_file.write('\n')
            else:
                lang_file.write(line)
                if line != '\n':
                    lang_file.write('\n')


def check_translations(meta: List[str], strings: Dict[str, str], path: Path):
    for i, line in enumerate(meta):
        if line in strings:
            # кидать варнинг если нет перевода
            if strings[line] == '"";':
                lang = path.parent.name.split('.')[0]
                print(f'{path.absolute()}:{i + 1}:{len(line) + 4}: '
                      f'warning: Translation for key {line} in language \"{lang}\" not found.')


def actualize_languages(path: str, main_lang='en'):
    main_folder, other_folders = find_lang_folders(path=path, main_lang='en')

    localizable_paths = list(main_folder.glob('*'))
    localizable_names = [path.name for path in localizable_paths if path.name.endswith('.strings')]

    for localizable_name in localizable_names:
        main_lang_meta, main_lang_strings = parse_localizable_file(main_folder / localizable_name)
        check_translations(main_lang_meta, main_lang_strings, main_folder / localizable_name)
        for lang_folder in other_folders:
            other_localizable_path = lang_folder / localizable_name
            if other_localizable_path.is_file():
                meta_lang_strings, lang_strings = parse_localizable_file(other_localizable_path)
                dirty, new_lang_strings = compare(main_lang_strings, lang_strings)
                if main_lang_meta != meta_lang_strings:
                    dirty = True
            else:
                new_lang_strings = {key: '"";' for key, value in main_lang_strings.items()}
                dirty = True
            if dirty:
                update_lang_file(main_lang_meta, new_lang_strings, lang_folder / localizable_name)
            else:
                check_translations(main_lang_meta, new_lang_strings, lang_folder / localizable_name)
