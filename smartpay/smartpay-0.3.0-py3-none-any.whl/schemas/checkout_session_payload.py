import jtd

checkout_session_payload_schema = jtd.Schema.from_dict({
    "definitions": {
        "address": {
            "properties": {
                "line1": {"type": "string"},
                "locality": {"type": "string"},
                "country": {"type": "string"},
                "postalCode": {"type": "string"}
            },
            "optionalProperties": {
                "line2": {"type": "string"},
                "line3": {"type": "string"},
                "line4": {"type": "string"},
                "line5": {"type": "string"},
                "administrativeArea": {"type": "string"},
                "subLocality": {"type": "string"},
                "addressType": {"type": "string"}
            },
            "additionalProperties": True
        },
        "product": {
            "properties": {
                "name": {"type": "string"}
            },
            "optionalProperties": {
                "brand": {"type": "string"},
                "categories": {"elements": {"type": "string"}},
                "description": {"type": "string"},
                "gtin": {"type": "string"},
                "images": {"elements": {"type": "string"}},
                "reference": {"type": "string"},
                "url": {"type": "string"}
            },
            "additionalProperties": True
        },
        "price": {
            "properties": {
                "productData": {"ref": "product"},
                "amount": {"type": "uint32"},
                "currency": {"type": "string"}
            },
            "optionalProperties": {
                "description": {"type": "string"},
                "label": {"type": "string"}
            },
            "additionalProperties": True
        },
        "lineItem": {
            "properties": {
                "quantity": {"type": "uint16"}
            },
            "optionalProperties": {
                "priceData": {"ref": "price"},
                "amount": {"type": "uint32"},
                "currency": {"type": "string"},
                "description": {"type": "string"},
                "image": {"type": "string"},

                "priceDescription": {"type": "string"},
                "label": {"type": "string"},

                "name": {"type": "string"},
                "brand": {"type": "string"},
                "categories": {"elements": {"type": "string"}},
                "productDescription": {"type": "string"},
                "gtin": {"type": "string"},
                "images": {"elements": {"type": "string"}},
                "reference": {"type": "string"},
                "url": {"type": "string"}
            },
            "additionalProperties": True
        },
        "order": {
            "properties": {
                "amount": {"type": "uint32"},
                "currency": {"type": "string"},
                "lineItemData": {"elements": {"ref": "lineItem"}},
                "shippingInfo": {
                    "properties": {
                        "address": {"ref": "address"}
                    },
                    "optionalProperties": {
                        "addressType": {"type": "string"},
                        "feeAmount": {"type": "uint32"},
                        "feeCurrency": {"type": "string"}
                    },
                    "additionalProperties": True
                },
                "reference": {"type": "string"}
            },
            "optionalProperties": {
                "captureMethod": {"type": "string"},
                "confirmationMethod": {"type": "string"},
                "coupons": {"elements": {"type": "string"}}
            },
            "additionalProperties": True
        },
        "customer": {
            "optionalProperties": {
                "accountAge": {"type": "uint32"},
                "emailAddress": {"type": "string"},
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "phoneNumber": {"type": "string"},
                "firstNameKana": {"type": "string"},
                "lastNameKana": {"type": "string"},
                "address": {"ref": "address"},
                "dateOfBirth": {"type": "string"},
                "legalGender": {"type": "string"},
                "reference": {"type": "string"}
            },
            "additionalProperties": True
        }
    },

    "properties": {},
    "optionalProperties": {
        "customerInfo": {"ref": "customer"},
        "customer": {"ref": "customer"},

        "orderData": {"ref": "order"},
        "amount": {"type": "uint32"},
        "currency": {"type": "string"},
        "lineItemData": {"elements": {"ref": "lineItem"}},
        "items": {"elements": {"ref": "lineItem"}},
        "shipping": {"ref": "address"},

        "reference": {"type": "string"},

        "successUrl": {"type": "string"},
        "cancelUrl": {"type": "string"},
        "successURL": {"type": "string"},
        "cancelURL": {"type": "string"}
    },
    "additionalProperties": True
}
)
