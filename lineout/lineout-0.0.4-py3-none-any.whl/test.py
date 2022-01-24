__all__ = ["APITestMixin"]

from .status_codes import *
from .data import *
from .url import *
from django.test import Client


class APITestMixin:
    def assertApiAllowGet(self, url, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        res = client.get(url_add_params(url, params), content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, 200, msg=msg)
        data = res.json()
        return data

    def assertApiAllowPost(self, url, sample_data, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        res = client.post(url_add_params(url, params), sample_data, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_PASSED, msg=msg)
        return res.json()

    def assertApiForbidGet(self, url, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        res = client.get(url_add_params(url, params), content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_REJECTED, msg=msg)

    def assertApiForbidPost(self, url, sample_data, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        res = client.post(url_add_params(url, params), sample_data, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_REJECTED, msg=msg)

    def assertIsListResult(self, data, msg=None):
        try:
            return get_result_list(data)
        except ValueError as e:
            self.fail(self._formatMessage(msg, str(e)))

    def assertIsPaginatedListResult(self, data, msg=None):
        if not isinstance(data, dict) or 'results' not in data or not isinstance(data['results'], list):
            self.fail(self._formatMessage(msg, "Data is not paginated list api result: {}".format(data)))

    def assertApiAllowList(self, url, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(url, params)
        res = client.get(final_url, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, StatusCode.OK, msg=msg)
        data = res.json()
        return self.assertIsListResult(data, msg=msg)

    def assertApiAllowRetrieve(self, url, sample_id, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(get_detail_url(url, sample_id), params)
        res = client.get(final_url, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, 200, msg=msg)
        data = res.json()
        self.assertIsInstance(data, dict, msg=msg)
        return data

    def assertApiAllowCreate(self, url, sample_data, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(url, params)
        res = client.post(final_url, sample_data, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, 201, msg=msg)
        return res.json()

    def assertApiAllowUpdate(self, url, sample_id, sample_data, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(get_detail_url(url, sample_id), params)
        res = client.put(final_url, sample_data, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_PASSED, msg=msg)
        return res.json()

    def assertApiAllowPartialUpdate(self, url, sample_id, sample_data, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(get_detail_url(url, sample_id), params)
        res = client.patch(final_url, sample_data, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_PASSED, msg=msg)
        return res.json()

    def assertApiAllowDelete(self, url, sample_id, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(get_detail_url(url, sample_id), params)
        res = client.delete(final_url, **extra)
        self.assertStatusCodeIs(res.status_code, 204, msg=msg)

    def assertApiForbidList(self, url, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(url, params)
        res = client.get(final_url, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_REJECTED, msg=msg)

    def assertApiForbidRetrieve(self, url, sample_id, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(get_detail_url(url, sample_id), params)
        res = client.get(final_url, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_REJECTED, msg=msg)

    def assertApiForbidCreate(self, url, sample_data, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(url, params)
        res = client.post(final_url, sample_data, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_REJECTED, msg=msg)

    def assertApiForbidUpdate(self, url, sample_id, sample_data, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(get_detail_url(url, sample_id), params)
        res = client.put(final_url, sample_data, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_REJECTED, msg=msg)

        res = client.patch(final_url, sample_data, content_type='application/json', **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_REJECTED, msg=msg)

    def assertApiForbidDelete(self, url, sample_id, params=None, client=None, msg=None, **extra):
        if not client:
            client = Client()

        final_url = url_add_params(get_detail_url(url, sample_id), params)
        res = client.delete(final_url, **extra)
        self.assertStatusCodeIs(res.status_code, STATUS_REJECTED, msg=msg)

    def assertApiReadOnly(self, url, sample_id, sample_data, params=None, client=None, msg=None, **extra):
        self.assertApiForbidCreate(url, sample_data=sample_data, params=params, client=client, msg=msg, **extra)
        self.assertApiForbidUpdate(url, sample_id=sample_id, sample_data=sample_data, params=params, client=client, msg=msg, **extra)
        self.assertApiForbidDelete(url, sample_id=sample_id, params=params, client=client, msg=msg, **extra)

    def assertStatusCodeIs(self, status_code, code_or_group, msg=None):
        if isinstance(code_or_group, int):
            group = [code_or_group]
        elif isinstance(code_or_group, (list, tuple, set)):
            group = code_or_group
        else:
            raise ValueError('arg code_or_group should be int or seq of int, but got {}'.format(code_or_group))

        if status_code not in group:
            standardMsg = 'Got unexpected status code {}, should be {}'.format(status_code, ' or '.join(['{} ({})'.format(c, STATUS_DESCRIPTIONS.get(c, '??')) for c in group]))
            self.fail(self._formatMessage(msg, standardMsg))
