import time
from datetime import timedelta

from django.utils import timezone

from celery_progress.backend import Progress

from aleksis.apps.evalu.models import EvaluationRegistration
from aleksis.core.celery import app
from aleksis.core.util.pdf import generate_pdf_from_template


@app.task
def generate_privacy_form_task(pk: int) -> bool:
    registration = EvaluationRegistration.objects.get(pk=pk)

    file_object, result = generate_pdf_from_template(
        "evalu/registration/print.html", {"object": registration}
    )
    progress = Progress(result)
    start_time = timezone.now()
    while timezone.now() - start_time < timedelta(minutes=5):
        info = progress.get_info()
        if info["complete"]:
            file_object.refresh_from_db()
            if file_object.file:
                registration.privacy_form.save("privacy_form.pdf", file_object.file.file)
                registration.save()
                return True
        time.sleep(0.5)
    return False
