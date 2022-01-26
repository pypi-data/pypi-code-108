import re

from .actions import ACTION_MAP

class RooProcConfigParser(object):
    
    kActions      = tuple(ACTION_MAP)
    
    def __init__(self):
        self.action_list = []
    
    @staticmethod
    def get_start_tag(text:str):
        result = re.search(r"^\s*<(\w+)>", text)
        if not result:
            return None
        else:
            return "<"+result.group(1)+">"
        
    @staticmethod
    def get_end_tag(text:str):
        result = re.search(r"</(\w+)>\s*$", text)
        if not result:
            return None
        else:
            return "</"+result.group(1)+">"
        
    @staticmethod
    def parse_text(text:str):
        lines = text.splitlines(True)
        # remove comments
        lines = [l.split("#")[0] for l in lines]
        # remove blank lines
        lines = filter(lambda x: not re.match(r'^\s*$', x), lines)
        action_list = []
        action_name = None
        expression  = ""
        block_flag  = False
        for l in lines:
            if action_name is None:
                tokens = [t.strip() for t in l.strip().split()]
                # remove empty tokens
                tokens = [t for t in tokens if t]
                if not tokens:
                    continue
                action_name = tokens[0].upper()
                if action_name not in RooProcConfigParser.kActions:
                    raise RuntimeError(f"unknown action `{action_name}`")
                if (len(tokens) == 1):
                    continue
                else:
                    expression = ' '.join(tokens[1:])
            else:
                start_tag = RooProcConfigParser.get_start_tag(l)
                end_tag = RooProcConfigParser.get_end_tag(l)
                if start_tag:
                    if block_flag:
                        raise RuntimeError("missing end-tag or multiple start-tags detected")
                    block_flag = True
                    l = l.split(start_tag)[1]
                if end_tag:
                    if not block_flag:
                        raise RuntimeError("missing start-tag or multiple end-tags detected")
                    block_flag = False
                    l = l.split(end_tag)[0]
                expression += l
            if block_flag:
                continue
            else:
                expression = expression.strip()
                action = RooProcConfigParser.create_action(action_name, expression)
                action_list.append(action)
                action_name = None
                expression  = ""
        if block_flag:
            raise RuntimeError("unterminated start-tag detected")
        return action_list
    
    @staticmethod
    def parse_file(path:str):
        with open(path, "r") as f:
            text = f.read()
        return RooProcConfigParser.parse_text(text)
    
    @staticmethod
    def create_action(action_name:str, expression:str):
        cls = ACTION_MAP.get(action_name, None)
        if cls is None:
            raise RuntimeError(f"unknown action `{action_name}`")
        action = cls.parse(expression)
        return action