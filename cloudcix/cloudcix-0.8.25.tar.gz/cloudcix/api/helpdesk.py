from cloudcix.client import Client


class Helpdesk:
    """
    The HelpDesk application is both a ticketing system, and a returns management system
    """
    _application_name = 'HelpDesk'

    iris_condition = Client(
        _application_name,
        'IRISCondition/',
    )
    iris_defect = Client(
        _application_name,
        'IRISDefect/',
    )
    iris_extended_condition = Client(
        _application_name,
        'IRISExtendedCondition/',
    )
    iris_ntf = Client(
        _application_name,
        'IRISNTF/',
    )
    iris_repair = Client(
        _application_name,
        'IRISRepair/',
    )
    iris_section = Client(
        _application_name,
        'IRISSection/',
    )
    iris_symptom = Client(
        _application_name,
        'IRISSymptom/',
    )
    item = Client(
        _application_name,
        'Ticket/{transaction_type_id}/{transaction_sequence_number}/Item/',
    )
    item_history = Client(
        _application_name,
        'Ticket/{transaction_type_id}/{transaction_sequence_number}/Item/{item_id}/History/',
    )
    item_part_used = Client(
        _application_name,
        'Ticket/{transaction_type_id}/{transaction_sequence_number}/Item/{item_id}/PartUsed/',
    )
    item_status = Client(
        _application_name,
        'ItemStatus/',
    )
    reason_for_return = Client(
        _application_name,
        'ReasonForReturn/',
    )
    reason_for_return_translation = Client(
        _application_name,
        'ReasonForReturn/{reason_for_return_id}/Translation/',
    )
    service_centre_logic = Client(
        _application_name,
        'ServiceCentreLogic/',
    )
    service_centre_warrantor = Client(
        _application_name,
        'ServiceCentre/{address_id}/Warrantor/',
    )
    status = Client(
        _application_name,
        'Status/',
    )
    ticket = Client(
        _application_name,
        'Ticket/{transaction_type_id}/',
    )
    ticket_history = Client(
        _application_name,
        'Ticket/{transaction_type_id}/{transaction_sequence_number}/History/',
    )
    ticket_question = Client(
        _application_name,
        'TicketQuestion/',
    )
    ticket_type = Client(
        _application_name,
        'TicketType/',
    )
    ticket_type_question = Client(
        _application_name,
        'TicketType/{id}/TicketQuestion/',
    )
    warrantor_logic = Client(
        _application_name,
        'WarrantorLogic/',
    )
    warrantor_service_centre = Client(
        _application_name,
        'Warrantor/{address_id}/ServiceCentre/',
    )
