from aiohttp.test_utils import unittest_run_loop, AioHTTPTestCase
from aiohttp import hdrs
from ..oidcclaimhdrs import SUB
from heaobject import user
from heaobject.root import from_dict
from ..representor import wstljson, cj, nvpjson, xwwwformurlencoded
from urllib.parse import urlencode
from typing import TYPE_CHECKING
from .mongotestcase import MongoTestCase
from .. import jsonschemavalidator
import logging


if TYPE_CHECKING:
    _Base = MongoTestCase
else:
    _Base = object


# The HTTP headers that every service call sends.
_standard_headers = {SUB: user.NONE_USER, hdrs.X_FORWARDED_HOST: 'localhost:8080'}


class PostMixin(_Base):
    @unittest_run_loop
    async def test_post(self) -> None:
        if not self._body_post:
            self.skipTest('_body_post not defined')
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        json=self._body_post,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: cj.MIME_TYPE})
        self.assertEqual('201: Created', await obj.text())

    @unittest_run_loop
    async def test_post_nvpjson(self) -> None:
        if not self._body_post:
            self.skipTest('_body_post not defined')
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        json={e['name']: e['value'] for e in self._body_post['template']['data']}, # type: ignore[index]
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
        self.assertEqual('201: Created', await obj.text())

    @unittest_run_loop
    async def test_post_xwwwformurlencoded(self) -> None:
        if not self._body_post:
            self.skipTest('_body_post not defined')
        try:
            data_ = self._post_data()
        except jsonschemavalidator.ValidationError:
            self.skipTest('_body_post cannot be converted xwwwformurlencoded form')
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        data=data_,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: xwwwformurlencoded.MIME_TYPE})
        self.assertEqual('201: Created', await obj.text())

    @unittest_run_loop
    async def test_post_status(self) -> None:
        if not self._body_post:
            self.skipTest('_body_post not defined')
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        json=self._body_post,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: cj.MIME_TYPE})
        self.assertEqual(201, obj.status)

    @unittest_run_loop
    async def test_post_status_nvpjson(self) -> None:
        if not self._body_post:
            self.skipTest('_body_post not defined')
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        json={e['name']: e['value'] for e in self._body_post['template']['data']}, # type: ignore[index]
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
        self.assertEqual(201, obj.status)

    @unittest_run_loop
    async def test_post_status_xwwwformurlencoded(self) -> None:
        if not self._body_post:
            self.skipTest('_body_post not defined')
        try:
            data_ = self._post_data()
        except jsonschemavalidator.ValidationError:
            self.skipTest('_body_post cannot be converted xwwwformurlencoded form')
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        data=data_,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: xwwwformurlencoded.MIME_TYPE})
        self.assertEqual(201, obj.status)

    @unittest_run_loop
    async def test_post_status_empty_body(self) -> None:
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: cj.MIME_TYPE})
        self.assertEqual(400, obj.status)

    @unittest_run_loop
    async def test_post_status_empty_body_nvpjson(self) -> None:
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
        self.assertEqual(400, obj.status)

    @unittest_run_loop
    async def test_post_status_empty_body_xwwwformurlencoded(self) -> None:
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: xwwwformurlencoded.MIME_TYPE})
        self.assertEqual(400, obj.status)

    @unittest_run_loop
    async def test_post_status_invalid_type(self) -> None:
        if not self._body_post:
            self.skipTest('_body_post not defined')
        await self._test_invalid({'type': 'foobar'})

    @unittest_run_loop
    async def test_invalid_url(self) -> None:
        if not self._body_post:
            self.skipTest('_body_post not defined')
        obj = await self.client.request('POST',
                                        (self._href / '1').path,
                                        json=self._body_post,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: cj.MIME_TYPE})
        self.assertEqual(405, obj.status)

    async def _test_invalid(self, changes) -> None:
        changed = _copy_heaobject_dict_with(self._body_post, changes)
        obj = await self.client.request('POST',
                                        (self._href / '').path,
                                        json=changed,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
        self.assertEqual(400, obj.status)

    def _post_data(self):
        return _to_xwwwformurlencoded_data(self._body_post)


class PutMixin(_Base):
    @unittest_run_loop
    async def test_put(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        obj = await self.client.request('PUT',
                                        (self._href / self._id()).path,
                                        json=self._body_put,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: cj.MIME_TYPE})
        self.assertEqual('', await obj.text())

    @unittest_run_loop
    async def test_put_nvpjson(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        obj = await self.client.request('PUT',
                                        (self._href / self._id()).path,
                                        json=cj.to_nvpjson(self._body_put) if self._body_put is not None else None,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
        self.assertEqual('', await obj.text())

    @unittest_run_loop
    async def test_put_xwwwformurlencoded(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        try:
            data_ = self._put_data()
        except jsonschemavalidator.ValidationError:
            self.skipTest('_body_put cannot be converted xwwwformurlencoded form')
        else:
            obj = await self.client.request('PUT',
                                            (self._href / self._id()).path,
                                            data=data_,
                                            headers={**_standard_headers, hdrs.CONTENT_TYPE: xwwwformurlencoded.MIME_TYPE})
            self.assertEqual('', await obj.text())

    @unittest_run_loop
    async def test_put_status(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        obj = await self.client.request('PUT',
                                        (self._href / self._id()).path,
                                        json=self._body_put,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: cj.MIME_TYPE})
        self.assertEqual(204, obj.status)

    @unittest_run_loop
    async def test_put_status_wrong_format(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        else:
            obj = await self.client.request('PUT',
                                            (self._href / self._id()).path,
                                            json=cj.to_nvpjson(self._body_put),
                                            headers={**_standard_headers, hdrs.CONTENT_TYPE: cj.MIME_TYPE})
            self.assertEqual(400, obj.status)

    @unittest_run_loop
    async def test_put_status_nvpjson(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        else:
            obj = await self.client.request('PUT',
                                            (self._href / self._id()).path,
                                            json=cj.to_nvpjson(self._body_put),
                                            headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
            self.assertEqual(204, obj.status)

    @unittest_run_loop
    async def test_put_status_nvpjson_wrong_format(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        try:
            data_ = self._put_data()
        except jsonschemavalidator.ValidationError:
            self.skipTest('_body_put cannot be converted xwwwformurlencoded form')
        else:
            obj = await self.client.request('PUT',
                                            (self._href / self._id()).path,
                                            json=data_,
                                            headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
        self.assertEqual(400, obj.status)

    @unittest_run_loop
    async def test_put_status_xwwwformurlencoded(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        try:
            data_ = self._put_data()
        except jsonschemavalidator.ValidationError:
            self.skipTest('_body_put cannot be converted xwwwformurlencoded form')
        else:
            obj = await self.client.request('PUT',
                                            (self._href / self._id()).path,
                                            data=data_,
                                            headers={**_standard_headers, hdrs.CONTENT_TYPE: xwwwformurlencoded.MIME_TYPE})
            self.assertEqual(204, obj.status)

    @unittest_run_loop
    async def test_put_status_xwwwformurlencoded_wrong_format(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        obj = await self.client.request('PUT',
                                        (self._href / self._id()).path,
                                        json=self._body_put,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: xwwwformurlencoded.MIME_TYPE})
        self.assertEqual(400, obj.status)

    @unittest_run_loop
    async def test_put_status_empty_body(self) -> None:
        obj = await self.client.request('PUT',
                                        (self._href / '666f6f2d6261722d71757578').path,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: cj.MIME_TYPE})
        self.assertEqual(400, obj.status)

    @unittest_run_loop
    async def test_put_status_empty_body_nvpjson(self) -> None:
        obj = await self.client.request('PUT',
                                        (self._href / '666f6f2d6261722d71757578').path,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
        self.assertEqual(400, obj.status)

    @unittest_run_loop
    async def test_put_status_empty_body_xwwwformurlencoded(self) -> None:
        obj = await self.client.request('PUT',
                                        (self._href / '666f6f2d6261722d71757578').path,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: xwwwformurlencoded.MIME_TYPE})
        self.assertEqual(400, obj.status)

    @unittest_run_loop
    async def test_put_status_missing_id(self) -> None:
        obj = await self.client.request('PUT',
                                        self._href.path,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: cj.MIME_TYPE})
        self.assertEqual(405, obj.status)

    @unittest_run_loop
    async def test_put_status_missing_id_nvpjson(self) -> None:
        obj = await self.client.request('PUT',
                                        self._href.path,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
        self.assertEqual(405, obj.status)

    @unittest_run_loop
    async def test_put_status_invalid_type(self) -> None:
        if not self._body_put:
            self.skipTest('_body_put not defined')
        await self._test_invalid({'type': 'foobar'})

    @unittest_run_loop
    async def test_put_content(self) -> None:
        if not self._put_content_status:
            self.skipTest('_put_content_status not defined')
        obj = await self.client.request('PUT',
                                        (self._href / self._id() / 'content').path,
                                        data='The quick brown fox jumps over the lazy dog',
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: 'text/plain'})
        self.assertEquals(self._put_content_status, obj.status)

    async def _test_invalid(self, changes) -> None:
        changed = _copy_heaobject_dict_with(self._body_put, changes)
        obj = await self.client.request('PUT',
                                        (self._href / '666f6f2d6261722d71757578').path,
                                        json=changed,
                                        headers={**_standard_headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
        self.assertEqual(400, obj.status)

    def _put_data(self):
        return _to_xwwwformurlencoded_data(self._body_put)

    def _id(self):
        logging.getLogger(__name__).debug('Template is %s', self._body_put)
        for e in self._body_put['template']['data']:
            if e['name'] == 'id':
                return e.get('value')


class GetOneMixin(_Base):
    @unittest_run_loop
    async def test_get(self) -> None:
        obj = await self.client.request('GET',
                                        (self._href / '666f6f2d6261722d71757578').path,
                                        headers=_standard_headers)
        self.assertEqual(_ordered(self._expected_one), _ordered(await obj.json()))

    @unittest_run_loop
    async def test_get_status(self) -> None:
        obj = await self.client.request('GET',
                                        (self._href / '666f6f2d6261722d71757578').path,
                                        headers=_standard_headers)
        self.assertEqual(200, obj.status)

    @unittest_run_loop
    async def test_get_wstl(self) -> None:
        if not self._expected_one_wstl:
            self.skipTest('self._expected_one_wstl is not defined')
        obj = await self.client.request('GET',
                                        (self._href / '666f6f2d6261722d71757578').path,
                                        headers={**_standard_headers, hdrs.ACCEPT: wstljson.MIME_TYPE})
        self.assertEqual(_ordered(self._expected_one_wstl), _ordered(await obj.json()))

    @unittest_run_loop
    async def test_get_not_acceptable(self) -> None:
        if not self._expected_one_wstl:
            self.skipTest('self._expected_one_wstl is not defined')
        obj = await self.client.request('GET',
                                        (self._href / '666f6f2d6261722d71757578').path,
                                        headers={**_standard_headers, hdrs.ACCEPT: 'application/msword'})
        self.assertEqual(406, obj.status)

    @unittest_run_loop
    async def test_get_duplicate_form(self) -> None:
        if not self._expected_one_duplicate_form:
            self.skipTest('self._expected_one_duplicate_wstl is not defined')
        obj = await self.client.request('GET',
                                        (self._href / '666f6f2d6261722d71757578' / 'duplicator').path,
                                        headers=_standard_headers)
        self.assertEqual(_ordered(self._expected_one_duplicate_form), _ordered(await obj.json()))

    @unittest_run_loop
    async def test_opener_header(self) -> None:
        if not self._expected_opener:
            self.skipTest('self._expected_opener is not defined')
        obj = await self.client.request('GET',
                                        (self._href / '666f6f2d6261722d71757578' / 'opener').path,
                                        headers=_standard_headers)
        self.assertEqual(self._expected_opener, obj.headers[hdrs.LOCATION])

    @unittest_run_loop
    async def test_opener_body(self) -> None:
        if not self._expected_opener_body:
            self.skipTest('self._expected_opener_body is not defined')
        obj = await self.client.request('GET',
                                        (self._href / '666f6f2d6261722d71757578' / 'opener').path,
                                        headers=_standard_headers)
        self.assertEqual(_ordered(self._expected_opener_body), _ordered(await obj.json()))

    @unittest_run_loop
    async def test_get_content(self) -> None:
        if not self._content:
            self.skipTest('self._content is not defined')
        else:
            content = self._content
        obj = await self.client.request('GET',
                                        (self._href / '666f6f2d6261722d71757578' / 'content').path,
                                        headers=_standard_headers)
        flag = True
        try:
            expected = content[self._coll]['666f6f2d6261722d71757578']
            if isinstance(expected, (dict, list)):
                self.assertEqual(_ordered(expected), _ordered(await obj.json()))
            elif isinstance(expected, str):
                self.assertEqual(expected, await obj.text())
            else:
                self.assertEqual(expected, await obj.read())
            obj.close()
            flag = False
        finally:
            if flag:
                try:
                    obj.close()
                except OSError:
                    pass

    @unittest_run_loop
    async def test_get_content_type(self) -> None:
        if not self._content:
            self.skipTest('self._content is not defined')
        if not self._content_type:
            self.skipTest('self._content_type is not defined')
        obj = await self.client.request('GET',
                                        (self._href / '666f6f2d6261722d71757578' / 'content').path,
                                        headers=_standard_headers)
        flag = True
        try:
            self.assertEqual(self._content_type, obj.headers.get(hdrs.CONTENT_TYPE))
            obj.close()
            flag = False
        finally:
            if flag:
                try:
                    obj.close()
                except OSError:
                    pass


class GetAllMixin(_Base):
    @unittest_run_loop
    async def test_get_all(self) -> None:
        obj = await self.client.request('GET',
                                        (self._href / '').path,
                                        headers=_standard_headers)
        self.assertEqual(200, obj.status)

    @unittest_run_loop
    async def test_get_all_json(self) -> None:
        obj = await self.client.request('GET',
                                        (self._href / '').path,
                                        headers=_standard_headers)
        self.assertEqual(_ordered(self._expected_all), _ordered(await obj.json()))

    @unittest_run_loop
    async def test_get_all_wstl(self) -> None:
        if not self._expected_all_wstl:
            self.skipTest('self._expected_all_wstl is not defined')
        obj = await self.client.request('GET',
                                        (self._href / '').path,
                                        headers={**_standard_headers, hdrs.ACCEPT: wstljson.MIME_TYPE})
        self.assertEqual(_ordered(self._expected_all_wstl), _ordered(await obj.json()))


class DeleteMixin(_Base):
    @unittest_run_loop
    async def test_delete_success(self) -> None:
        obj = await self.client.request('DELETE',
                                        (self._href / '666f6f2d6261722d71757578').path,
                                        headers=_standard_headers)
        self.assertEqual(204, obj.status)

    @unittest_run_loop
    async def test_delete_fail(self) -> None:
        obj = await self.client.request('DELETE',
                                        (self._href / '3').path,
                                        headers=_standard_headers)
        self.assertEqual(404, obj.status)


def _copy_heaobject_dict_with(d, changes):
    copied_dict = dict(d)
    copied_dict.update(changes)
    return copied_dict


def _to_xwwwformurlencoded_data(template) -> str:
    _logger = logging.getLogger(__name__)
    _logger.debug('Encoding %s', template)
    e = {}
    jsonschemavalidator.CJ_TEMPLATE_SCHEMA_VALIDATOR.validate(template)
    for e_ in template['template']['data']:
        if 'section' in e_:
            raise jsonschemavalidator.ValidationError('XWWWFormUrlEncoded does not support the section property')
        if e_['value'] is not None:
            e[e_['name']] = e_['value']
    result = urlencode(e, True)
    _logger.debug('Returning %s', result)
    return result


def _ordered(obj):
    if isinstance(obj, dict):
        def _ordered_one(k, v):
            if k == 'rel' and isinstance(v, str):
                return k, _ordered(' '.join(sorted(v.split() if v else [])))
            else:
                return k, _ordered(v)
        return sorted(_ordered_one(k, v) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    else:
        return obj
