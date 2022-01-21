import json
import logging
import os
import subprocess
import sys
import uuid
import re

from parsec import BasicState, ParsecError

from .exercises.markdown import parse

id_set = set()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def search_author(author_dict, username):
    for key in author_dict:
        names = author_dict[key]
        if username in names:
            return key
    return username


def user_name(md_file, author_dict):
    ret = subprocess.Popen([
        "git", "log", md_file
    ], stdout=subprocess.PIPE)
    lines = list(map(lambda l: l.decode(), ret.stdout.readlines()))
    author_lines = []
    for line in lines:
        if line.startswith('Author'):
            author_lines.append(line.split(' ')[1])
    author_nick_name = author_lines[-1]
    return search_author(author_dict, author_nick_name)


def load_json(p):
    with open(p, 'r', encoding="utf-8") as f:
        try:
            return json.loads(f.read())
        except UnicodeDecodeError:
            logger.info("json 文件 [{p}] 编码错误，请确保其内容保存为 utf-8 或 base64 后的 ascii 格式。")


def dump_json(p, j, exist_ok=False, override=False):
    if os.path.exists(p):
        if exist_ok:
            if not override:
                return
        else:
            logger.error(f"{p} already exist")
            sys.exit(0)

    with open(p, 'w+', encoding="utf8") as f:
        f.write(json.dumps(j, indent=2, ensure_ascii=False))


def ensure_config(path):
    config_path = os.path.join(path, "config.json")
    if not os.path.exists(config_path):
        node = {"keywords": [],
                "keywords_must": [],
                "keywords_forbid": []}
        dump_json(config_path, node, exist_ok=True, override=False)
        return node
    else:
        return load_json(config_path)


def parse_no_name(d):
    p = r'(\d+)\.(.*)'
    m = re.search(p, d)

    try:
        no = int(m.group(1))
        dir_name = m.group(2)
    except:
        sys.exit(0)

    return no, dir_name


def check_export(base, cfg):
    flag = False
    exports = []
    for export in cfg.get('export', []):
        ecfg_path = os.path.join(base, export)
        if os.path.exists(ecfg_path):
            exports.append(export)
        else:
            flag = True
    if flag:
        cfg["export"] = exports
    return flag


class TreeWalker:
    def __init__(
            self, root,
            tree_name,
            title=None,
            log=None,
            authors=None,
            enable_notebook=None,
            ignore_keywords=False
    ):
        self.ignore_keywords = ignore_keywords
        self.authors = authors if authors else {}
        self.enable_notebook = enable_notebook
        self.name = tree_name
        self.root = root
        self.title = tree_name if title is None else title
        self.tree = {}
        self.logger = logger if log is None else log

    def walk(self):
        root = self.load_root()
        root_node = {
            "node_id": root["node_id"],
            "keywords": root.get("keywords", []),
            "children": [],
            "keywords_must": root.get("keywords_must", []),
            "keywords_forbid": root.get("keywords_forbid", [])
        }
        self.tree[root["tree_name"]] = root_node
        self.load_levels(root_node)
        self.load_chapters(self.root, root_node)
        for index, level in enumerate(root_node["children"]):
            level_title = list(level.keys())[0]
            level_node = list(level.values())[0]
            level_path = os.path.join(self.root, f"{index + 1}.{level_title}")
            self.load_chapters(level_path, level_node)
            for index, chapter in enumerate(level_node["children"]):
                chapter_title = list(chapter.keys())[0]
                chapter_node = list(chapter.values())[0]
                chapter_path = os.path.join(
                    level_path, f"{index + 1}.{chapter_title}")
                self.load_sections(chapter_path, chapter_node)
                for index, section_node in enumerate(chapter_node["children"]):
                    section_title = list(section_node.keys())[0]
                    full_path = os.path.join(
                        chapter_path, f"{index + 1}.{section_title}")
                    if os.path.isdir(full_path):
                        self.check_section_keywords(full_path)
                        self.ensure_exercises(full_path)

        tree_path = os.path.join(self.root, "tree.json")
        dump_json(tree_path, self.tree, exist_ok=True, override=True)
        return self.tree

    def sort_dir_list(self, dirs):
        result = [self.extract_node_env(dir) for dir in dirs]
        result.sort(key=lambda item: item[0])
        return result

    def load_levels(self, root_node):
        levels = []
        for level in os.listdir(self.root):
            if not os.path.isdir(level):
                continue
            level_path = os.path.join(self.root, level)
            num, config = self.load_level_node(level_path)
            levels.append((num, config))

        levels = self.resort_children(self.root, levels)
        root_node["children"] = [item[1] for item in levels]
        return root_node

    def load_level_node(self, level_path):
        config = self.ensure_level_config(level_path)
        num, name = self.extract_node_env(level_path)

        result = {
            name: {
                "node_id": config["node_id"],
                "keywords": config["keywords"],
                "children": [],
                "keywords_must": config.get("keywords_must", []),
                "keywords_forbid": config.get("keywords_forbid", [])
            }
        }

        return num, result

    def load_chapters(self, base, level_node):
        chapters = []
        for name in os.listdir(base):
            full_name = os.path.join(base, name)
            if os.path.isdir(full_name):
                num, chapter = self.load_chapter_node(full_name)
                chapters.append((num, chapter))

        chapters = self.resort_children(base, chapters)
        level_node["children"] = [item[1] for item in chapters]
        return level_node

    def load_sections(self, base, chapter_node):
        sections = []
        for name in os.listdir(base):
            full_name = os.path.join(base, name)
            if os.path.isdir(full_name):
                num, section = self.load_section_node(full_name)
                sections.append((num, section))

        sections = self.resort_children(base, sections)
        chapter_node["children"] = [item[1] for item in sections]
        return chapter_node

    def resort_children(self, base, children):
        children.sort(key=lambda item: item[0])
        for index, [number, element] in enumerate(children):
            title = list(element.keys())[0]
            origin = os.path.join(base, f"{number}.{title}")
            posted = os.path.join(base, f"{index + 1}.{title}")
            if origin != posted:
                self.logger.info(f"rename [{origin}] to [{posted}]")
            os.rename(origin, posted)
        return children

    def ensure_chapters(self):
        for subdir in os.listdir(self.root):
            self.ensure_level_config(subdir)

    def load_root(self):
        config_path = os.path.join(self.root, "config.json")
        if not os.path.exists(config_path):
            config = {
                "tree_name": self.name,
                "keywords": [],
                "node_id": self.gen_node_id(),
                "keywords_must": [],
                "keywords_forbid": []
            }
            dump_json(config_path, config, exist_ok=True, override=True)
        else:
            config = load_json(config_path)
            flag, result = self.ensure_node_id(config)
            if flag:
                dump_json(config_path, result, exist_ok=True, override=True)

        return config

    def ensure_level_config(self, path):
        config_path = os.path.join(path, "config.json")
        if not os.path.exists(config_path):
            config = {
                "node_id": self.gen_node_id()
            }
            dump_json(config_path, config, exist_ok=True, override=True)
        else:
            config = load_json(config_path)
            flag, result = self.ensure_node_id(config)
            if flag:
                dump_json(config_path, config, exist_ok=True, override=True)
        return config

    def ensure_chapter_config(self, path):
        config_path = os.path.join(path, "config.json")
        if not os.path.exists(config_path):
            config = {
                "node_id": self.gen_node_id(),
                "keywords": [],
                "keywords_must": [],
                "keywords_forbid": []
            }
            dump_json(config_path, config, exist_ok=True, override=True)
        else:
            config = load_json(config_path)
            flag, result = self.ensure_node_id(config)
            if flag:
                dump_json(config_path, config, exist_ok=True, override=True)
        return config

    def ensure_section_config(self, path):
        config_path = os.path.join(path, "config.json")
        if not os.path.exists(config_path):
            config = {
                "node_id": self.gen_node_id(),
                "keywords": [],
                "children": [],
                "export": [],
                "keywords_must": [],
                "keywords_forbid": []
            }
            dump_json(config_path, config, exist_ok=True, override=True)
        else:
            config = load_json(config_path)
            flag, result = self.ensure_node_id(config)
            if flag:
                dump_json(config_path, result, exist_ok=True, override=True)
        return config

    def ensure_node_id(self, config):
        flag = False
        if "node_id" not in config or \
                not config["node_id"].startswith(f"{self.name}-") or \
                config["node_id"] in id_set:
            new_id = self.gen_node_id()
            id_set.add(new_id)
            config["node_id"] = new_id
            flag = True

        for child in config.get("children", []):
            child_node = list(child.values())[0]
            f, _ = self.ensure_node_id(child_node)
            flag = flag or f

        return flag, config

    def gen_node_id(self):
        return f"{self.name}-{uuid.uuid4().hex}"

    def extract_node_env(self, path):
        try:
            _, dir = os.path.split(path)
            self.logger.info(path)
            number, title = dir.split(".", 1)
            return int(number), title
        except Exception as error:
            self.logger.error(f"目录 [{path}] 解析失败，结构不合法，可能是缺少序号")
            # sys.exit(1)
            raise error

    def load_chapter_node(self, full_name):
        config = self.ensure_chapter_config(full_name)
        num, name = self.extract_node_env(full_name)
        result = {
            name: {
                "node_id": config["node_id"],
                "keywords": config["keywords"],
                "children": [],
                "keywords_must": config.get("keywords_must", []),
                "keywords_forbid": config.get("keywords_forbid", [])
            }
        }
        return num, result

    def load_section_node(self, full_name):
        config = self.ensure_section_config(full_name)
        num, name = self.extract_node_env(full_name)
        result = {
            name: {
                "node_id": config["node_id"],
                "keywords": config.get("keywords", []),
                "children": config.get("children", []),
                "keywords_must": config.get("keywords_must", []),
                "keywords_forbid": config.get("keywords_forbid", [])
            }
        }
        # if "children" in config:
        #     result["children"] = config["children"]
        return num, result

    def ensure_exercises(self, section_path):
        config = self.ensure_section_config(section_path)
        flag = False
        for e in os.listdir(section_path):
            base, ext = os.path.splitext(e)
            _, source = os.path.split(e)
            if ext != ".md":
                continue
            mfile = base + ".json"
            meta_path = os.path.join(section_path, mfile)
            md_file = os.path.join(section_path, e)
            self.ensure_exercises_meta(meta_path, source, md_file)
            export = config.get("export", [])
            if mfile not in export and self.name != "algorithm":
                export.append(mfile)
                flag = True
                config["export"] = export
            with open(md_file, "r", encoding="utf-8") as efile:
                try:
                    data = efile.read()
                except UnicodeDecodeError:
                    logger.error(f"习题 [{md_file}] 编码错误，请确保其保存为 utf-8 编码")
                    sys.exit(1)
                state = BasicState(data)
                try:
                    doc = parse(state)
                except ParsecError as err:
                    index = state.index
                    context = state.data[index - 15:index + 15]
                    logger.error(f"习题 [{md_file}] 解析失败，在位置 {index} [{context}] 附近有格式: [{err}]")

        if flag:
            dump_json(os.path.join(section_path, "config.json"),
                      config, True, True)

        for e in config.get("export", []):
            full_name = os.path.join(section_path, e)
            exercise = load_json(full_name)
            if "exercise_id" not in exercise or exercise.get("exercise_id") in id_set:
                eid = uuid.uuid4().hex
                exercise["exercise_id"] = eid
                dump_json(full_name, exercise, True, True)
            else:
                id_set.add(exercise["exercise_id"])

    def ensure_exercises_meta(self, meta_path, source, md_file):
        _, mfile = os.path.split(meta_path)
        meta = None
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                content = f.read()
            if content:
                meta = json.loads(content)
                if "exercise_id" not in meta:
                    meta["exercise_id"] = uuid.uuid4().hex
                if "notebook_enable" not in meta:
                    meta["notebook_enable"] = self.default_notebook()
                if "source" not in meta:
                    meta["source"] = source
                if "author" not in meta:
                    meta["author"] = user_name(md_file, self.authors)
                if "type" not in meta:
                    meta["type"] = "code_options"

        if meta is None:
            meta = {
                "type": "code_options",
                "author": user_name(md_file, self.authors),
                "source": source,
                "notebook_enable": self.default_notebook(),
                "exercise_id": uuid.uuid4().hex
            }
        dump_json(meta_path, meta, True, True)

    def default_notebook(self):
        if self.enable_notebook is not None:
            return self.enable_notebook
        if self.name in ["python", "java", "c"]:
            return True
        else:
            return False

    def check_section_keywords(self, full_path):
        if self.ignore_keywords:
            return
        config = self.ensure_section_config(full_path)
        if not config.get("keywords", []):
            self.logger.error(f"节点 [{full_path}] 的关键字为空，请修改配置文件写入关键字")
            sys.exit(1)
