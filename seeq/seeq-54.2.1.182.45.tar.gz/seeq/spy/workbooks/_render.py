import os
import re
import textwrap

from seeq.base import system
from seeq.sdk import *
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status


# noinspection PyPep8Naming
def pull(session: Session, report, *, errors='raise', quiet=False, status: Status = None):
    status = Status.validate(status, quiet)
    _common.validate_errors_arg(errors)
    report.rendered_content_images = None
    images = dict()

    content_api = ContentApi(session.client)

    def _get_screenshot(_content_id):
        _timer = _common.timer_start()

        # noinspection PyBroadException
        try:
            status.send_update(_content_id, {
                'Result': 'Rendering',
                'Time': _common.timer_elapsed(_timer)
            })

            if session.options.clear_content_cache_before_render:
                content_api.clear_image_cache(id=_content_id)

            _seeq_url = session.public_url
            _request_url = _seeq_url + f'/api/content/{_content_id}/image'

            status.send_update(_content_id, {
                'Result': 'Success',
                'Time': _common.timer_elapsed(_timer)
            })

            return _content_id, _login.pull_image(session, _request_url)

        except BaseException:
            status.send_update(_content_id, {
                'Result': _common.format_exception(),
                'Time': _common.timer_elapsed(_timer)
            })

            if errors == 'raise':
                raise

    def _on_success(_row_index, _job_result):
        _content_id, _image = _job_result
        images[(_content_id, 'Content.png')] = _image

    img_matches = re.finditer(r'<img[^>]* data-seeq-content="([^"]+)".*?>', report.html, re.IGNORECASE)
    for img_match in img_matches:
        content_id = img_match.group(1)

        status.df.at[content_id, 'Content ID'] = content_id
        status.df.at[content_id, 'Result'] = 'Queued'

        status.add_job(content_id,
                       (_get_screenshot, content_id),
                       _on_success)

    job_count = len(status.jobs)
    status.update(f'Pulling {job_count} pieces of embedded content', Status.RUNNING)
    try:
        status.execute_jobs(session, errors)
        status.update(f'Pulled {job_count} pieces of embedded content', Status.SUCCESS)
        report.rendered_content_images = images
    except BaseException as e:
        status.exception(e, throw=(errors == 'raise'))


def get_rendered_topic_folder(workbook_folder: str):
    return os.path.join(workbook_folder, 'RenderedTopic')


def save(report, workbook_folder: str):
    if report.rendered_content_images is None:
        raise SPyValueError(f'Embedded content for {report.worksheet} has not been pulled. '
                            'Use include_embedded_content=True when calling spy.workbooks.pull()')

    rendered_topic_folder = get_rendered_topic_folder(workbook_folder)
    os.makedirs(rendered_topic_folder, exist_ok=True)
    _common.save_image_files(report.rendered_content_images, rendered_topic_folder)
    _common.save_image_files(report.images, rendered_topic_folder)
    img_matches = re.finditer(r'<img[^>]*>', report.html, re.IGNORECASE)
    new_html = ''
    cursor = 0

    for img_match in img_matches:
        image_file = None
        img_html = img_match.group(0)
        embedded_content_match = re.search(r' data-seeq-content="([^"]*)"', img_html)
        static_image_match = re.search(r' src="/api(/annotations/(.*?)/images/(.*?))"', img_html)
        if embedded_content_match:
            embedded_content_id = embedded_content_match.group(1)
            if (embedded_content_id, 'Content.png') in report.rendered_content_images:
                image_file = _common.get_image_file(rendered_topic_folder, (embedded_content_id, 'Content.png'))
        elif static_image_match:
            image_id_tuple = (static_image_match.group(2), static_image_match.group(3))
            if image_id_tuple in report.images:
                image_file = _common.get_image_file(rendered_topic_folder, image_id_tuple)

        new_html += report.html[cursor:img_match.start()]
        if image_file:
            image_file = os.path.basename(system.cleanse_path(image_file, windows_long_path=False))
            src_match = re.search(r' src="([^"]*)"', img_html)
            img_html = img_html[0:src_match.start(1)] + image_file + img_html[src_match.end(1):]

        new_html += img_html
        cursor = img_match.end()

    new_html += report.html[cursor:]

    new_html = textwrap.dedent(f"""
            <html>
            <head>
              <link rel="stylesheet" href="app.css">
              <title>{report.worksheet.name}</title>
            </head>
            <body style="overflow: auto;">
            <div class="p10">
            {new_html}
            </div>
            </body>
            </html>
        """)

    with open(os.path.join(rendered_topic_folder, f'{report.id}.html'), 'w', encoding='utf-8') as f:
        f.write(new_html)

    system.copyfile(os.path.join(os.path.dirname(__file__), 'app.css'),
                    os.path.join(rendered_topic_folder, 'app.css'))


def toc(workbook, workbook_folder: str):
    rendered_topic_folder = get_rendered_topic_folder(workbook_folder)

    worksheet_html = [textwrap.dedent(f"""
        <li class="list-group-item"><a class="h2" href="{worksheet.document.id}.html">{worksheet.name}</a></li>
    """) for worksheet in workbook.worksheets]

    worksheets_html = '\n'.join(worksheet_html)

    new_html = textwrap.dedent(f"""
            <html>
            <head>
              <link rel="stylesheet" href="app.css">
              <title>{workbook.name}</title>
            </head>
            <body style="overflow: auto;">
            <div class="p10">
            <p class="h1">{workbook.name}</p>
            <ul>
            {worksheets_html}
            </ul>
            </div>
            </body>
            </html>
        """)

    index_filename = os.path.join(rendered_topic_folder, 'index.html')
    os.makedirs(os.path.dirname(index_filename), exist_ok=True)
    with open(index_filename, 'w', encoding='utf-8') as f:
        f.write(new_html)
