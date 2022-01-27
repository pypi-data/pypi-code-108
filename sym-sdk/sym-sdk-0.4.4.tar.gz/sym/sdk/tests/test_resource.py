import pytest

from sym.sdk.resource import (
    SRN,
    InvalidSlugError,
    InvalidSRNError,
    MultipleErrors,
    TrailingSeparatorError,
)


class TestResource:
    def test_sym_resource_fails_on_malformed_srn(self):
        self._test_bad("foo", InvalidSRNError)
        self._test_bad("foo:bar", InvalidSRNError)
        self._test_bad("foo:bar:baz", InvalidSRNError)
        self._test_bad("foo:bar:baz:boz", InvalidSRNError)
        self._test_bad("foo:bar:baz:lates:", TrailingSeparatorError, match="trailing separator.")
        self._test_bad("foo:bar:baz:1.0:", InvalidSRNError)
        self._test_bad("foo:bar:baz:1.0.0::", InvalidSRNError)
        self._test_bad("foo:bar:baz:latest:1.0.0:", TrailingSeparatorError)
        self._test_bad("foo:bar:baz:1.3000.0:something", InvalidSRNError)
        self._test_bad("foo:bar:baz::something", InvalidSRNError)
        self._test_bad("foo:bar:baz:latestsomething", InvalidSRNError)
        self._test_bad("foo:bar:baz:latest:", TrailingSeparatorError)
        self._test_bad("foo!foobar:bar:baz:latest:foo", InvalidSlugError, match="org")
        self._test_bad("sym:flow:something::", InvalidSRNError)
        self._test_bad("foo!foobar:bar:baz:1000.0.2000:foo", MultipleErrors, match="version")

    def _test_bad(self, srn, exc, match: str = None):
        if match:
            with pytest.raises(exc, match=match):
                SRN.parse(srn)
        else:
            with pytest.raises(exc):
                SRN.parse(srn)

    def test_sym_srn_succeeds_on_valid_srn(self):
        self._test_good("sym:foo-bar:12345-11233:0.1.0:stuff")
        self._test_good("foo:bar:baz:1.300.0:something")
        self._test_good("foo:bar:baz:latest")
        self._test_good("foo_foo:bar:baz:latest")
        self._test_good("sym:template:approval:1.0.0")
        self._test_good("sym:template:approval:1.0.0:e97af6b3-0249-4855-971f-4e1dd188773a")

    def _test_good(self, raw):
        SRN.parse(raw)

    def test_srn_copy_should_succeed_without_identifier(self):
        srn_string = "foo:bar:baz:1.0.0"

        srn = SRN.parse(srn_string)

        assert str(srn.copy(version="latest")) == "foo:bar:baz:latest"
        assert str(srn.copy(organization="myorg")) == "myorg:bar:baz:1.0.0"

    def test_srn_str_should_produce_an_identical_srn(self):
        text = "sym:template:approval:1.0.0"
        srn = SRN.parse(text)

        srn_str = str(srn)
        srn2 = SRN.parse(srn_str)

        assert srn == srn2
        assert str(srn) == str(srn2)
        assert text == srn_str
