from Cryptodome.PublicKey import RSA

from spell.cli.integration_tests.testing_utils import verify_exit_code, parse_raw


class TestKeys:
    def test_keys(self, run):
        # verify auto-generated key is on the server
        result = run(["keys", "list", "--raw"])
        verify_exit_code(result, 0)
        vals = parse_raw(result.stdout)
        assert len(vals) == 1
        assert "Spell CLI" in vals[0][0]

    def test_add_key(self, tmpdir, run):
        # find the number of keys on the server
        result = run(["keys", "list", "--raw"])
        verify_exit_code(result, 0)
        vals = parse_raw(result.stdout)
        num_keys = len(vals)
        # generate a new key
        key = RSA.generate(1024).exportKey("OpenSSH")
        key_title = "new_key1"
        f = tmpdir.join(".spell", key_title)
        f.ensure()
        f.write(key)
        # add the key
        result = run(["keys", "add", "-f", f.strpath, "-t", key_title])
        verify_exit_code(result, 0)
        result = run(["keys", "list", "--raw"])
        verify_exit_code(result, 0)
        vals = parse_raw(result.stdout)
        # verify the new key is on the server
        assert key_title in [x[0] for x in vals]
        # verify the numnber of keys increased by 1
        assert len(vals) == num_keys + 1

    def test_remove_key(self, tmpdir, run):
        # generate a new key
        key = RSA.generate(1024).exportKey("OpenSSH")
        key_title = "new_key2"
        f = tmpdir.join(".spell", key_title)
        f.ensure()
        f.write(key)
        # add the key
        result = run(["keys", "add", "-f", f.strpath, "-t", key_title])
        verify_exit_code(result, 0)
        result = run(["keys", "list", "--raw"])
        verify_exit_code(result, 0)
        vals = parse_raw(result.stdout)
        num_keys = len(vals)
        # verify the new key is on the server
        assert key_title in [x[0] for x in vals]
        # remove the key
        result = run(["keys", "rm", key_title])
        verify_exit_code(result, 0)
        result = run(
            ["keys", "list", "--raw"],
        )
        verify_exit_code(result, 0)
        vals = parse_raw(result.stdout)
        # verify the new key is not on the server anymore
        assert key_title not in [x[0] for x in vals]
        # verify the number of keys decreased by 1
        assert len(vals) == num_keys - 1
