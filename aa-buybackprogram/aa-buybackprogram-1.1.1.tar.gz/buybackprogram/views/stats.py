from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render
from eveuniverse.models import EveEntity

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.services.hooks import get_extension_logger

from ..models import (
    Contract,
    ContractItem,
    ContractNotification,
    Tracking,
    TrackingItem,
)

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybackprogram.basic_access")
def my_stats(request):

    # List for valid contracts to be displayed
    valid_contracts = []

    # Tracker values
    values = {
        "outstanding": 0,
        "finished": 0,
        "outstanding_count": 0,
        "finished_count": 0,
    }

    # Request user owned characters
    characters = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__character_id", flat=True
    )

    # All tracking objects
    tracking_numbers = Tracking.objects.all()

    # Loop tracking objects to see if we have any contracts
    for tracking in tracking_numbers:

        # Get contracts matching tracking numbers
        contract = Contract.objects.filter(
            issuer_id__in=characters, title__contains=tracking.tracking_number
        ).first()

        # If we have matching contracts
        if contract:

            # Get notes for this contract
            contract.notes = ContractNotification.objects.filter(contract=contract)

            contract.tracking = tracking

            # Walk the tracker values for contracts
            if contract.status == "outstanding":
                values["outstanding"] += contract.price
                values["outstanding_count"] += 1
            if contract.status == "finished":
                values["finished"] += contract.price
                values["finished_count"] += 1

            # Get the name for the issuer
            contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)

            # Get the name for the assignee
            contract.assignee_name = EveEntity.objects.resolve_name(
                contract.assignee_id
            )

            # Add contract to the valid contract list
            valid_contracts.append(contract)

    context = {
        "contracts": valid_contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/stats.html", context)


@login_required
@permission_required("buybackprogram.manage_programs")
def program_stats(request):

    # List for valid contracts to be displayed
    valid_contracts = []

    # Tracker values
    values = {
        "outstanding": 0,
        "finished": 0,
        "outstanding_count": 0,
        "finished_count": 0,
    }

    # Request user owned characters
    characters = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__character_id", flat=True
    )

    # Request user owned corporations
    corporations = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__corporation_id", flat=True
    )

    # All tracking objects
    tracking_numbers = Tracking.objects.all()

    # Loop tracking objects to see if we have any contracts
    for tracking in tracking_numbers:

        # Get contracts matching tracking numbers
        contract = Contract.objects.filter(
            Q(assignee_id__in=characters) | Q(assignee_id__in=corporations),
            title__contains=tracking.tracking_number,
        ).first()

        # If we have matching contracts
        if contract:

            # Get notes for this contract
            contract.notes = ContractNotification.objects.filter(contract=contract)

            contract.tracking = tracking

            # Walk the tracker values for contracts
            if contract.status == "outstanding":
                values["outstanding"] += contract.price
                values["outstanding_count"] += 1
            if contract.status == "finished":
                values["finished"] += contract.price
                values["finished_count"] += 1

            # Get the name for the issuer
            contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)

            # Get the name for the assignee
            contract.assignee_name = EveEntity.objects.resolve_name(
                contract.assignee_id
            )

            # Add contract to the valid contract list
            valid_contracts.append(contract)

    context = {
        "contracts": valid_contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/stats.html", context)


@login_required
@permission_required("buybackprogram.see_all_statics")
def program_stats_all(request):

    # List for valid contracts to be displayed
    valid_contracts = []

    # Tracker values
    values = {
        "outstanding": 0,
        "finished": 0,
        "outstanding_count": 0,
        "finished_count": 0,
    }

    # All tracking objects
    tracking_numbers = Tracking.objects.all()

    # Loop tracking objects to see if we have any contracts
    for tracking in tracking_numbers:

        # Get contracts matching tracking numbers
        contract = Contract.objects.filter(
            title__contains=tracking.tracking_number
        ).first()

        # If we have matching contracts
        if contract:

            # Get notes for this contract
            contract.notes = ContractNotification.objects.filter(contract=contract)

            contract.tracking = tracking

            # Walk the tracker values for contracts
            if contract.status == "outstanding":
                values["outstanding"] += contract.price
                values["outstanding_count"] += 1
            if contract.status == "finished":
                values["finished"] += contract.price
                values["finished_count"] += 1

            # Get the name for the issuer
            contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)

            # Get the name for the assignee
            contract.assignee_name = EveEntity.objects.resolve_name(
                contract.assignee_id
            )

            valid_contracts.append(contract)

    context = {
        "contracts": valid_contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/stats.html", context)


@login_required
@permission_required("buybackprogram.basic_access")
def contract_details(request, contract_title):

    contract = Contract.objects.get(title__contains=contract_title)

    # Get notes for this contract
    notes = ContractNotification.objects.filter(contract=contract)

    # Get items for this contract
    contract_items = ContractItem.objects.filter(contract=contract)

    # Get tracking object for this contract
    tracking = Tracking.objects.get(
        tracking_number=contract_title,
    )

    # Get tracked items
    tracking_items = TrackingItem.objects.filter(tracking=tracking)

    # Get the name for the issuer
    contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)

    # Get the name for the assignee
    contract.assignee_name = EveEntity.objects.resolve_name(contract.assignee_id)

    context = {
        "notes": notes,
        "contract": contract,
        "contract_items": contract_items,
        "tracking": tracking,
        "tracking_items": tracking_items,
    }

    return render(request, "buybackprogram/contract_details.html", context)
