from django.core.management.base import BaseCommand
from django.db import Error

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.models import Contract, Tracking

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    help = "Links tracking objects with old contracts after 1.2.0 update"

    def handle(self, *args, **options):

        updated = 0

        self.stdout.write("Starting contract and tracking manual linking...")

        # Get all contracts for owner
        all_contracts = Contract.objects.all()

        self.stdout.write(
            "Found %s old contracts stored in database" % len(all_contracts)
        )

        # Get all tracking objects from the database
        tracking_numbers = Tracking.objects.filter(contract__isnull=True)

        self.stdout.write(
            "Found %s tracking objects with no contracts" % len(tracking_numbers)
        )

        # Start looping for all stored tracking objects
        for tracking in tracking_numbers:

            # If the tracking has an active program (not deleted)
            if tracking.program:

                # Start checking if we find any matches from our ESI contracts
                for contract in all_contracts:

                    # Only get contracts with the correct prefill ticker
                    if tracking.tracking_number in contract.title:

                        try:
                            tracking = Tracking.objects.filter(pk=tracking.id).update(
                                contract=contract.id
                            )

                            updated += 1

                        except Error as e:
                            logger.error(
                                "Error linking contract %s with tracking %s: %s"
                                % (
                                    contract.contract_id,
                                    tracking.tracking_number,
                                    e,
                                )
                            )

                        break

        self.stdout.write("Linked up %s tracking objects with contracts" % (updated))
