
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


def convert_to_puml(simple_statement:str, resources:dict={}) -> str:
    simple_statement = simple_statement.replace("\\n", "\n")
    rels = [
        rel
        for i, l in enumerate(simple_statement.split("\n"))
        for rel in parse_rels_from_line(l, i+1)
    ]
    # print(rels)
    return clean_multiline_str(
        "\n".join([
            header(),
            define_resources_involved_in_rels(rels, resources),
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
    
    ' https://plantuml.com/stdlib
    ' https://github.com/awslabs/aws-icons-for-plantuml#basic-usage
    
    !define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v11.1/dist
    !includeurl AWSPuml/AWSCommon.puml
    !includeurl AWSPuml/AWSSimplified.puml
    !includeurl AWSPuml/ApplicationIntegration/APIGateway.puml
    !includeurl AWSPuml/Compute/Lambda.puml
    !includeurl AWSPuml/Database/DynamoDB.puml
    !includeurl AWSPuml/General/Users.puml
    !includeurl AWSPuml/SecurityIdentityCompliance/Cognito.puml
    !includeurl AWSPuml/Storage/SimpleStorageService.puml

    ' https://plantuml.com/style-evolution
    'skinparam linetype polyline
    'skinparam linetype ortho
    skinparam package<<Layout>> {
        BorderColor Transparent
        BackgroundColor Transparent
        FontColor Transparent
        TitleFontColor Transparent
        StereotypeFontColor Transparent
    }
    """
# TODO ... support bidirectional arrows ...

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
    {{rel.src}}{{rel.num}} --> {{rel.dst}}{{rel.num}} : {{rel.rel}}
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
    {{node}}{{left}} ..right.. {{node}}{{right}}: Same
    {% endfor %}
    {% endfor %}
    """
    )
    return t.render(combinations_per_node=combinations_per_node)


def define_resource(id, line, resources):
    awsdef = {x["id"]: x for x in resources.get("aws", [])}.get(id)
    if awsdef:
        awsdef["tooltip"] = awsdef["title"] if not awsdef.get("tooltip") else awsdef["tooltip"]
        awsdef["title"] = (
            awsdef["title"]
            # Use title if link not defined or already expanded into link ...
            if (not awsdef.get("link") or awsdef.get("title").startswith("[[")) 
            else "[[{link}{{{tooltip}}} {title}]]".format(**awsdef)
        )
        #  { "id": "sources", "type": "Users", "title": "Events", "note": "millions of users" },
        return '{type}({id}{line}, "{title}", "{note}")'.format(**awsdef, line=line)
    return f"rectangle {id}{line}"


def define_resources_involved_in_rels(rels:List[Relationship], resources:dict):
    lines_per_node = determine_node_repitition(rels)
    t = Template(
    """
    {% for node, lines in lines_per_node.items() %}
    package " " as {{node}} <<Layout>> {
        {% for line in lines %}
         {{ define_resource(node, line, resources) }} 
        {% endfor %}
    }
    {% endfor %}
    """
    )
    # https://stackoverflow.com/questions/6036082/call-a-python-function-from-jinja2
    t.globals["define_resource"] = define_resource
    t.globals["resources"] = resources
    return t.render(lines_per_node=lines_per_node)


if __name__ == "__main__":
    print(convert_to_puml("a-[knows]->b-[knows]->c"))
    print(convert_to_puml("a -[knows]->b-[knows]->c\n   a     -[owes]->c"))
    print(convert_to_puml(
        """
        """, 
    ))