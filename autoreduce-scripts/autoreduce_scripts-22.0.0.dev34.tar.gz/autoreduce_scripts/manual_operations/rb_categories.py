from enum import Enum


class RBCategory(Enum):
    DIRECT_ACCESS = "direct_access"
    RAPID_ACCESS = "rapid_access"
    COMMISSIONING = "commissioning"
    CALIBRATION = "calibration"
    INDUSTRIAL_ACCESS = "industrial_access"
    INTERNATIONAL_PARTNERS = "international_partners"
    XPESS_ACCESS = "xpess_access"
    UNCATEGORIZED = "uncategorized"
