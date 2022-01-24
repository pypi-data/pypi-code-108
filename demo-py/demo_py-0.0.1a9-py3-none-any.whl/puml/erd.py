from typing import get_type_hints, _GenericAlias, List, Optional


def delimit_camel_case(s):
    # https://stackoverflow.com/questions/5020906/python-convert-camel-case-to-space-delimited-using-regex-and-taking-acronyms-in
    return ''.join(' ' + c if c.isupper() and s[max(0, i-1)].islower() else c for i, c in enumerate(s))

def clean_type(t):
    # https://www.delftstack.com/howto/python/python-get-class-name/
    t = str(t) if isinstance(t, _GenericAlias) else t.__name__
    return t.replace("typing.List", "").replace("__main__.", "").replace("typing.Optional", "")

def convert_class_to_puml(cls):
    name = cls.__name__
    private_fields, public_fields = convert_fields_to_puml(cls)
    private_fields, public_fields = "\n".join(private_fields), "\n".join(public_fields)
    return (f"""
    class "{delimit_camel_case(name)}" as {name} {{
        {private_fields}
        {public_fields}
    }}
    """)

def convert_fields_to_puml(cls):
    # https://docs.python.org/3/library/typing.html#introspection-helpers
    fields = get_type_hints(cls)
    private_fields = [
        f"- {clean_type(v)} {k}"
        for k, v in fields.items()
        if k.startswith("_")
    ]
    public_fields = [
        f"+ {clean_type(v)} {k}"
        for k, v in fields.items()
        if not k.startswith("_")
    ]
    return private_fields, public_fields


def base_type(cls):
    return clean_type(cls).replace("[", "").replace("]", "")

def parent_class(cls):
    return cls.__mro__[1:][0]

def convert_relationships_to_puml(cls, other_custom_resources):
    # https://docs.python.org/3/library/typing.html#introspection-helpers
    relationships = []
    fields = get_type_hints(cls)
    for k, v in fields.items():
        # print(k, v, clean_type(cls), clean_type(v), base_type(v))
        if base_type(v) in other_custom_resources:
            if clean_type(v) == f'[{base_type(v)}]':
                rel = f"{base_type(cls)} --{{ {base_type(v)}"
            else:
                rel = f"{base_type(cls)} -- {base_type(v)}"
        else:
            continue 
        relationships = relationships + [rel]
    if base_type(parent_class(cls)) in other_custom_resources:
        relationships = relationships + [
            f'{base_type(cls)} --o {base_type(parent_class(cls))}'
        ]
    return "\n".join(relationships)


def header():
    return """
@startuml
' skinparam linetype ortho
  skinparam packageStyle rectangle
  skinparam shadowing false
  skinparam class {
    BackgroundColor White
    BorderColor Black
    ArrowColor Black
  }
  hide circle
"""


def footer():
    return "@enduml"


#   class "User" as User1 {
#     - int id
#     - int age
#     - string name
#     + ([role]) roles()
#     + ([user_role]) user_roles()
#   }
#   class Role {
#     - int id
#     - string name
#   }
#   class "UserRole" as User1Role {
#     - int id
#     - int user_id
#     - int role_id
#   }
