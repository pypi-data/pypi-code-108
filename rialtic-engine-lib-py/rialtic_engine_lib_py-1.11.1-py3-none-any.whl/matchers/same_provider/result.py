from enum import Enum, unique


@unique
class SameProviderResult(str, Enum):
    Facility = "Facility Provider"
    SameRendering = "Same Rendering Provider"
    Different = "Different Provider"
    Partial400N = "Different Rendering Providers with same Billing NPI and unknown Specialty"
    Partial600Y = "Different Rendering Providers with same Billing NPI and Specialty"
    Partial600N = "Different Rendering Providers with same Billing NPI and different Specialty"
    Partial700N = "Different Rendering and Billing Providers with same TaxID and unknown Specialty"
    Partial800Y = "Different Rendering and Billing Providers with same TaxID and Specialty"
    Partial800N = "Different Rendering and Billing Providers with same TaxID and different Specialty"
    Error = "Error"
