PAYLOAD_CANCEL_SUBSCRIPTION = {
    "id": "evt_1I0SkiGeGvgK89lRJLGcWcdq",
    "object": "event",
    "api_version": "2020-08-27",
    "created": 1608473956,
    "livemode": False,
    "pending_webhooks": 1,
    "request": {
        "id": None,
        "idempotency_key": "pi_1I0SjpGeGvgK89lRRpzTMumY-src_1I0SjqGeGvgK89lRNMDOYVAt"
    },
    "type": "customer.subscription.deleted",
    "data": {
        "object": {
            "id": "sub_1Js0mcGeGvgK89lRv7MzzFzM",
            "object": "subscription",
            "application_fee_percent": None,
            "automatic_tax": {
                "enabled": False
            },
            "billing_cycle_anchor": 1641282890,
            "billing_thresholds": None,
            "cancel_at": None,
            "cancel_at_period_end": False,
            "canceled_at": 1642582735,
            "collection_method": "charge_automatically",
            "created": 1636012490,
            "current_period_end": 1672818890,
            "current_period_start": 1641282890,
            "customer": "cus_KX4wzAxijbbUcz",
            "days_until_due": None,
            "default_payment_method": None,
            "default_source": None,
            "default_tax_rates": [
            ],
            "discount": None,
            "ended_at": 1642582735,
            "items": {
                "object": "list",
                "data": [
                    {
                        "id": "si_KX4wKrpUWJj7gk",
                        "object": "subscription_item",
                        "billing_thresholds": None,
                        "created": 1636012490,
                        "metadata": {
                        },
                        "plan": {
                            "id": "price_1HNZgfGeGvgK89lR4RYWNb42",
                            "object": "plan",
                            "active": True,
                            "aggregate_usage": None,
                            "amount": 4900,
                            "amount_decimal": "4900",
                            "billing_scheme": "per_unit",
                            "created": 1599205821,
                            "currency": "eur",
                            "interval": "year",
                            "interval_count": 1,
                            "livemode": True,
                            "metadata": {
                            },
                            "nickname": None,
                            "product": "prod_HxUgWVDT3R3AWI",
                            "tiers_mode": None,
                            "transform_usage": None,
                            "trial_period_days": 60,
                            "usage_type": "licensed"
                        },
                        "price": {
                            "id": "price_1HNZgfGeGvgK89lR4RYWNb42",
                            "object": "price",
                            "active": True,
                            "billing_scheme": "per_unit",
                            "created": 1599205821,
                            "currency": "eur",
                            "livemode": True,
                            "lookup_key": None,
                            "metadata": {
                            },
                            "nickname": None,
                            "product": "prod_HxUgWVDT3R3AWI",
                            "recurring": {
                                "aggregate_usage": None,
                                "interval": "year",
                                "interval_count": 1,
                                "trial_period_days": 60,
                                "usage_type": "licensed"
                            },
                            "tax_behavior": "unspecified",
                            "tiers_mode": None,
                            "transform_quantity": None,
                            "type": "recurring",
                            "unit_amount": 4900,
                            "unit_amount_decimal": "4900"
                        },
                        "quantity": 1,
                        "subscription": "sub_1Js0mcGeGvgK89lRv7MzzFzM",
                        "tax_rates": [
                        ]
                    }
                ],
                "has_more": False,
                "total_count": 1,
                "url": "/v1/subscription_items?subscription=sub_1Js0mcGeGvgK89lRv7MzzFzM"
            },
            "latest_invoice": "in_1KE7rNGeGvgK89lRTNQOI0lc",
            "livemode": True,
            "metadata": {
                "path": "/guillotina/subscription",
                "db": "db"
            },
            "next_pending_invoice_item_invoice": None,
            "pause_collection": None,
            "payment_settings": {
                "payment_method_options": None,
                "payment_method_types": None
            },
            "pending_invoice_item_interval": None,
            "pending_setup_intent": None,
            "pending_update": None,
            "plan": {
                "id": "price_1HNZgfGeGvgK89lR4RYWNb42",
                "object": "plan",
                "active": True,
                "aggregate_usage": None,
                "amount": 4900,
                "amount_decimal": "4900",
                "billing_scheme": "per_unit",
                "created": 1599205821,
                "currency": "eur",
                "interval": "year",
                "interval_count": 1,
                "livemode": True,
                "metadata": {
                },
                "nickname": None,
                "product": "prod_HxUgWVDT3R3AWI",
                "tiers_mode": None,
                "transform_usage": None,
                "trial_period_days": 60,
                "usage_type": "licensed"
            },
            "quantity": 1,
            "schedule": None,
            "start_date": 1636012490,
            "status": "canceled",
            "transfer_data": None,
            "trial_end": 1641282890,
            "trial_start": 1636012490
        }
    }
}


PAYLOAD = {
    "id": "evt_1I0SkiGeGvgK89lRJLGcWcdq",
    "object": "event",
    "api_version": "2020-08-27",
    "created": 1608473956,
    "data": {
        "object": {
            "id": "in_1I0SjpGeGvgK89lRLJThS7KK",
            "object": "invoice",
            "account_country": "ES",
            "account_name": "BLABLA",
            "account_tax_ids": None,
            "amount_due": 4000,
            "amount_paid": 4000,
            "amount_remaining": 0,
            "application_fee_amount": None,
            "attempt_count": 1,
            "attempted": True,
            "auto_advance": False,
            "billing_reason": "subscription_create",
            "charge": "ch_1I0SkhGeGvgK89lR2sGeIYZk",
            "collection_method": "charge_automatically",
            "created": 1608473901,
            "currency": "eur",
            "custom_fields": None,
            "customer": "cus_Ibg5fE2K1XzMCI",
            "customer_address": None,
            "customer_email": "test@test.com",
            "customer_name": None,
            "customer_phone": None,
            "customer_shipping": None,
            "customer_tax_exempt": "none",
            "customer_tax_ids": [],
            "default_payment_method": None,
            "default_source": None,
            "default_tax_rates": [],
            "description": None,
            "discount": None,
            "discounts": [],
            "due_date": None,
            "ending_balance": 0,
            "footer": None,
            "hosted_invoice_url": "https://invoice.stripe.com/i/acct_1ALBplGeGvgK89lR/invst_Ibg6zwbCjxVMacznqYPWJnva41oKtDF",
            "invoice_pdf": "https://pay.stripe.com/invoice/acct_1ALBplGeGvgK89lR/invst_Ibg6zwbCjxVMacznqYPWJnva41oKtDF/pdf",
            "last_finalization_error": None,
            "lines": {
                "object": "list",
                "data": [
                    {
                        "id": "il_1I0SjpGeGvgK89lRpkXE3p4M",
                        "object": "line_item",
                        "amount": 4000,
                        "currency": "eur",
                        "description": "1 × Subscripció TESTING (at €40.00 / year)",
                        "discount_amounts": [],
                        "discountable": True,
                        "discounts": [],
                        "livemode": False,
                        "metadata": {
                            "path": "/guillotina/subscription",
                            "db": "db"
                        },
                        "period": {
                            "end": 1640009901,
                            "start": 1608473901
                        },
                        "plan": {
                            "id": "price_1HNb9XGeGvgK89lRkF3KPEgs",
                            "object": "plan",
                            "active": True,
                            "aggregate_usage": None,
                            "amount": 4000,
                            "amount_decimal": "4000",
                            "billing_scheme": "per_unit",
                            "created": 1599211455,
                            "currency": "eur",
                            "interval": "year",
                            "interval_count": 1,
                            "livemode": False,
                            "metadata": {},
                            "nickname": None,
                            "product": "prod_HxWBZBSRA1ZV1H",
                            "tiers_mode": None,
                            "transform_usage": None,
                            "trial_period_days": None,
                            "usage_type": "licensed"
                        },
                        "price": {
                            "id": "price_1HNb9XGeGvgK89lRkF3KPEgs",
                            "object": "price",
                            "active": True,
                            "billing_scheme": "per_unit",
                            "created": 1599211455,
                            "currency": "eur",
                            "livemode": False,
                            "lookup_key": None,
                            "metadata": {},
                            "nickname": None,
                            "product": "prod_HxWBZBSRA1ZV1H",
                            "recurring": {
                                "aggregate_usage": None,
                                "interval": "year",
                                "interval_count": 1,
                                "trial_period_days": None,
                                "usage_type": "licensed"
                            },
                            "tiers_mode": None,
                            "transform_quantity": None,
                            "type": "recurring",
                            "unit_amount": 4000,
                            "unit_amount_decimal": "4000"
                        },
                        "proration": False,
                        "quantity": 1,
                        "subscription": "sub_Ibg6j4TZGkDH3d",
                        "subscription_item": "si_Ibg6YxvR24GDQu",
                        "tax_amounts": [],
                        "tax_rates": [],
                        "type": "subscription"
                    }
                ],
                "has_more": False,
                "total_count": 1,
                "url": "/v1/invoices/in_1I0SjpGeGvgK89lRLJThS7KK/lines"
            },
            "livemode": False,
            "next_payment_attempt": None,
            "number": "DD59E763-0001",
            "paid": True,
            "payment_intent": "pi_1I0SjpGeGvgK89lRRpzTMumY",
            "period_end": 1608473901,
            "period_start": 1608473901,
            "post_payment_credit_notes_amount": 0,
            "pre_payment_credit_notes_amount": 0,
            "receipt_number": None,
            "starting_balance": 0,
            "statement_descriptor": None,
            "status": "paid",
            "status_transitions": {
                "finalized_at": 1608473901,
                "marked_uncollectible_at": None,
                "paid_at": 1608473955,
                "voided_at": None
            },
            "subscription": "sub_Ibg6j4TZGkDH3d",
            "subtotal": 4000,
            "tax": None,
            "total": 4000,
            "total_discount_amounts": [],
            "total_tax_amounts": [],
            "transfer_data": None,
            "webhooks_delivered_at": None
        }
    },
    "livemode": False,
    "pending_webhooks": 1,
    "request": {
        "id": None,
        "idempotency_key": "pi_1I0SjpGeGvgK89lRRpzTMumY-src_1I0SjqGeGvgK89lRNMDOYVAt"
    },
    "type": "invoice.paid"
}
