import os
template_dir = os.path.dirname(os.path.abspath(__file__))


def get_template_path(template_name):
    return os.path.join(template_dir, template_name)
