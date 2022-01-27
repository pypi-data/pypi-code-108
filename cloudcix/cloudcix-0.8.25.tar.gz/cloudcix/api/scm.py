from cloudcix.client import Client


class SCM:
    """
    SCM is an Application to manage the planning, procurement, storage, distribution, service and return of inventory
    """
    _application_name = 'SCM'

    agreed_price = Client(
        _application_name,
        'AgreedPrice/',
    )
    bin = Client(
        _application_name,
        'Bin/',
    )
    bin_sku = Client(
        _application_name,
        'Bin/{id}/SKU/',
    )
    brand = Client(
        _application_name,
        'Brand/',
    )
    cloud_bill = Client(
        _application_name,
        'CloudBill/{address_id}/',
    )
    # idSKUComponent should be passed as pk to resource methods
    critical_bom = Client(
        _application_name,
        'SKU/{sku_id}/BOM/',
    )
    # CriticalBOM for member returns all BOM records for the idMember
    # doing the request
    critical_bom_for_member = Client(
        _application_name,
        'SKU/BOM/',
    )
    manufactured_item = Client(
        _application_name,
        'ManufacturedItem/',
    )
    purchase_order = Client(
        _application_name,
        'PurchaseOrder',
    )
    return_question = Client(
        _application_name,
        'ReturnQuestion/',
    )
    return_question_field_type = Client(
        _application_name,
        'ReturnQuestionFieldType/',
    )
    sales_order = Client(
        _application_name,
        'SalesOrder/',
    )
    service_group = Client(
        _application_name,
        'ServiceGroup/',
    )
    sku = Client(
        _application_name,
        'SKU/',
    )
    sku_category = Client(
        _application_name,
        'SKUCategory/',
    )
    sku_category_return_question = Client(
        _application_name,
        'SKUCategory/{sku_category_id}/ReturnQuestion/',
    )
    sku_stock = Client(
        _application_name,
        'SKU/{sku_id}/Stock/',
    )
    sku_stock_adjustment = Client(
        _application_name,
        'SKUStockAdjustment/',
    )
    sku_value = Client(
        _application_name,
        'SKU/{sku_id}/Value/',
    )
    validate_purchase_order = Client(
        _application_name,
        'Validate/PurchaseOrder/',
    )
    validate_sales_order = Client(
        _application_name,
        'Validate/SalesOrder/',
    )
