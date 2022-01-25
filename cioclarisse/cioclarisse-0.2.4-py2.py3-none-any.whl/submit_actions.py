"""Handle button presses to submit and preview jobs.

Preview, open a window containing the submission script JSON, and
eventually also the structure of the submission and the JSON objects
that will be sent to Conductor.

Submit, send jobs straight to Conductor.
"""
import ix
from cioclarisse import utils
from cioclarisse import preview_ui
from cioclarisse.submission import Submission
from cioclarisse import validation
from ciocore.validator  import ValidationError

 
def submit(*args):
    """
    Validate and submit directly.
    """
    node = args[0]
    try:
        validation.run(node)
    except ValidationError as ex:
        ix.log_error(str(ex))
        return

    with utils.waiting_cursor():
        submission = Submission(node)
        response = submission.submit()
    if response:
        preview_ui.show_submission_responses(response)
    else:
        ix.log_error(str("No Response"))

def write_render_package(*args):
    node = args[0]
    with utils.waiting_cursor():
        submission = Submission(node)
        submission.write_render_package()

def preview(*args):
    """
    Validate and show the script in a panel.

    Submission can be invoked from the preview panel.
    """
    node = args[0]
    with utils.waiting_cursor():
        submission = Submission(node)
    preview_ui.build(submission)
