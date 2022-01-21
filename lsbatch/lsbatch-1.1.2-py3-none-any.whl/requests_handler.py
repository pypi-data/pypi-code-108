import io
import mimetypes
import uuid
from urllib import request, error
from lsbatch.constants import API_BASE_URL, API_URLS, ValidationMessages, Constants
import json


class RequestHandler:

    __org_code = None
    __token = None
    __region = None

    def __init__(self):
        pass

    @classmethod
    def set_up_credentials(cls, credentials):
        cls.__org_code = credentials.get(Constants.OrgCode)
        cls.__token = credentials.get(Constants.Token)
        cls.__region = credentials.get(Constants.Region)

    @classmethod
    def create_batch(cls, name, description):
        url = f"{API_BASE_URL.get(cls.__region.get('id'))}/{API_URLS.get('CreateBatch')}?{Constants.OrgCode}={cls.__org_code}"
        data = json.dumps({"Name": name, "Description": description}).encode("utf-8")
        headers = {"x-api-key": cls.__token, "Content-Type": "application/json"}
        response = cls.__call_api(url, "POST", data, headers)
        return response

    @classmethod
    def upload_zip(cls, batch_job_name, file_bytes_buffer, file_name):
        url = f"{API_BASE_URL.get(cls.__region.get('id'))}/{API_URLS.get('UploadZip')}?{Constants.OrgCode}={cls.__org_code}&batchjobname={batch_job_name}"
        file_bytes_buffer.seek(0)
        form = MultiPartForm()
        form.add_file('FormFile', file_name, file_bytes_buffer)
        form_data = bytes(form)
        headers = {"x-api-key": cls.__token, "Content-Type": form.get_content_type(),
                   'Content-Length': len(form_data)}
        response = cls.__call_api(url, "POST", form_data, headers)
        return response

    @classmethod
    def publish_batch(cls, batch_job_name):
        url = f"{API_BASE_URL.get(cls.__region.get('id'))}/{API_URLS.get('PublishBatch')}?{Constants.OrgCode}={cls.__org_code}&batchjobname={batch_job_name}"
        headers = {"x-api-key": cls.__token, "Content-Type": "application/json"}
        response = cls.__call_api(url, "POST", None, headers)
        return response

    @classmethod
    def save_settings(cls, batch_job_name, settings):
        url = f"{API_BASE_URL.get(cls.__region.get('id'))}/{API_URLS.get('AddVariables')}?{Constants.OrgCode}={cls.__org_code}"
        headers = {"x-api-key": cls.__token, "Content-Type": "application/json"}
        post_data = json.dumps({"BatchJobName": batch_job_name, "Settings": settings}).encode("utf-8")
        response = cls.__call_api(url, "POST", post_data, headers)
        return response

    @classmethod
    def get_package_info(cls):
        contents = request.urlopen('https://pypi.org/pypi/lsbatch/json').read()
        data = json.loads(contents)
        return data

    @classmethod
    def __call_api(cls, url, method, data, headers):
        try:
            api_request = request.Request(url, data=data, headers=headers, method=method)
            with request.urlopen(api_request) as f:
                data = f.read().decode()# getting data in utf-8 and would need conversion, therefore decode
            try:
                data = json.loads(data)
            except Exception:
                pass
            return {"Status": "Success", "Data": data}
        except Exception as ex:
            return cls.__handle_exception(ex)

    @classmethod
    def __handle_exception(cls, ex):
        response = {"Status": "Failed"}
        if type(ex) == error.HTTPError:
            if ex.code == 401 or ex.code == 403:
                response["ExceptionType"] = Constants.UnauthorizedAccess
                response["Message"] = ValidationMessages.UnAuthorizedAccess
                return response
            if ex.code == 400:
                data = {}
                try:
                    data = json.loads(ex.read().decode())
                except Exception:
                    pass
                if data.get('ExceptionType') is not None and data['ExceptionType'].startswith("MX"):
                    response["ExceptionType"] = data["ExceptionType"]
                    response["Message"] = data["ExceptionMessage"]
                    return response
        response["ExceptionType"] = Constants.UnexpectedError
        response["Message"] = ValidationMessages.SomethingWentWrong
        return response


class MultiPartForm:
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        # Use a large random byte string to separate
        # parts of the MIME data.
        self.boundary = uuid.uuid4().hex.encode('utf-8')
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary={}'.format(
            self.boundary.decode('utf-8'))

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))

    def add_file(self, fieldname, filename, fileHandle,
                 mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = (
                    mimetypes.guess_type(filename)[0] or
                    'application/octet-stream'
            )
        self.files.append((fieldname, filename, mimetype, body))
        return

    @staticmethod
    def _form_data(name):
        return ('Content-Disposition: form-data; '
                'name="{}"\r\n').format(name).encode('utf-8')

    @staticmethod
    def _attached_file(name, filename):
        return ('Content-Disposition: form-data; '
                'name="{}"; filename="{}"\r\n').format(
            name, filename).encode('utf-8')

    @staticmethod
    def _content_type(ct):
        return 'Content-Type: {}\r\n'.format(ct).encode('utf-8')

    def __bytes__(self):
        """Return a byte-string representing the form data,
        including attached files.
        """
        buffer = io.BytesIO()
        boundary = b'--' + self.boundary + b'\r\n'

        # Add the form fields
        for name, value in self.form_fields:
            buffer.write(boundary)
            buffer.write(self._form_data(name))
            buffer.write(b'\r\n')
            buffer.write(value.encode('utf-8'))
            buffer.write(b'\r\n')

        # Add the files to upload
        for f_name, filename, f_content_type, body in self.files:
            buffer.write(boundary)
            buffer.write(self._attached_file(f_name, filename))
            buffer.write(self._content_type(f_content_type))
            buffer.write(b'\r\n')
            buffer.write(body)
            buffer.write(b'\r\n')

        buffer.write(b'--' + self.boundary + b'--\r\n')
        return buffer.getvalue()
