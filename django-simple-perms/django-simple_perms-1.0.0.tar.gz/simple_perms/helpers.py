# -*- coding: utf-8 -*-


class AssertPermissions:
    """
    Class for testing permissions

    :Example:

    >>> permissions = [
    >>>     { 'usr': 'admin', 'perm': 'contracts.can_use_contracts_ui', 'args': (None,),           'result': True, },
    >>>     { 'usr': 'admin', 'perm': 'contracts.add',                  'args': (None,),           'result': True, },
    >>>     { 'usr': 'admin', 'perm': 'contracts.view',                 'args': (self.contract, ), 'result': True, },
    >>>     { 'usr': 'admin', 'perm': 'contracts.change',               'args': (self.contract, ), 'result': True, },
    >>> ]
    >>> self.assertPerms(permissions)

    Where:
    usr is a class attribute of self.
    """
    __exceptions__ = []

    def assertPerms(self, permissions):
        """
        Test if permissions are correct given to the dict of permissions
        """
        self.__exceptions__ = []

        for permission in permissions:
            self._test_permission_(permission)

        if self.__exceptions__:
            e = self.__exceptions__[0]
            for ex in self.__exceptions__[1:]:
                e.args = e.args + ex.args

            raise e

    def _test_permission_(self, permission):
        """
        Test if permission is correct. 
        Raise AssertionError if result is not correct.

        >>> ======================================================================
        >>> FAIL: test_permissions_of_team_leader (contracts.tests.perms.TestContractPermission)
        >>> ----------------------------------------------------------------------
        >>> Traceback (most recent call last):
        >>>   File "/app/django/contracts/tests/perms.py", line 138, in test_permissions_of_team_leader
        >>>     self.assertPerms(permissions)
        >>>   File "/app/django/contracts/tests/perms.py", line 18, in assertPerms
        >>>     self._test_permission_(permission)
        >>>   File "/app/django/contracts/tests/perms.py", line 36, in _test_permission_
        >>>     raise e
        >>>   File "/app/django/contracts/tests/perms.py", line 31, in _test_permission_
        >>>     getattr(self, permission['usr']).has_perm(permission['perm'], *permission['args'])
        >>> AssertionError: ('False is not true', 'PERM ERROR user:team_leader perm:contracts.view - attended: True')

        """
        if permission['result']:
            action = self.assertTrue
        else:
            action = self.assertFalse

        try:
            action(
                getattr(self, permission['usr']).has_perm(permission['perm'], *permission['args'])
            )
        except Exception as e:
            my_err = f"PERM ERROR user:{permission['usr']} perm:{permission['perm']} args:{permission['args']}: "
            e.args = (f'{my_err}', )
            self.__exceptions__.append(e)
