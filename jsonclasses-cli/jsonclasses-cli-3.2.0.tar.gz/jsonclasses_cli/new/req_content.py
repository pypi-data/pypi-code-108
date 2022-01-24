def req_content(include_user: bool, include_admin: bool) -> str:
    nl = '\n'
    return f"""
jsonclasses>=3.2.0,<4.0.0
jsonclasses-pymongo>=3.2.0,<4.0.0
jsonclasses-server>=3.2.0,<4.0.0
thunderlight>=0.1.2,<1.0.0
inflection-plus>=0.1.0,<1.0.0{f'{nl}bcrypt>=3.2.0,<4.0.0' if include_admin or include_user else ''}
    """.strip() + '\n'
