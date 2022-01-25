
from collections import namedtuple, defaultdict
from itertools import combinations
import re
from typing import List
from jinja2 import Template
# https://realpython.com/primer-on-jinja-templating/
from demopy.tools import clean_multiline_str

Relationship = namedtuple('Relationship', ['src', 'dst', 'rel', 'num'])


def parse_rels_from_line(simple_statement:str, line_number:int=1):
    lines = re.sub(r"\]->([^-]+)-\[", r"]->\1\n\1-[", simple_statement).split("\n")
    return [
        eval(re.sub(
            r"(.*)-\[(.*)\]->(.*)", 
            f'Relationship("\\1".strip(), "\\3".strip(), "\\2".strip(), {line_number})', 
            line
        ))
        for line in lines
    ]


def convert_to_puml(simple_statement:str) -> str:
    rels = [
        rel
        for i, l in enumerate(simple_statement.split("\n"))
        for rel in parse_rels_from_line(l, i+1)
    ]
    # print(rels)
    return clean_multiline_str(
        "\n".join([
            header(),
            define_resources_involved_in_rels(rels),
            define_rels(rels),
            define_same_links(rels),
            footer()
        ])
    )


def header() -> str:
    return """
    @startuml
    !theme cerulean
    left to right direction
    
    'skinparam linetype polyline
    'skinparam linetype ortho
    skinparam package<<Layout>> {
        borderColor Transparent
        backgroundColor Transparent
        fontColor Transparent
        stereotypeFontColor Transparent
    }
    """


def footer()->str:
    return "@enduml"

    
def determine_node_repitition(rels:List[Relationship]):
    lines_per_node = defaultdict(set)
    for rel in rels:
        lines_per_node[rel.src].add(rel.num)
        lines_per_node[rel.dst].add(rel.num)
    return lines_per_node


def define_rels(rels:List[Relationship]) -> str:
    t = Template(
    """
    {% for rel in rels %}
    {{ rel.src * rel.num }} --> {{ rel.dst * rel.num }} : {{ rel.rel }}
    {% endfor %}
    """
    )
    return t.render(rels=rels)


def define_same_links(rels:List[Relationship]) -> str:
    lines_per_node = determine_node_repitition(rels)
    combinations_per_node = {k: list(combinations(v, 2)) for k, v in lines_per_node.items()}
    t = Template(
    """
    {% for (node, combinations) in combinations_per_node.items() %}
    {% for (left, right) in combinations %}
    {{ node * left }} ..right.. {{ node * right }}: Same
    {% endfor %}
    {% endfor %}
    """
    )
    return t.render(combinations_per_node=combinations_per_node)

def define_resources_involved_in_rels(rels:List[Relationship]):
    lines_per_node = determine_node_repitition(rels)
    t = Template(
    """
    {% for node, lines in lines_per_node.items() %}
    package {{node}}'s <<Layout>> {
        {% for line in lines %}
        rectangle {{ node * line }} 
        {% endfor %}
    }
    {% endfor %}
    """
    )
    return t.render(lines_per_node=lines_per_node)


if __name__ == "__main__":
    print(convert_to_puml("a-[knows]->b-[knows]->c"))
    print(convert_to_puml("a -[knows]->b-[knows]->c\n   a     -[owes]->c"))