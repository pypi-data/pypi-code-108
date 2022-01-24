from tests.BaseTestClass import TestVendorIndependentBase
from net_models.models import (
    PseudowireLoadBalancing,
    PseudowireEncapsulation,
    PseudowireClass,
    PseudowireNeighbor,
    PseudowireBackupNeighbor,
    Pseudowire,
    XConnectGroup
)




class TestPseudowireFlowLabel(TestVendorIndependentBase):

    TEST_CLASS = PseudowireClass


class TestPseudowireLoadBalancing(TestVendorIndependentBase):

    TEST_CLASS = PseudowireLoadBalancing


class TestPseudowireEncapsulation(TestVendorIndependentBase):

    TEST_CLASS = PseudowireEncapsulation

class TestPseudowireClass(TestVendorIndependentBase):

    TEST_CLASS = PseudowireClass


class TestPseudowire(TestVendorIndependentBase):

    TEST_CLASS = Pseudowire


class TestPseudowireNeighbor(TestVendorIndependentBase):

    TEST_CLASS = PseudowireNeighbor


class TestPseudowireBackupNeighbor(TestVendorIndependentBase):

    TEST_CLASS = PseudowireBackupNeighbor


class TestXConnectGroup(TestVendorIndependentBase):

    TEST_CLASS = XConnectGroup

if __name__ == '__main__':
    unittest.main()