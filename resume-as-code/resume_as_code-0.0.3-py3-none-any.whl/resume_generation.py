import logging
import os
import tempfile
from typing import Dict, List

import magic
import requests  # To request the images listed in the badges
import yaml  # Retrieve the context
from docx.shared import Mm  # Set the height of the inlined image
from docxtpl import DocxTemplate, InlineImage  # Create Microsoft Word template
from jinja2 import Environment  # To pass custom filters to template

from resume_as_code.util import store_image_to_temp
from resume_as_code.validation import validate_resume


def fetch_resume_template(template_location: str) -> DocxTemplate:
    """
    [Retrieve the resume template]

    Args:
        template_location (str): [the location where the resume template is stored]
    Raises:
        FileNotFoundError: [if the file with filename provided in template_location does not exist]
        ValueError: [if the file is of the wrong filetype]
    Returns:
        DocxTemplate: [the Docx-Jinja-template]
    """
    if not os.path.exists(template_location):
        raise FileNotFoundError(
            "There is no file with location {}".format(template_location)
        )

    if "Microsoft Word" not in magic.from_file(template_location):
        raise ValueError(
            "Wrong filetype provided for the template file with location {}".format(
                template_location
            )
        )

    return DocxTemplate(template_location)


def fetch_yaml_context(context_location: str, schema_filename: str) -> Dict[str, Dict]:
    """
    [Retrieve the yaml context from its file and return as dictionary]

    Args:
        context_location (str): [the location where the yaml-resume is stored]
        schema_filename (str): [the filename containing the yaml specification]
    Raises:
        FileNotFoundError: [if the file with filename provided in context_location does not exist]
        ValueError: [if the file with the filename provided in context_location does not adhere to the spec defined in $SCHEMA_FILENAME]
    Returns:
        Dict[str, Dict]: [a dictionairy of key-value pairs]
    """
    if not os.path.exists(context_location):
        raise FileNotFoundError(
            "There is no file with location {}".format(context_location)
        )

    with open(context_location, "r") as file:
        yaml_resume = yaml.load(file, Loader=yaml.FullLoader)

    msg, validation_flag = validate_resume(yaml_resume, schema_filename)
    if validation_flag:
        logging.info(msg.format(context_location=context_location))
        return yaml_resume
    else:
        raise ValueError(msg.format(context_location=context_location))


def render_and_save(
    template: DocxTemplate,
    context: Dict[str, Dict],
    jinja_env: Environment,
    target_location: str,
) -> int:
    """
    [Render the template with the provided context and store in the target location]

    Args:
        template (DocxTemplate): [the Jinja-parametrized template]
        context (Dict[str, Dict]): [the YAML-context retrieved from the resume]
        jinja_env (Environment): [the jinja2 Environment to be passed down to the template]
        target_location (str): [the location to store the file in]

    Returns:
        int: [an integer status code]
    """
    with tempfile.TemporaryDirectory() as image_folder:
        preprocess_context(context, template, image_folder)
    template.render(context=context, jinja_env=jinja_env)
    template.save(target_location)
    return 0


def preprocess_context(
    context: Dict[str, Dict], template: DocxTemplate, image_folder: str
) -> None:
    """
    [Preprocess the context. Inline the images.]

    Args:
        context (Dict[str, Dict]): [The dict containing the yaml resume-values]
        template (DocxTemplate): [The template to inline the images on]
        image_folder (str): [The name of the temporary directory to save the images in]
    """
    for cert in context["contact"]["certifications"]:
        if "badge_image" not in cert.keys():
            continue
        badge_location = cert["badge_image"]
        try:
            image_location = store_image_to_temp(image_folder, badge_location)
            logging.info(f"Inlining image from location {image_location}")
            cert["image"] = InlineImage(template, image_location, height=Mm(20))
        except ValueError as e:
            # In case of an invalid url, the image shouldn't be inlined. Log the error though.
            logging.warning(e)
        except requests.exceptions.ConnectionError as e:  # type: ignore
            logging.warning(f"The url in string {badge_location} does not exist")


def with_badge(certs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    [Filter those certifications with a badge]

    Args:
        certs (List[Dict[str, str]]): [The unfiltered list of certifications]

    Returns:
        List[Dict[str, str]]: [Only those certifications that have a badge_image linked to it]
    """
    badged_certs = [cert for cert in certs if "badge_image" in cert.keys()]
    return badged_certs


def without_badge(certs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    [Filter those certifications with a badge]

    Args:
        certs (List[Dict[str, str]]): [The unfiltered list of certifications]

    Returns:
        List[Dict[str, str]]: [Only those certifications that have a badge_image linked to it]
    """
    badged_certs = [cert for cert in certs if "badge_image" not in cert.keys()]
    return badged_certs


def generate_resume(
    template_location: str,
    context_location: str,
    target_location: str,
    schema_location: str,
) -> int:
    """
    [Go through the entire flow of generating the resume]

    Args:
        template_location (str): [the location where the template is stored]
        context_location (str): [the location where the context is stored]
        target_location (str): [the location to store the generated resume in]
        schema_location (str): [the location where the yaml specification is stored]

    Returns:
        int: [the status code to indicate succes/not]
    """
    template = fetch_resume_template(template_location)
    try:
        context = fetch_yaml_context(context_location, schema_location)
    except ValueError as _:
        logging.error(
            f"The context in '{context_location}' does not contain a valid resume. Please review the spec in {schema_location}"
        )
        exit(1)
    jinja_env = Environment()
    jinja_env.filters["with_badge"] = with_badge
    jinja_env.filters["without_badge"] = without_badge
    status_code = render_and_save(template, context, jinja_env, target_location)
    return status_code
