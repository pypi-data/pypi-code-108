from burlap.files import file # pylint: disable=redefined-builtin
from burlap.tests.functional_tests.base import TestCase
from burlap.common import Satchel

is_file = file.is_file

class _TestSatchel(Satchel):

    name = 'test'

    def configure(self):
        pass

class CommonTests(TestCase):

    def get_test_satchel(self):
        test = _TestSatchel()
        test.genv.hosts = ['localhost']
        test.genv.host_string = test.genv.hosts[0]
        return test

    def test_dryrun(self):

        test = self.get_test_satchel()

        test.dryrun = True
        test.run('touch ~/abc.txt')
        assert not is_file('~/abc.txt')

        test.dryrun = 1
        test.run('touch ~/def.txt')
        assert not is_file('~/def.txt')

        test.dryrun = False
        test.run('touch ~/mno.txt')
        assert not is_file('~/mno.txt')
        test.run('rm -f ~/mno.txt')

        test.dryrun = 0
        test.run('touch ~/xyz.txt')
        assert not is_file('~/xyz.txt')
        test.run('rm -f ~/xyz.txt')

    def test_sudo(self):

        test = self.get_test_satchel()

        all_users = test.run('cut -d: -f1 /etc/passwd')
        print('all users:', all_users)

        ret = (test.sudo('whoami') or '').split('\n')[-1]
        print('ret0:', ret)
        self.assertEqual(ret, 'root')

        if 'travis' in all_users:
            target_user = 'travis'
        else:
            target_user = 'www-data'
        ret = (test.sudo('whoami', user=target_user) or '').split('\n')[-1]
        print('ret1:', ret)
        self.assertEqual(ret, target_user)
