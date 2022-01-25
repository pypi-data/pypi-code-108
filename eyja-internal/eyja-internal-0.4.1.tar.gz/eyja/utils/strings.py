import random
import string

from jinja2 import (
    FileSystemLoader,
    Environment
)


def random_string(prefix = None, length=0):
    result = prefix if prefix else ''

    letters = string.ascii_lowercase + string.digits
    return f'{result}{"".join(random.choice(letters) for i in range(length-len(result)))}'

async def render_template(template_root: str = None, template: str = None, data: dict = {}) -> str:
    template_loader = FileSystemLoader(searchpath=template_root)
    template_env = Environment(loader=template_loader, enable_async=True)
    template = template_env.get_template(template)
    return await template.render_async(data)
