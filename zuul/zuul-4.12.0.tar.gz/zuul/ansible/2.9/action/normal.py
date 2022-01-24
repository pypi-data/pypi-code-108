# Copyright 2017 Red Hat, Inc.
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

from ansible.errors import AnsibleError

from zuul.ansible import paths
normal = paths._import_ansible_action_plugin('normal')


class ActionModule(normal.ActionModule):
    '''Override the normal action plugin

    :py:class:`ansible.plugins.normal.ActionModule` is run for every
    module that does not have a more specific matching action plugin.

    Our overridden version of it wraps the execution with checks to block
    undesired actions on localhost.
    '''

    def run(self, tmp=None, task_vars=None):
        '''Overridden primary method from the base class.'''

        if paths._is_localhost_task(self):
            if not self.dispatch_handler():
                raise AnsibleError("Executing local code is prohibited")
        return super(ActionModule, self).run(tmp, task_vars)

    def dispatch_handler(self):
        '''Run per-action handler if one exists.'''
        handler_name = 'handle_{action}'.format(action=self._task.action)
        handler = getattr(self, handler_name, None)
        if handler:
            paths._fail_if_local_module(self)
            handler()
            return True
        return False

    def handle_zuul_return(self):
        '''Allow zuul_return module on localhost.'''
        pass

    def handle_stat(self):
        '''Allow stat module on localhost if it doesn't touch unsafe files.

        The :ansible:module:`stat` can be useful in jobs for manipulating logs
        and artifacts.

        Block any access of files outside the zuul work dir.
        '''
        if self._task.args.get('get_mime'):
            raise AnsibleError("get_mime on localhost is forbidden")
        paths._fail_if_unsafe(self._task.args['path'])

    def handle_file(self):
        '''Allow file module on localhost if it doesn't touch unsafe files.

        The :ansible:module:`file` can be useful in jobs for manipulating logs
        and artifacts.

        Block any access of files outside the zuul work dir.
        '''
        for arg in ('path', 'dest', 'name'):
            dest = self._task.args.get(arg)
            if dest:
                paths._fail_if_unsafe(dest)

    def handle_known_hosts(self):
        '''Allow known_hosts on localhost

        The :ansible:module:`known_hosts` can be used to add SSH host keys of
        a remote system. When run from a executor it can be used with the
        add_host task to access remote servers. This is needed because ansible
        on the executor is configured to check host keys by default.

        Block any access of files outside the zuul work dir.
        '''
        if paths._is_localhost_task(self):
            path = self._task.args.get('path')
            if path:
                paths._fail_if_unsafe(path)

    def handle_k8s(self):
        '''Allow k8s module on localhost if it doesn't touch unsafe files.

        The :ansible:module:`k8s` can be used from the executor to modify
        k8s resources.  Several options refer to local paths; check that
        they are constrained to the work dir.
        '''
        for arg in ('src', 'ca_cert', 'client_cert',
                    'client_key', 'kubeconfig'):
            path = self._task.args.get(arg)
            if path:
                paths._fail_if_unsafe(path)

    def handle_find(self):
        '''Allow find module on localhost if it doesn't traverse unsafe files.

        The :ansible:module:`find` can be used from the executor to
        gather a list of files.
        '''
        find_paths = self._task.args.get('paths')
        if not isinstance(find_paths, list):
            find_paths = (find_paths,)
        for path in find_paths:
            paths._fail_if_unsafe(path)
