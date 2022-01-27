"""Namespace for AsynicIO version of the sdk

It is very basic, like the plain one
"""
import json
import aiohttp

async def get_path(url=None, data=None):
    """TODO"""
    if data is None:
        data = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, data=data) as resp:
            response = await resp.text()

    return response

async def post_path(url=None, data=None):
    """TODO"""
    if data is None:
        data = {}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as resp:
            response = await resp.text()

    return response

API_HOSTS = {
    'v1': 'vapi.netactuate.com',
}


class NetActuateException(Exception):
    """TODO"""
    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.args = (code, message)
        super().__init__(message)

    async def __str__(self):
        return self.__repr__()

    async def __repr__(self):
        return "<NetActuateException in %d : %s>" % (self.code, self.message)


# pylint: disable=useless-object-inheritance, too-few-public-methods
class HVFromDict(object):
    """Takes any dict and creates an object out of it
    May behave weirdly if you do multiple level dicts
    So don't...
    """
    def __init__(self, kwargs):
        self.__dict__ = kwargs

    def __len__(self):
        return len(self.__dict__)


class HVJobStatus:
    """TODO"""
    def __init__(self, conn=None, node_id=None, job_result=None):
        if job_result is None:
            self.job_result = {}
        else:
            self.job_result = job_result
        self.conn = conn
        self.node_id = node_id
        self._job = None

    async def _get_job_status(self):
        """TODO"""
        params = {'mbpkgid': self.node_id,
                  'job_id': self.job_result['id']}
        result = await self.conn.connection(
            '/cloud/serverjob',
            data=params)
        return json.loads(result) # json.loads(result)

    async def status(self):
        """TODO"""
        if self._job is None:
            await self.refresh()
        return int(self._job['status'])

    async def job_id(self):
        """TODO"""
        if self._job is None:
            await self.refresh()
        return int(self._job.get('id', '0'))

    async def command(self):
        """TODO"""
        if self._job is None:
            await self.refresh()
        return self._job.get('command', '')

    async def inserted(self):
        """TODO"""
        if self._job is None:
            await self.refresh()
        return self._job.get('ts_insert', '0')

    async def is_success(self):
        """TODO"""
        if self._job is None:
            await self.refresh()
        return int(await self.status()) == 5

    async def is_working(self):
        """TODO"""
        if self._job is None:
            await self.refresh()
        return int(await self.status()) <= 3

    async def is_failure(self):
        """TODO"""
        if self._job is None:
            await self.refresh()
        return int(await self.status()) == 6

    async def refresh(self):
        """TODO"""
        self._job = await self._get_job_status()
        return self


# This is a closure that returns the request method below pre-configured
def connection(key, api_version):
    """TODO"""
    __key__ = key
    if api_version in ['v1', 'v1.1', 'v2']:
        root_url = 'https://{0}'.format(API_HOSTS[api_version])
    else:
        root_url = 'https://{0}'.format(API_HOSTS['v1'])

    async def request(url, data=None, method=None):
        if method is None:
            method = 'GET'
        if data is None:
            data = {}
        if not url.startswith('/'):
            url = '/{0}'.format(url)

        # build full url
        url_root = '{0}{1}?key={2}'.format(root_url, url, __key__)

        try:
            if method == 'GET':
                for key, val in data.items():
                    url_root = "{0}&{1}={2}".format(url_root, key, val)
                response = await get_path(url_root)
            elif method == 'POST':
                response = post_path(url_root, data=data)
        except aiohttp.ClientError:
            raise NetActuateException(
                response.status_code, response.content)

        return response

    return request


class NetActuateNodeDriver():
    """TODO"""
    name = 'NetActuate'
    website = 'http://www.netactuate.com'

    def __init__(self, key, api_version=None):
        if api_version is None:
            self.api_version = 'v1'
        else:
            self.api_version = api_version
        self.key = key
        self.connection = connection(
            self.key,
            api_version=api_version)


    async def locations(self):
        """Rewriting the dictionary into a list
        Also adding a key to each location named 'country'
        based off the name value
        """
        locs_resp = await self.connection('/cloud/locations/')
        locations = []
        locs_dict = json.loads(locs_resp)
        for loc_key in locs_dict:
            # just add the country from part of the name afer comma
            locs_dict[loc_key]['country'] = (
                locs_dict[loc_key]['name']
                .split(',')[1].replace(" ", "")
            )
            # put in list
            locations.append(locs_dict[loc_key])

        # update the response object so we can return it as a list
        # like other response objects. TODO: Update api to return a list
        # pylint: disable=protected-access
        return json.dumps(locations)

    async def os_list(self):
        """TODO"""
        return await self.connection('/cloud/images/')

    async def plans(self, location=False):
        """TODO"""
        if location:
            return await self.connection('/cloud/sizes/' + str(location))
        return await self.connection('/cloud/sizes/')

    async def servers(self, mbpkgid=False):
        """TODO"""
        if mbpkgid:
            return await self.connection('/cloud/server/' + str(mbpkgid))
        return await self.connection('/cloud/servers/')

    async def packages(self, mbpkgid=False):
        """TODO"""
        if mbpkgid:
            return await self.connection('/cloud/package/' + str(mbpkgid))
        return await self.connection('/cloud/packages')

    async def ipv4(self, mbpkgid):
        """TODO"""
        return await self.connection('/cloud/ipv4/' + str(mbpkgid))

    async def ipv6(self, mbpkgid):
        """TODO"""
        return await self.connection('/cloud/ipv6/' + str(mbpkgid))

    async def networkips(self, mbpkgid):
        """TODO"""
        return await self.connection('/cloud/networkips/' + str(mbpkgid))

    async def summary(self, mbpkgid):
        """TODO"""
        return await self.connection('/cloud/serversummary/' + str(mbpkgid))

    async def start(self, mbpkgid):
        """TODO"""
        return await self.connection(
            '/cloud/server/start/{0}'.format(mbpkgid), method='POST')

    async def shutdown(self, mbpkgid, force=False):
        """TODO"""
        params = {}
        if force:
            params['force'] = 1
        return await self.connection(
            '/cloud/server/shutdown/{0}'.format(mbpkgid), data=params, method='POST')

    async def reboot(self, mbpkgid, force=False):
        """TODO"""
        params = {}
        if force:
            params['force'] = 1
        return await self.connection(
            '/cloud/server/reboot/{0}'.format(mbpkgid), data=params,
            method='POST')

    async def rescue(self, mbpkgid, password):
        """TODO"""
        params = {'rescue_pass': str(password)}
        return await self.connection(
            '/cloud/server/start_rescue/{0}'.format(mbpkgid), data=params,
            method='POST')

    async def rescue_stop(self, mbpkgid):
        """TODO"""
        return await self.connection(
            '/cloud/server/stop_rescue/{0}'.format(mbpkgid), method='POST')

    # pylint: disable=too-many-arguments
    async def build(self, site, image, fqdn, passwd, mbpkgid):
        """TODO"""
        params = {'fqdn': fqdn, 'mbpkgid': mbpkgid,
                  'image': image, 'location': site,
                  'password': passwd}

        return await self.connection(
            '/cloud/server/build/', data=params, method='POST')

    async def delete(self, mbpkgid, extra_params=None):
        """TODO"""
        if extra_params is not None:
            extra_params['mbpkgid'] = mbpkgid
            return await self.connection(
                '/cloud/server/delete', data=extra_params, method='POST'
            )
        return await self.connection(
            '/cloud/server/delete/{0}'.format(mbpkgid), method='POST'
        )

    async def unlink(self, mbpkgid):
        """TODO"""
        return await self.connection(
            '/cloud/unlink/{0}'.format(mbpkgid), method='POST')

    async def status(self, mbpkgid):
        """TODO"""
        return await self.connection('/cloud/status/{0}'.format(mbpkgid))

    async def bandwidth_report(self, mbpkgid):
        """TODO"""
        return await self.connection('/cloud/servermonthlybw/' + str(mbpkgid))

    async def cancel(self, mbpkgid):
        """TODO"""
        return await self.connection(
            '/cloud/cancel/{0}'.format(mbpkgid), method='POST')

    async def buy(self, plan):
        """TODO"""
        return await self.connection('/cloud/buy/' + plan)

    async def buy_build(self, params):
        """TODO"""
        return await self.connection(
            '/cloud/buy_build/', data=params, method='POST')

    async def get_job(self, mbpkgid, job_id):
        """Gets all server jobs for this mbpkgid with the provided jobid

        TODO:   update get_job and get_jobs to be more explicit
                This will require an api change
        """
        params = {'job_id': job_id, 'mbpkgid': mbpkgid}
        return await self.connection('/cloud/serverjob/', data=params)

    async def get_jobs(self, mbpkgid):
        """Gets all server jobs for this mbpkgid

        TODO:   update get_job and get_jobs to be more explicit
                This will require an api change
        """
        params = {'mbpkgid': mbpkgid}
        return await self.connection('/cloud/serverjobs/', data=params)

    async def bgp_sessions(self, session_id=False):
        """
            Retrieve BGP session information
        """
        if session_id:
            return await self.connection('/cloud/bgpsession2/' + str(session_id))
        return await self.connection('/cloud/bgpsessions2')

    async def bgp_summary(self):
        """
            Retrieve BGP session summary
        """
        return await self.connection('/cloud/bgpsummary')

    async def bgp_create_sessions(self, mbpkgid, group_id, ipv6=True, redundant=False):
        """
            Build BGP sessions for a node in a given BGP group
        """
        params = { "group_id": group_id }
        if ipv6:
            params['ipv6'] = 1
        if redundant:
            params['redundant'] = 1
        return await self.connection(
            '/cloud/bgpcreatesessions/{0}'.format(mbpkgid), data=params, method='POST'
        )