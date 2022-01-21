import os
import unittest
import numpy as np

class BaseForTests(unittest.TestCase):
    ''' Base class for tests '''
    def setUp(self):
        # get test_forecast_dir from environment
        # TODO use this again - currently disabled to distinguish
        # old and new results formats
        if 'TEST_DATA_DIR' not in os.environ:
            raise ValueError('TEST_DATA_DIR is not defined. It should point to example data.')
        self.test_data_dir = os.environ['TEST_DATA_DIR']

        if not os.path.exists(self.test_data_dir):
            raise ValueError('Test data directory %s does not exist' % self.test_data_dir)
        
        self.mppfile = os.path.join(self.test_data_dir, 'NpsNextsim.mpp')

    def set_envs(self, new_envs):
        """
        temporarily change os.environ variables
        Parameters:
        -----------
        new_envs : dict
            keys are the variables to change, values are the new values

        Returns:
        --------
        old_envs : dict
            keys are the variables that were changed, values are the old values
        del_envs : list
            environment variables that did not exist before now

        To reset the variables later call:
        * self.set_envs(old_envs)
        * self.del_envs(del_envs)
        """
        del_envs = []
        old_envs = {}
        for env in new_envs:
            if env not in os.environ:
                del_envs.append(env)
            else:
                old_envs[env] = os.environ[env]
        for env in new_envs:
            os.environ[env] = new_envs[env]
        return old_envs, del_envs

    def del_envs(self, env_list):
        for env in env_list:
            del(os.environ[env])


    def arrays_equal(self, a1, a2, **kwargs):
        '''
        test if 2 arrays are equal

        Parameters:
        -----------
        a1, a2: numpy arrays
        kwargs for self.values_equal
        '''

        # should have same shape
        if a1.shape != a2.shape:
            return False

        # NB values_equal says np.nan == np.nan gives True
        iseq = [self.values_equal(v1, v2, **kwargs) for v1, v2 in zip(a1, a2)]
        return np.all(iseq)

    def values_equal(self, a1, a2, **kwargs):
        '''
        Parameters:
        -----------
        a1, a2 : numbers or numpy.arrays
            can have np.array as values
        kwargs for floats_equal

        Returns:
        --------
        is_equal : bool
            True if equal
        '''
        if type(a1) != type(a2):
            types = {type(a1), type(a2)}
            if types in [
                    {float, int},
                    {np.float64, np.int64},
                    ]:
                return self.floats_equal(a1, a2, **kwargs)
            else:
                return False
        if type(a1) == np.ndarray:
            return self.arrays_equal(a1, a2, **kwargs)
        if isinstance(a1, list):
            return self.lists_equal(a1, a2, **kwargs)
        if isinstance(a1, float) or isinstance(a1, int):
            return self.floats_equal(a1, a2, **kwargs)
        return a1==a2

    def floats_equal(self, a1, a2, tol=1e-12, **kwargs):
        '''
        Parameters:
        -----------
        a1, a2 : float or int
        tol : float
            used with np.array or float types
        dummy kwargs

        Returns:
        --------
        bool (True if equal)
          - NB we define np.nan equal to np.nan
        '''
        nans = [np.isnan(a1), np.isnan(a2)]
        if np.all(nans):
            return True
        if np.any(nans):
            return False
        return np.abs(a1-a2)<=tol

    def lists_equal(self, a1, a2, **kwargs):
        '''
        Parameters:
        -----------
        a1, a2 : list
            can have np.array as elements
        kwargs for self.values_equal

        Returns:
        --------
        * bool (True if equal)
        '''
        if len(a1) != len(a2):
            return False
        for v1, v2 in zip(a1, a2):
            if not self.values_equal(v1, v2, **kwargs):
                return False
        return True

    def dicts_equal(self, a1, a2, **kwargs):
        '''
        Parameters:
        -----------
        a1, a2 : dict
            can have np.array as values
        kwargs for self.values_equal

        Returns:
        -----------
        is_equal : bool
            True if equal
        '''
        # same keys?
        if sorted(list(a1)) != sorted(list(a2)):
            return False
        # same values?
        for kw, v1 in a1.items():
            v2 = a2[kw]
            if not self.values_equal(v1, v2, **kwargs):
                return False
        return True

    def args_equal(self, a1, a2, **kwargs):
        '''
        Parameters:
        -----------
        a1, a2 (most things with == operator)
          - includes dicts/lists with np.array's as values
        kwargs: 'tol' for agreement within a tolerance
            (used with np.array or float types)

        Returns:
        --------
        is_equal: bool
            True if equal
        '''
        if type(a1) != type(a2):
            return False
        if isinstance(a1, list):
            return self.lists_equal(a1, a2, **kwargs)
        elif isinstance(a1, dict):
            return self.dicts_equal(a1, a2, **kwargs)
        else:
            return self.values_equal(a1, a2, **kwargs)

    def calls_equal(self, actual_call, call_req, **kwargs):
        """
        Parameters:
        -----------
        actual_call, call_req: mock.call
        kwargs for self.args_equal

        Returns:
        --------
        is_equal: bool
            True if equal
        """
        # check args
        if not self.lists_equal(actual_call[1], call_req[1], **kwargs):
            return False
        # check kwargs
        if not self.dicts_equal(actual_call[2], call_req[2], **kwargs):
            return False
        return True

    def list_contains_call(self, clist, c1):
        """
        Parameters:
        -----------
        call_list : list
            list of mock.call objects
        call : mock.call
            , call_req: mock.call
        kwargs for self.args_equal


        Returns:
        --------
        in_list: bool
            True if call is in call_list
        index: int
            index in call_list corresponding to call
        """
        for i, c2 in enumerate(clist):
            if self.calls_equal(c1, c2):
                return True, i
        return False, None

    def call_lists_equal(self, cl1, cl2, **kwargs):
        """
        Parameters:
        -----------
        call_list1, call_list2 : list
            lists of mock.call objects
        kwargs for self.calls_equal


        Returns:
        --------
        is_equal: bool
            True if call lists have the same calls in the same order
        """
        if len(cl1) != len(cl2):
            return False
        for c1, c2 in zip(cl1, cl2):
            if not self.calls_equal(c1, c2, **kwargs):
                return False
        return True

    def assert_dict_of_arrays_equal(self , d1, d2, **kwargs):
        '''
        assert 2 dictionarys are equal when they contain numpy arrays

        Parameters:
        -----------
        d1, d2: 2 dictionaries containing numpy arrays of same size for each value
        '''
        if not self.args_equal(d1, d2, **kwargs):
            print('Dicts not equal:')
            print(d1)
            print(d2)
            raise AssertionError('Dicts not equal')

    def assert_arrays_equal(self , a1, a2, **kwargs):
        '''
        assert 2 arrays are equal

        Parameters:
        -----------
        a1, a2: numpy.array
        tol : float
            tolerance for each element
        '''
        if not self.arrays_equal(a1, a2, **kwargs):
            print('Arrays not equal:')
            print(a1)
            print(a2)
            raise AssertionError('Arrays not equal')

    def assert_dicts_equal(self , a1, a2, **kwargs):
        '''
        assert 2 arrays are equal

        Parameters:
        -----------
        a1, a2: dict
        kwargs for values_equal or floats_equal
        '''
        if not self.dicts_equal(a1, a2, **kwargs):
            print('Dicts not equal:')
            print(a1)
            print(a2)
            raise AssertionError('Dicts not equal')

    def assert_lists_equal(self, l1, l2, **kwargs):
        '''
        like self.assertEqual(l1, l2),
        but asserts ordering is correct too

        Parameters:
        -----------
        l1, l2: list
        kwargs for self.lists_equal
        '''
        if not self.lists_equal(l1, l2, **kwargs):
            print('lists not equal:')
            print(l1)
            print(l2)
            raise AssertionError('lists not equal')


    def assert_mock_has_calls(self, mock_fun, calls_req,
            any_order=False, **kwargs):
        '''
        like MagicMock().assert_has_calls(calls_req, **kwargs),
        but when arguments can be np.array's

        Parameters:
        -----------
        mock_fun : MagicMock
        calls_req : list
            list of calls we expect mock_fun to have

        Raises:
        -------
        Assertion error if condition is not satisfied
        '''

        actual_calls = list(mock_fun.mock_calls) # copy
        print('Actual calls:')
        print(actual_calls)
        print('Expected calls:')
        print(calls_req)
        if not any_order:
            self.assertTrue(self.call_lists_equal(
                actual_calls,
                calls_req,
                **kwargs))
        else:
            inds = []
            for c1 in calls_req:
                inlist, i = self.list_contains_call(actual_calls, c1)
                self.assertTrue(inlist)
                inds.append(i)
            self.assertEqual(
                    sorted(inds),
                    list(range(len(actual_calls))),
                    )

    def assert_ascending(self, lst):
        '''assert a list is ascending'''
        for i, it in enumerate(lst):
            if i>0:
                self.assertTrue(it>lst[i-1])

    def assert_descending(self, lst):
        '''assert a list is ascending'''
        for i, it in enumerate(lst):
            if i>0:
                self.assertTrue(it<lst[i-1])
