"""
Submit.

"""
import traceback
from ciocore import conductor_submit
from pymxs import runtime as rt
from ciomax import validation
 
def submit(dialog):
    """Initiate the submission wit validations."""
    # validation runs before saving or changing anything
    errors, warnings, notices = validation.run(dialog)

    if  errors or warnings or notices:
        dialog.show_validation_tab()
        dialog.validation_tab.populate(errors, warnings, notices)
    else:
        do_submit(dialog)

def do_submit(dialog):
    """
    Submit the job.
    
    Get the result and display in the responses tab as appropriate.
    """

    advanced_section = dialog.main_tab.section("AdvancedSection")
    show_tracebacks = advanced_section.tracebacks_checkbox.isChecked()

    context = dialog.get_context()
    submission = dialog.main_tab.resolve(context)

    try:
        remote_job = conductor_submit.Submit(submission)
        response, response_code = remote_job.main()
        result = {"code": response_code, "response": response}
        # Typical result is: 
        # {'code': 201, 'response': {u'body': u'job submitted.', u'status': u'success', u'uri': u'/jobs/01140', u'jobid': u'01140'}}
    except BaseException as ex:
        if show_tracebacks:
            msg = traceback.format_exc()
        else:
            msg = str(ex)
        code = int(str(ex).split(" ")[4])
        result = {"code": code, "response": msg}
 

    dialog.show_response_tab()
    dialog.response_tab.populate(result)

