import os
import subprocess  # noqa
from tempfile import TemporaryDirectory
from typing import Optional, Tuple, Union
from urllib.parse import urljoin

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext as _

from celery.result import AsyncResult
from celery_progress.backend import ProgressRecorder

from aleksis.core.celery import app
from aleksis.core.models import PDFFile
from aleksis.core.util.celery_progress import recorded_task, render_progress_page
from aleksis.core.util.core_helpers import process_custom_context_processors


@recorded_task
def generate_pdf(
    file_pk: int, html_url: str, recorder: ProgressRecorder, lang: Optional[str] = None
):
    """Generate a PDF file by rendering the HTML code using a headless Chromium."""
    file_object = get_object_or_404(PDFFile, pk=file_pk)

    recorder.set_progress(0, 1)

    # Open a temporary directory
    with TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, "print.pdf")
        lang = lang or get_language()

        # Run PDF generation using a headless Chromium
        cmd = [
            "chromium",
            "--headless",
            "--no-sandbox",
            "--run-all-compositor-stages-before-draw",
            "--temp-profile",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-setuid-sandbox",
            "--dbus-stub",
            f"--home-dir={temp_dir}",
            f"--lang={lang}",
            f"--print-to-pdf={pdf_path}",
            html_url,
        ]
        res = subprocess.run(cmd)  # noqa

        # Let the task fail on a non-success return code
        res.check_returncode()

        # Upload PDF file to media storage
        with open(pdf_path, "rb") as f:
            file_object.file.save("print.pdf", File(f))
            file_object.save()

    recorder.set_progress(1, 1)


def generate_pdf_from_template(
    template_name: str, context: Optional[dict] = None, request: Optional[HttpRequest] = None
) -> Tuple[PDFFile, AsyncResult]:
    """Start a PDF generation task and return the matching file object and Celery result."""
    if not request:
        processed_context = process_custom_context_processors(settings.PDF_CONTEXT_PROCESSORS)
        processed_context.update(context)
    else:
        processed_context = context
    html_template = render_to_string(template_name, processed_context, request)

    file_object = PDFFile.objects.create(html_file=ContentFile(html_template, name="source.html"))

    # As this method may be run in background and there is no request available,
    # we have to use a predefined URL from settings then
    if request:
        html_url = request.build_absolute_uri(file_object.html_file.url)
    else:
        html_url = urljoin(settings.BASE_URL, file_object.html_file.url)

    result = generate_pdf.delay(file_object.pk, html_url, lang=get_language())

    return file_object, result


def render_pdf(
    request: Union[HttpRequest, None], template_name: str, context: dict = None
) -> HttpResponse:
    """Start PDF generation and show progress page.

    The progress page will redirect to the PDF after completion.
    """
    if not context:
        context = {}

    file_object, result = generate_pdf_from_template(template_name, context, request)

    redirect_url = reverse("redirect_to_pdf_file", args=[file_object.pk])

    return render_progress_page(
        request,
        result,
        title=_("Progress: Generate PDF file"),
        progress_title=_("Generating PDF file …"),
        success_message=_("The PDF file has been generated successfully."),
        error_message=_("There was a problem while generating the PDF file."),
        redirect_on_success_url=redirect_url,
        back_url=context.get("back_url", reverse("index")),
        button_title=_("Download PDF"),
        button_url=redirect_url,
        button_icon="picture_as_pdf",
    )


def clean_up_expired_pdf_files() -> None:
    """Clean up expired PDF files."""
    PDFFile.objects.filter(expires_at__lt=timezone.now()).delete()


@app.task
def clean_up_expired_pdf_files_task() -> None:
    """Clean up expired PDF files."""
    return clean_up_expired_pdf_files()
