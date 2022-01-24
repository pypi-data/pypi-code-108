#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from datarobot.models.api_object import APIObject
from datarobot.utils import deprecation_warning, get_id_from_response


class ComplianceDocumentation(APIObject):
    """
    A :ref:`compliance documentation <compliance_documentation_overview>` object.

    .. versionadded:: v2.14

    Attributes
    ----------
    project_id : str
        the id of the project
    model_id : str
        the id of the model
    template_id : str or None
        optional id of the template for the generated doc. See documentation for
        :py:class:`ComplianceDocTemplate
        <datarobot.models.compliance_doc_template.ComplianceDocTemplate>` for more info.

    Examples
    --------
    .. code-block:: python

        doc = ComplianceDocumentation('project-id', 'model-id')
        job = doc.generate()
        job.wait_for_completion()
        doc.download('example.docx')

    """

    def __init__(self, project_id, model_id, template_id=None):
        self.project_id = project_id
        self.model_id = model_id
        self.template_id = template_id

        deprecation_warning(
            "ComplianceDocumentation",
            deprecated_since_version="v2.24",
            will_remove_version="v2.27",
            message="Use AutomatedDocument instead.",
        )

    def generate(self):

        """
        Start a job generating model compliance documentation.

        Returns
        -------
        Job
            an instance of an async job
        """
        from . import Job

        url = "projects/{}/models/{}/complianceDocs/".format(self.project_id, self.model_id)
        payload = {"template_id": self.template_id} if self.template_id else {}
        response = self._client.post(url, data=payload)
        job_id = get_id_from_response(response)

        return Job.get(self.project_id, job_id)

    def download(self, filepath):
        """ Download the generated compliance documentation file and save it
        to the specified path. The generated file has a DOCX format.

        Parameters
        ----------
        filepath : str
            A file path, e.g. "/path/to/save/compliance_documentation.docx"
        """
        url = "projects/{}/models/{}/complianceDocs/".format(self.project_id, self.model_id)
        response = self._client.get(url, stream=True)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
