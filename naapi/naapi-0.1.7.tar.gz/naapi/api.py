"""NetActuate API Python client library naapi

Author: Dennis Durling<djdtahoe@gmail.com>
"""
import json
import requests as rq

API_HOSTS = {
    'v1': 'vapi.netactuate.com',
}

class NetActuateException(Exception):
    """TODO"""
    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.args = (code, message)
        super(NetActuateException, self).__init__()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            "<NetActuateException in {0} : {1}>"
            .format(self.code, self.message)
        )

def connection(key, api_version):
    """TODO"""
    __key__ = key
    if api_version in API_HOSTS.keys():
        root_url = 'https://{0}'.format(API_HOSTS[api_version])
    else:
        root_url = 'https://{0}'.format(API_HOSTS['v1'])

    def request(url, data=None, method=None):
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
                for key, value in data.items():
                    url_root = "{0}&{1}={2}".format(url_root, key, value)
                response = rq.get(url_root)
            elif method == 'POST':
                response = rq.post(url_root, json=data)
        except rq.HTTPError:
            raise NetActuateException(
                response.status_code, response.content)

        return response

    return request

# pylint: disable=too-many-public-methods
class NetActuateNodeDriver():
    """Todo"""
    name = 'NetActuate'
    website = 'http://www.netactuate.com'

    def __init__(self, key, api_version=None):
        if api_version is None:
            self.api_version = 'v1'
        else:
            self.api_version = api_version
        self.key = key
        self.connection = connection(self.key, api_version=api_version)

    def locations(self):
        """Rewriting the dictionary into a list
        Also adding a key to each location named 'country'
        based off the name value
        """
        locs_resp = self.connection('/cloud/locations/')
        locations = []
        locs_dict = locs_resp.json()

        # If we received an error pass it up now for handling
        if 'error' in locs_dict:
            if 'msg' in locs_dict:
                return locs_dict

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
        locs_resp._content = json.dumps(locations).encode()
        return locs_resp

    def os_list(self):
        """Todo"""
        return self.connection('/cloud/images/')

    def plans(self, location=False):
        """Todo"""
        if location:
            return self.connection('/cloud/sizes/' + str(location))
        return self.connection('/cloud/sizes/')

    def servers(self, mbpkgid=False):
        """Todo"""
        if mbpkgid:
            return self.connection('/cloud/server/' + str(mbpkgid))
        return self.connection('/cloud/servers/')

    def packages(self, mbpkgid=False):
        """Todo"""
        if mbpkgid:
            return self.connection('/cloud/package/' + str(mbpkgid))
        return self.connection('/cloud/packages')

    def ipv4(self, mbpkgid):
        """Todo"""
        return self.connection('/cloud/ipv4/' + str(mbpkgid))

    def ipv6(self, mbpkgid):
        """Todo"""
        return self.connection('/cloud/ipv6/' + str(mbpkgid))

    def networkips(self, mbpkgid):
        """Todo"""
        return self.connection('/cloud/networkips/' + str(mbpkgid))

    def summary(self, mbpkgid):
        """Todo"""
        return self.connection('/cloud/serversummary/' + str(mbpkgid))

    def start(self, mbpkgid):
        """Todo"""
        return self.connection(
            '/cloud/server/start/{0}'.format(mbpkgid), method='POST')

    def shutdown(self, mbpkgid, force=False):
        """Todo"""
        params = {}
        if force:
            params['force'] = 1
        return self.connection(
            '/cloud/server/shutdown/{0}'.format(mbpkgid), data=params, method='POST')

    def reboot(self, mbpkgid, force=False):
        """Todo"""
        params = {}
        if force:
            params['force'] = 1
        return self.connection(
            '/cloud/server/reboot/{0}'.format(mbpkgid), data=params,
            method='POST')

    def rescue(self, mbpkgid, password):
        """Todo"""
        params = {'rescue_pass': str(password)}
        return self.connection(
            '/cloud/server/start_rescue/{0}'.format(mbpkgid), data=params,
            method='POST')

    def rescue_stop(self, mbpkgid):
        """Todo"""
        return self.connection(
            '/cloud/server/stop_rescue/{0}'.format(mbpkgid), method='POST')

    # pylint: disable=too-many-arguments
    def build(self, site, image, fqdn, passwd, mbpkgid):
        """Todo"""
        params = {'fqdn': fqdn, 'mbpkgid': mbpkgid,
                  'image': image, 'location': site,
                  'password': passwd}

        return self.connection(
            '/cloud/server/build/', data=params, method='POST')

    def delete(self, mbpkgid, extra_params=None):
        """Delete the vm
        If extra_params which defaults to cancel_billing=False
        add mbpkgid to extra_params and pass params, otherwise
        pass just the url with the mbpkgid
        Ansible role 'node.py' passes cancel_billing by default
        """
        if extra_params is not None:
            extra_params['mbpkgid'] = mbpkgid
            return self.connection(
                '/cloud/server/delete/{0}'.format(mbpkgid), data=extra_params, method='POST'
            )
        return self.connection(
            '/cloud/server/delete/{0}'.format(mbpkgid), method='POST'
        )

    def unlink(self, mbpkgid):
        """Todo"""
        return self.connection(
            '/cloud/unlink/{0}'.format(mbpkgid), method='POST')

    def status(self, mbpkgid):
        """Todo"""
        return self.connection('/cloud/status/{0}'.format(mbpkgid))

    def bandwidth_report(self, mbpkgid):
        """Todo"""
        return self.connection('/cloud/servermonthlybw/' + str(mbpkgid))

    def cancel(self, mbpkgid):
        """Todo"""
        return self.connection(
            '/cloud/cancel/{0}'.format(mbpkgid), method='POST'
        )

    def buy(self, plan):
        """Todo"""
        return self.connection('/cloud/buy/' + plan)

    def buy_build(self, params):
        """Todo"""
        return self.connection(
            '/cloud/buy_build/', data=params, method='POST'
        )

    def get_job(self, mbpkgid, job_id):
        """Gets all server jobs for this mbpkgid with the provided jobid

        TODO:   update get_job and get_jobs to be more explicit
                This will require an api change
        """
        params = {'job_id': job_id, 'mbpkgid': mbpkgid}
        return self.connection('/cloud/serverjob/', data=params)

    def get_jobs(self, mbpkgid):
        """Gets all server jobs for this mbpkgid

        TODO:   update get_job and get_jobs to be more explicit
                This will require an api change
        """
        params = {'mbpkgid': mbpkgid}
        return self.connection('/cloud/serverjobs/', data=params)

    def bgp_sessions(self, session_id=False):
        """
            Retrieve BGP session information
        """
        if session_id:
            return self.connection('/cloud/bgpsession2/' + str(session_id))
        return self.connection('/cloud/bgpsessions2')

    def bgp_summary(self):
        """
            Retrieve BGP session summary
        """
        return self.connection('/cloud/bgpsummary')

    def bgp_create_sessions(self, mbpkgid, group_id, ipv6=True, redundant=False):
        """
            Build BGP sessions for a node in a given BGP group
        """
        params = { "group_id": group_id }
        if ipv6:
            params['ipv6'] = 1
        if redundant:
            params['redundant'] = 1
        return self.connection(
            '/cloud/bgpcreatesessions/{0}'.format(mbpkgid), data=params, method='POST'
        )