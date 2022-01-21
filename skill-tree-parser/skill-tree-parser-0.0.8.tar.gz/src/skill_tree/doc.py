import os
from sys import version
from .tree import load_json, dump_json


def simple_list_md_load(p):
    with open(p, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        result = []
        for line in lines:
            item = line.strip('\n')
            if item.startswith('* '):
                item = item[2:]
            result.append(item)
        return result


class DocWalker():

    def __init__(self, root) -> None:
        self.root = root

    def walk(self):
        root = self.root
        root_config_path = os.path.join(root, 'config.json')
        root_config = load_json(root_config_path)
        doc_path = os.path.join(root, 'doc.json')
        versions = []
        for version_dir in root_config['versions']:
            version_full_dir = os.path.join(root, version_dir)
            version_config_path = os.path.join(version_full_dir, 'config.json')
            if os.path.exists(version_config_path):
                version_config = load_json(version_config_path)

                for benchmark in version_config['benchmarks']:
                    username = benchmark['user_name']
                    benchmark['askme'] = f'https://ask.csdn.net/new?expertName={username}'

                asserts_path = os.path.join(
                    version_full_dir,
                    version_config['asserts']
                )
                version_config['asserts'] = load_json(asserts_path)

                bug_fixes_path = os.path.join(
                    version_full_dir,
                    version_config['bugfixes']
                )
                version_config['bugfixes'] = simple_list_md_load(
                    bug_fixes_path)

                features_path = os.path.join(
                    version_full_dir,
                    version_config['features']
                )

                parts = version_full_dir.split("/")
                version_config['version'] = parts[len(parts)-1]
                version_config['features'] = simple_list_md_load(features_path)
                versions.append(version_config)

        root_config['versions'] = versions
        dump_json(doc_path, root_config, True, True)
