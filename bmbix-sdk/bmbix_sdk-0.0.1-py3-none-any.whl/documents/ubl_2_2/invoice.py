from datetime import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from uuid import UUID
    from datetime import datetime

import attr
from dateparser import parse  # type: ignore
from lxml.builder import ElementMaker  # type: ignore
from lxml import etree

BRI = str

cac = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"  # noqa
cbc = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
inv = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
rdr = "urn:oasis:names:specification:ubl:schema:xsd:Reminder-2"
TOP_NSMAP = {"cac": cac, "cbc": cbc, "rdr": rdr, "inv": inv}

CAC = ElementMaker(
    namespace=cac,
    nsmap={"cac": cac},
)
CBC = ElementMaker(
    namespace=cbc,
    nsmap={"cbc": cbc},
)
INV = ElementMaker(
    namespace=inv,
    nsmap={None: inv},
)
RDR = ElementMaker(
    namespace=rdr,
    nsmap={None: rdr},
)


@attr.s
class PostalAddress:
    street_name = attr.ib(default="")
    building_name = attr.ib(default="")
    building_number = attr.ib(default="")
    city_name = attr.ib(default="")
    postal_zone = attr.ib(default="")
    country_subentity = attr.ib(default="")
    address_line = attr.ib(default="")
    country_identification_code = attr.ib(default="")

    def xml(self):
        element = CAC.PostalAddress(
            CBC.StreetName(self.street_name),
            CBC.BuildingName(self.building_name),
            CBC.BuildingNumber(self.building_number),
            CBC.CityName(self.city_name),
            CBC.PostalZone(self.postal_zone),
            CBC.CountrySubentity(self.country_subentity),
            CAC.AddressLine(
                CBC.Line(self.address_line)
            ),
            CAC.Country(
                CBC.IdentificationCode(self.country_identification_code)
            ),
        )
        return element


@attr.s
class PartyLegalEntity:
    registration_name = attr.ib(default=None)
    company_id = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.registration_name_element = \
            CBC.RegistrationName(self.registration_name) \
            if self.registration_name else ""
        self.company_id_element = \
            CBC.CompanyID(self.company_id) if self.company_id else ""

    def xml(self):
        return CAC.PartyLegalEntity(
            self.registration_name_element,
            self.company_id_element,
        )


@attr.s
class PartyTaxScheme:
    registration_name = attr.ib(default=None)
    company_id = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.registration_name_element = \
            CBC.RegistrationName(self.registration_name) \
            if self.registration_name else ""
        self.company_id_element = \
            CBC.CompanyID(self.company_id) if self.company_id else ""

    def xml(self):
        return CAC.PartyTaxScheme(
            self.registration_name_element,
            self.company_id_element,
            CAC.TaxScheme(),
        )


@attr.s
class Party:
    party_id: BRI = attr.ib(default=None)
    party_name: str = attr.ib(default=None)
    postal_address: PostalAddress = attr.ib(default=None)
    party_tax_scheme: PartyTaxScheme = attr.ib(default=None)
    party_legal_entity: PartyLegalEntity = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.postal_address_element = \
            self.postal_address.xml() if self.postal_address else ""
        self.party_tax_scheme_element = \
            self.party_tax_scheme.xml() if self.party_tax_scheme else ""
        self.party_legal_entity_element = \
            self.party_legal_entity.xml() if self.party_legal_entity else ""

    def xml(self):
        element = CAC.Party(
            CAC.PartyIdentification(
                CBC.ID(self.party_id, schemeID="bmbix")
            ),
            CAC.PartyName(
                CBC.Name(self.party_name)
            ),
            self.postal_address_element,
            self.party_tax_scheme_element,
            self.party_legal_entity_element,
        )
        return element


@attr.s
class AccountingSupplierParty:
    party: Party = attr.ib(default=None)

    def xml(self):
        element = CAC.AccountingSupplierParty(
            self.party.xml()
        )
        return element


@attr.s
class AccountingCustomerParty:
    supplier_assigned_account_id = attr.ib(default=None)
    party: Party = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.supplier_assigned_account_id_element = \
            CBC.SupplierAssignedAccountID(self.supplier_assigned_account_id) \
            if self.supplier_assigned_account_id else ""

    def xml(self):
        element = CAC.AccountingCustomerParty(
            self.supplier_assigned_account_id_element,
            self.party.xml(),
        )
        return element


@attr.s
class PayableAmount:
    amount: str = attr.ib(default=None)
    currency_id: str = attr.ib(default=None)

    def xml(self):
        element = CBC.PayableAmount(
            self.amount, currencyID=self.currency_id
        )
        return element


@attr.s
class TaxTotal:
    tax_type: str = attr.ib(default=None)
    tax_amount: str = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.tax_amount_element = \
            CBC.TaxAmount(
                self.tax_amount, currencyID="GBP") if self.tax_amount else ""

        self.tax_name_element = \
            CBC.Name(self.tax_type) if self.tax_type else ""

    def xml(self):
        element = CAC.TaxTotal(
            self.tax_amount_element,
            CAC.TaxSubtotal(
                CBC.TaxAmount(self.tax_amount, currencyID="GBP"),
                CAC.TaxCategory(
                    self.tax_name_element,
                    CAC.TaxScheme()
                ),
            ),
        )
        return element


@attr.s
class LegalMonetaryTotal:
    payable_amount: PayableAmount = attr.ib(default=None)
    allowance_total_amount: str = attr.ib(default=None)
    line_extension_amount: str = attr.ib(default=None)
    tax_exclusive_amount: str = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.tax_exclusive_amount_element = CBC.TaxExclusiveAmount(
            self.tax_exclusive_amount, currencyID="GBP"
        ) if self.tax_exclusive_amount else ""

        self.allowance_total_amount_element = \
            CBC.AllowanceTotalAmount(
                self.allowance_total_amount, currencyID="GBP") \
            if self.allowance_total_amount else ""

        self.line_extension_amount_element = \
            CBC.LineExtensionAmount(
                self.line_extension_amount, currencyID="GBP") \
            if self.line_extension_amount else ""

    def xml(self):
        element = CAC.LegalMonetaryTotal(
            self.line_extension_amount_element,
            self.tax_exclusive_amount_element,
            self.allowance_total_amount_element,
            self.payable_amount.xml(),
        )
        return element


@attr.s
class InvoiceDocumentReference:
    id: str = attr.ib(default=None)

    def xml(self):
        element = CAC.InvoiceDocumentReference(
            CBC.ID(self.id)
        )
        return element


@attr.s
class Item:
    descriptions: Optional[List[str]] = attr.ib(default=None)
    pack_quantity: Optional[float] = attr.ib(default=None)
    pack_size_numeric: Optional[float] = attr.ib(default=None)
    catalogue_indicator: Optional[bool] = attr.ib(default=None)
    name: Optional[str] = attr.ib(default=None)
    hazardous_risk_indicator: Optional[bool] = attr.ib(default=None)
    additional_information: Optional[List[str]] = attr.ib(default=None)
    keyword: Optional[List[str]] = attr.ib(default=None)
    brand_name: Optional[List[str]] = attr.ib(default=None)
    model_name: Optional[List[str]] = attr.ib(default=None)
    buyers_item_identification: Optional[str] = attr.ib(default=None)
    sellers_item_identification: Optional[str] = attr.ib(default=None)
    manufacturers_item_identification: Optional[List[str]] = \
        attr.ib(default=None)
    standard_item_identification: Optional[str] = attr.ib(default=None)
    catalogue_item_identification: Optional[str] = attr.ib(default=None)
    additional_item_identification: Optional[List[str]] = attr.ib(default=None)
    catalogue_document_reference: Optional[str] = attr.ib(default=None)
    item_specification_document_reference: Optional[List[str]] = \
        attr.ib(default=None)
    origin_country: Optional[str] = attr.ib(default=None)
    commodity_classification: Optional[str] = attr.ib(default=None)
    transaction_conditions: Optional[List[str]] = attr.ib(default=None)
    hazardous_item: Optional[List[str]] = attr.ib(default=None)
    classified_tax_category: Optional[List[str]] = attr.ib(default=None)
    additional_item_property: Optional[List[str]] = attr.ib(default=None)
    manufacturer_party: Optional[List[str]] = attr.ib(default=None)
    information_content_provider_party: Optional[str] = attr.ib(default=None)
    origin_address: Optional[List[str]] = attr.ib(default=None)
    item_instance: Optional[List[str]] = attr.ib(default=None)
    certificate: Optional[List[str]] = attr.ib(default=None)
    dimension: Optional[List[str]] = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.sellers_item_identification_element = \
            CAC.SellersItemIdentification(
                CBC.ID(self.sellers_item_identification),
            ) if self.sellers_item_identification else ""
        self.description_elements = [
            CBC.Description(d) for d in self.descriptions
        ] if self.descriptions else ""

    def xml(self):
        element = CAC.Item(
            *self.description_elements,
            self.sellers_item_identification_element,
        )
        return element


@attr.s
class InvoiceLine:
    id: int = attr.ib()
    item: Item = attr.ib()
    uuid: Optional[str] = attr.ib(default=None)
    note: Optional[List[str]] = attr.ib(default=None)
    invoiced_quantity: Optional[str] = attr.ib(default=None)
    unit_of_measure: Optional[str] = attr.ib(default=None)
    line_extension_amount: str = attr.ib(default=None)
    tax_point_date: Optional[str] = attr.ib(default=None)
    accounting_cost_code: Optional[str] = attr.ib(default=None)
    accounting_cost: Optional[str] = attr.ib(default=None)
    payment_purpose_code: Optional[str] = attr.ib(default=None)
    free_of_charge_indicator: Optional[str] = attr.ib(default=None)
    invoice_period: Optional[List[str]] = attr.ib(default=None)
    order_line_reference: Optional[List[str]] = attr.ib(default=None)
    despatch_line_reference: Optional[List[str]] = attr.ib(default=None)
    receipt_line_reference: Optional[List[str]] = attr.ib(default=None)
    billing_reference: Optional[List[str]] = attr.ib(default=None)
    document_reference: Optional[List[str]] = attr.ib(default=None)
    pricing_reference: Optional[str] = attr.ib(default=None)
    originator_party: Optional[str] = attr.ib(default=None)
    delivery: Optional[List[str]] = attr.ib(default=None)
    payment_terms: Optional[List[str]] = attr.ib(default=None)
    allowance_charge: Optional[List[str]] = attr.ib(default=None)
    tax_total: Optional[TaxTotal] = attr.ib(default=None)
    withholding_tax_total: Optional[List[str]] = attr.ib(default=None)
    price: Optional[str] = attr.ib(default=None)
    delivery_terms: Optional[str] = attr.ib(default=None)
    sub_invoice_line: Optional[List[str]] = attr.ib(default=None)
    item_price_extension: Optional[str] = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.invoiced_quantity_element = CBC.InvoicedQuantity(
            str(self.invoiced_quantity),
            unitCode=self.unit_of_measure,
        ) if (self.invoiced_quantity and self.unit_of_measure) else ""
        self.line_extension_amount_element = CBC.LineExtensionAmount(
            self.line_extension_amount, currencyID="GBP",
        ) if self.line_extension_amount else ""
        self.tax_total_element = self.tax_total.xml() if self.tax_total else ""

    def xml(self):
        element = CAC.InvoiceLine(
            CBC.ID(str(self.id)),
            self.invoiced_quantity_element,
            self.line_extension_amount_element,
            self.tax_total_element,
            self.item.xml(),
            CAC.Price(CBC.PriceAmount(str(self.price), currencyID="GBP")),
        )
        return element


@attr.s
class Invoice:
    id: "UUID" = attr.ib(default=None)
    issue_date: "datetime" = attr.ib(default=None)
    accounting_supplier_party: AccountingSupplierParty = attr.ib(default=None)
    accounting_customer_party: AccountingCustomerParty = attr.ib(default=None)
    legal_monetary_total: LegalMonetaryTotal = attr.ib(default=None)
    invoice_lines: List[InvoiceLine] = attr.ib(default=None)
    tax_total: Optional[TaxTotal] = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.tax_total_element = self.tax_total.xml() if self.tax_total else ""

    def xml(self):
        element = INV.Invoice(
            CBC.ID(str(self.id)),
            CBC.IssueDate(str(self.issue_date)),
            self.accounting_supplier_party.xml(),
            self.accounting_customer_party.xml(),
            self.tax_total_element,
            self.legal_monetary_total.xml(),
            *[rl.xml() for rl in self.invoice_lines],
        )
        return element


def dump_xml(doc):
    etree.cleanup_namespaces(
        doc,
        top_nsmap=TOP_NSMAP,
    )
    return etree.tostring(doc, encoding="unicode", pretty_print=True)
