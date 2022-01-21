from pydantic import ValidationError

from net_models.models import IosLineConfig
from tests.BaseTestClass import TestBaseNetModel, TestVendorIndependentBase



class TestIosLineConfig(TestVendorIndependentBase):

    TEST_CLASS = IosLineConfig
    RESOURCE_DIR = TestVendorIndependentBase.RESOURCE_DIR.joinpath("line").joinpath("cisco_ios")

if __name__ == '__main__':
    unittest.main()



