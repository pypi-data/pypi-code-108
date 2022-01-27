import pytest

from sym.sdk.templates import ApprovalTemplate, Template


class TestTemplates:
    def test_approval(self):
        with pytest.raises(TypeError, match="Can't instantiate abstract class ApprovalTemplate"):
            ApprovalTemplate("sym:template:approval:1.0.0")

    def test_abstract_base(self):
        with pytest.raises(TypeError):
            Template()
