def boolean_validator(field, value, error):
    if value and value not in ["true", "false"]:
        error(field, "Must be a boolean value: true or false")


S_ADDRESS_CREATE = {
    "street": {"type": "string", "required": True, "empty": False},
    "street2": {"type": "string"},
    "zip_code": {"type": "string", "required": True, "empty": False},
    "city": {"type": "string", "required": True, "empty": False},
    "country": {"type": "string", "required": True, "empty": False},
    "state": {"type": "string"},
}

S_ISP_INFO_CREATE = {
    "phone_number": {"type": "string"},
    "type": {"type": "string"},
    "delivery_address": {
        "nullable": True,
        "type": "dict",
        "schema": S_ADDRESS_CREATE
    },
    "invoice_address": {
        "type": "dict",
        "schema": S_ADDRESS_CREATE
    },
    "previous_provider": {"type": "integer"},
    "previous_owner_vat_number": {"type": "string"},
    "previous_owner_name": {"type": "string"},
    "previous_owner_first_name": {"type": "string"},
}

S_MOBILE_ISP_INFO_CREATE = {
    "icc": {"type": "string"},
    "icc_donor": {"type": "string"},
    "previous_contract_type": {"type": "string"},
}

S_BROADBAND_ISP_INFO_CREATE = {
    "service_address": {
        "type": "dict",
        "schema": S_ADDRESS_CREATE
    },
    "keep_phone_number": {"type": "boolean"},
    "change_address": {"type": "boolean"},
}

S_CRM_LEAD_RETURN_CREATE = {
    "id": {"type": "integer"}
}

S_CRM_LEAD_CREATE = {
    "iban": {"type": "string", "required": True, "empty": False},
    "subscription_request_id": {
        "type": "integer",
        "empty": False,
        "required": True,
        'excludes': ['partner_id'],
    },
    "partner_id": {
        "type": "string",
        "empty": False,
        "required": True,
        'excludes': ['subscription_request_id'],
    },
    "lead_line_ids": {
        "type": "list",
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": {
                "product_code": {"type": "string", "required": True},
                "broadband_isp_info": {
                    "type": "dict",
                    # Merging dicts in Python 3.5+
                    # https://www.python.org/dev/peps/pep-0448/
                    "schema": {**S_ISP_INFO_CREATE, **S_BROADBAND_ISP_INFO_CREATE}  # noqa
                },
                "mobile_isp_info": {
                    "type": "dict",
                    "schema": {**S_ISP_INFO_CREATE, **S_MOBILE_ISP_INFO_CREATE}  # noqa
                },
            }
        },
    }
}
S_CONTRACT_SERVICE_INFO_CREATE = {
    "phone_number": {"type": "string", "required": True, "empty": False},
}

S_CONTRACT_ROUTER_MAC_ADDRESS_CREATE = {
    "router_mac_address": {
        "type": "string", "required": False, "empty": True,
        "regex": "-|^[0-9A-F]{2}([-:]?)[0-9A-F]{2}(\\1[0-9A-F]{2}){4}$"
    },
}
S_MOBILE_CONTRACT_SERVICE_INFO_CREATE = {
    "icc": {"type": "string", "required": True, "empty": False},
}
S_ADSL_CONTRACT_SERVICE_INFO_CREATE = {
    "administrative_number": {"type": "string", "required": True, "empty": False},
    "router_product_id": {"type": "string", "required": True},
    "router_serial_number": {"type": "string", "required": True, "empty": False},
    "ppp_user": {"type": "string", "required": True, "empty": False},
    "ppp_password": {"type": "string", "required": True, "empty": False},
    "endpoint_user": {"type": "string", "required": True, "empty": False},
    "endpoint_password": {"type": "string", "required": True, "empty": False},
}

S_VODAFONE_ROUTER_4G_CONTRACT_SERVICE_INFO_CREATE = {
    "vodafone_id": {"type": "string", "required": True, "empty": False},
    "vodafone_offer_code": {"type": "string", "required": True, "empty": False},
}

S_VODAFONE_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "vodafone_id": {"type": "string", "required": True, "empty": False},
    "vodafone_offer_code": {"type": "string", "required": True, "empty": False},
}

S_MM_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "mm_id": {"type": "string", "required": True, "empty": False},
}

S_ORANGE_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "suma_id": {"type": "string", "required": True, "empty": False},
}

S_XOLN_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "external_id": {"type": "string", "required": True, "empty": False},
    "id_order": {"type": "string", "required": True, "empty": False},
    "project": {"type": "string", "required": True, "empty": False},
    "router_product_id": {"type": "string", "required": True},
    "router_serial_number": {"type": "string", "required": True, "empty": False},
}

S_CONTRACT_CREATE = {
    "code": {"type": "string", "required": False, "empty": False},
    "iban": {"type": "string", "required": True, "empty": False},
    "email": {"type": "string", "required": True, "empty": True},
    "mobile_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_MOBILE_CONTRACT_SERVICE_INFO_CREATE
        }
    },
    "adsl_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_CONTRACT_ROUTER_MAC_ADDRESS_CREATE,
            **S_ADSL_CONTRACT_SERVICE_INFO_CREATE
        }
    },
    "vodafone_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_VODAFONE_FIBER_CONTRACT_SERVICE_INFO_CREATE
        },
    },
    "router_4G_service_contract_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_VODAFONE_ROUTER_4G_CONTRACT_SERVICE_INFO_CREATE
        },
    },
    "mm_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_MM_FIBER_CONTRACT_SERVICE_INFO_CREATE,
        }
    },
    "orange_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_ORANGE_FIBER_CONTRACT_SERVICE_INFO_CREATE,
        }
    },
    "xoln_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_CONTRACT_ROUTER_MAC_ADDRESS_CREATE,
            **S_XOLN_FIBER_CONTRACT_SERVICE_INFO_CREATE,
        }
    },
    "partner_id": {"type": "string", "required": True},
    "service_address": {"type": "dict", "schema": S_ADDRESS_CREATE},
    "service_technology": {"type": "string", "required": True, "empty": False},
    "service_supplier": {"type": "string", "required": True, "empty": False},
    "fiber_signal_type": {
        "type": "string",
        "allowed": ["", "fibraCoaxial", "fibraFTTH", "fibraIndirecta", "NEBAFTTH"]
    },
    "contract_lines": {
        "type": "list",
        "dependencies": {'contract_line': None},
        "schema": {
            "type": "dict",
            "schema": {
                "product_code": {"type": "string", "required": True},
                "date_start": {
                    "type": "string", "required": True,
                    "regex": "\\d{4}-[01]\\d-[0-3]\\d [0-2]\\d:[0-5]\\d:[0-5]\\d"
                }
            }
        }
    },
    "contract_line": {
        "type": "dict",
        "dependencies": {'contract_lines': None},
        "schema": {
            "product_code": {"type": "string", "required": True},
            "date_start": {
                "type": "string", "required": True,
                "regex": "\\d{4}-[01]\\d-[0-3]\\d [0-2]\\d:[0-5]\\d:[0-5]\\d"
            }
        }
    },
    "ticket_number": {"type": "string", "required": True}
}

S_CONTRACT_RETURN_CREATE = {
    "id": {"type": "integer"}
}

S_PREVIOUS_PROVIDER_REQUEST_SEARCH = {
    "mobile": {"type": "string", "check_with": boolean_validator},
    "broadband": {"type": "string", "check_with": boolean_validator},
}

S_PREVIOUS_PROVIDER_RETURN_SEARCH = {
    "count": {"type": "integer"},
    "providers": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "id": {"type": "integer", "required": True},
                "name": {"type": "string", "required": True},
            }
        }
    }
}

S_DISCOVERY_CHANNEL_REQUEST_SEARCH = {"_id": {"type": "integer"}}

S_DISCOVERY_CHANNEL_RETURN_SEARCH = {
    "discovery_channels": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "id": {"type": "integer", "required": True},
                "name": {"type": "string", "required": True},
            }
        }
    }
}

S_PRODUCT_CATALOG_REQUEST_SEARCH = {
    "code": {"type": "string"},
    "categ": {"type": "string", 'allowed': ['mobile', 'adsl', 'fiber']},
}

S_PRODUCT_CATALOG_RETURN_SEARCH = {
    "pricelists": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "code": {"type": "string", "required": True},
                "products": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": {
                            "code": {"type": "string", "required": True},
                            "name": {"type": "string", "required": True},
                            "price": {"type": "number", "required": True},
                            "category": {"type": "string", "required": True},
                            "minutes": {"type": "integer", "nullable": True,
                                        "required": True},
                            "data": {"type": "integer", "nullable": True,
                                     "required": True},
                            "bandwidth": {"type": "integer", "nullable": True,
                                          "required": True},
                            "available_for": {
                                "type": "list",
                                "required": True,
                                "schema": {
                                    "type": "string",
                                },
                            }
                        }
                    }
                }
            }
        }
    }
}


S_CONTRACT_ONE_SHOT_ADDITION = {
    "product_code": {"type": "string", "required": True},
    "phone_number": {"type": "string", "required": True},
}

S_CONTRACT_CHANGE_TARIFF = {
    "product_code": {"type": "string", "required": True},
    "phone_number": {"type": "string", "required": True},
}

S_RES_PARTNER_REQUEST_GET = {"_id": {"type": "integer"}}

S_RES_PARTNER_REQUEST_SEARCH = {
    "vat": {"type": "string", "required": True},
}

S_RES_PARTNER_RETURN_GET = {
    "id": {"type": "integer"},
    "name": {"type": "string"},
    "firstname": {"type": "string"},
    "lastname": {"type": "string"},
    "display_name": {"type": "string"},
    "ref": {"type": "string"},
    "lang": {"type": "string"},
    "vat": {"type": "string"},
    "type": {"type": "string"},
    "email": {"type": "string"},
    "phone": {"type": "string"},
    "mobile": {"type": "string"},
    "birthdate_date": {"type": "string"},
    "cooperator_register_number": {"type": "integer"},
    "cooperator_end_date": {"type": "string"},
    "coop_agreement_code": {"type": "string"},
    "sponsor_id": {"type": "integer"},
    "coop_candidate": {"type": "boolean"},
    "member": {"type": "boolean"},
}

S_ACCOUNT_INVOICE_CREATE = {
    'billingAccountCode': {
        "type": "string", "required": True,
        "regex": "^[0-9]+_[0-9]+$"
    },
    'invoiceNumber': {"type": "string", "required": True},
    "invoiceDate": {
        "type": "integer", "required": True,
    },
    'amountWithoutTax': {
        "type": "float",
        "required": True
    },
    'amountTax': {
        "type": "float",
        "required": True
    },
    'amountWithTax': {
        "type": "float",
        "required": True
    },
    "categoryInvoiceAgregates": {
        "type": "list",
        "required": True,
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": {
                "listSubCategoryInvoiceAgregateDto": {
                    "type": "list",
                    "required": True,
                    "empty": False,
                    "schema": {
                        "type": "dict",
                        "schema": {
                            "description": {
                                "type": "string",
                                "required": True
                            },
                            "accountingCode": {
                                "type": "string",
                                "required": True
                            },
                            "amountWithoutTax": {
                                "type": "float",
                                "required": True
                            },
                            "amountWithTax": {
                                "type": "float",
                                "required": True
                            },
                            "amountTax": {
                                "type": "float",
                                "required": True
                            },
                            "taxCode": {
                                "type": "string",
                                "required": True
                            },
                            "invoiceSubCategoryCode": {
                                "type": "string",
                                "required": True
                            },
                        }
                    }
                }
            }
        }
    },
    'taxAggregates': {
        "type": "list",
        "required": True,
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": {
                "taxCode": {
                    "type": "string",
                    "required": True
                },
                "amountTax": {
                    "type": "float",
                    "required": True
                },
                "amountWithoutTax": {
                    "type": "float",
                    "required": True
                },
            }
        }
    }
}

S_SUBSCRIPTION_REQUEST_CREATE_SC_FIELDS = {
    "iban": {"type": "string"},
    "vat": {"type": "string", "required": True},
    "coop_agreement": {"type": "string"},
    "sponsor_vat": {"type": "string"},
    "voluntary_contribution": {"type": "float"},
    "nationality": {"type": "string"},
    "payment_type": {"type": "string", "required": True},
    "address": {"type": "dict", "schema": S_ADDRESS_CREATE},
    "type": {"type": "string", "required": True},
    "share_product": {"type": "integer", "required": False},
    "ordered_parts": {"type": "integer", "required": False},
    "discovery_channel_id": {"type": "integer", "required": True},
    "birthdate": {
        "type": "string",
        "regex": "\\d{4}-[01]\\d-[0-3]\\d"
    },
    "gender": {"type": "string"},
    "phone": {"type": "string"},
    "is_company": {"type": "boolean"},
    "company_name": {"type": "string"},
    "firstname": {"type": "string"},
    "lastname": {"type": "string"},
}

S_SUBSCRIPTION_REQUEST_RETURN_CREATE_SC_FIELDS = {
    "share_product": {"required": False},
    "ordered_parts": {"type": "integer", "required": False},
}

S_CONTRACT_IBAN_CHANGE_CREATE = {
    "partner_id": {"type": "string", "required": True},
    "iban": {"type": "string", "required": True},
    "contracts": {"type": "string", "required": False},
}
