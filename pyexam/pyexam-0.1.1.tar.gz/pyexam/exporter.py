import logging
import os
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, PackageLoader

from . import Exam

logger = logging.getLogger(__name__)


@lru_cache
def get_jinja_env(template_dir: Optional[str]) -> Environment:
    # only load each template once if multiple exams rendered
    loader = (FileSystemLoader(template_dir) if template_dir
              else PackageLoader('pyexam', 'templates'))
    env = Environment(loader=loader)
    env.globals['render_question'] = question_renderer(env)
    return env


def question_renderer(env: Environment):
    def render_question(question: dict, solution: bool = False, is_part: bool = False,) -> str:
        question_type = question['type']
        template = env.get_template(f'{question_type}.j2')
        return template.render(question | {'is_part': is_part, 'solution': solution})
    return render_question


def render(exam: Exam, solution: bool = False, template_dir: Optional[str] = None) -> str:
    env = get_jinja_env(template_dir)
    template = env.get_template('exam.j2')  # templates are cached
    return template.render(exam.dict() | {'solution': solution})


def export(exam: Exam, dir: str, file_name: str, solution: bool, template_dir: Optional[str]) -> None:
    Path(dir).mkdir(parents=False, exist_ok=True)
    file_path = os.path.join(dir, file_name)
    rendered = render(exam, solution, template_dir)
    with open(file_path, 'w') as file:
        file.write(rendered)


def export_latex(exam: Exam, dir: str, solution: bool = False, template_dir: Optional[str] = None) -> None:
    export(exam, dir, f'{exam.name}.tex', solution, template_dir)


def export_pdf(exam: Exam, dir: str, solution: bool = False, template_dir: Optional[str] = None) -> None:
    export_latex(exam, dir, solution, template_dir)
    args = ['latexmk', '-interaction=nonstopmode', '-pdf', f'{exam.name}.tex']
    result = subprocess.run(args, capture_output=True, cwd=dir)
    logger.debug(f'stdout {result.stdout.decode("utf-8")}')
    if result.stderr:
        logger.debug(f'stderr {result.stderr.decode("utf-8")}')
    result.check_returncode()
