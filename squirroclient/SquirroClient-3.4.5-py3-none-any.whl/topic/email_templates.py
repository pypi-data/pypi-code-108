import json


class EmailTemplatesMixin(object):
    def list_email_templates(self):
        """List all email templates.

        :return List of email template names.
        """

        url = "%(ep)s/v0/%(tenant)s/email_templates" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res, [200])

    def get_email_template(self, template_name):
        """Get an email template.

        :param template_name: str, the name of the template
        :return dict
        """

        url = "%(ep)s/v0/%(tenant)s/email_templates/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "name": template_name,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res, [200])

    def edit_email_template(self, template_name, data):
        """Edit an email template.

        :param template_name: str, the name of the template
        :param data: dict, the json body
        """

        url = "%(ep)s/v0/%(tenant)s/email_templates/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "name": template_name,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [200])

    def send_sample_email(self, template_name, email, data):
        """Sends a sample email.

        :param template_name: str, the name of the template
        :param email: str, email address
        :param data: dict, with the keys content, content_plain, subject
            providing email templates
        """

        url = "%(ep)s/v0/%(tenant)s/email_templates/%(name)s/sample/%(email)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "name": template_name,
            "email": email,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, headers=headers, data=json.dumps(data))
        return self._process_response(res, [200])
