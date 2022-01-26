"""
Import FAT data from ImicusFAT module
"""

# Django
from django.apps import apps
from django.core.management.base import BaseCommand

# Alliance Auth AFAT
from afat import __version__ as afat_version_installed
from afat.models import (
    AFat,
    AFatLink,
    AFatLinkType,
    AFatLog,
    AFatLogEvent,
    ClickAFatDuration,
)


def get_input(text) -> str:
    """
    Wrapped input to enable import
    :param text:
    :type text:
    :return:
    :rtype:
    """

    return input(text)


def imicusfat_installed() -> bool:
    """
    Check if imicusfat is installed
    :return:
    :rtype:
    """

    return apps.is_installed("imicusfat")


if imicusfat_installed():
    # Standard Library
    import sys

    # Third Party
    import requests
    from imicusfat import __version__ as ifat_version_installed
    from imicusfat.models import (
        ClickIFatDuration,
        IFat,
        IFatLink,
        IFatLinkType,
        ManualIFat,
    )
    from packaging.specifiers import SpecifierSet
    from packaging.version import parse as version_parse


class Command(BaseCommand):
    """
    Initial import of FAT data from AA FAT module
    """

    help = "Imports FAT data from ImicusFAT module"

    def latest_version_available(self, package_name):
        """
        Checking for the latest available version of a package on Pypi
        :param package_name:
        :type package_name:
        :return:
        :rtype:
        """

        current_python_version = version_parse(
            f"{sys.version_info.major}.{sys.version_info.minor}"
            f".{sys.version_info.micro}"
        )

        current_version = version_parse(ifat_version_installed)
        current_is_prerelease = (
            str(current_version) == str(ifat_version_installed)
            and current_version.is_prerelease
        )

        result = requests.get(
            f"https://pypi.org/pypi/{package_name}/json", timeout=(5, 30)
        )

        latest = None

        if result.status_code == requests.codes.ok:
            pypi_info = result.json()

            for release, release_details in pypi_info["releases"].items():
                release_detail = (
                    release_details[-1] if len(release_details) > 0 else None
                )
                if not release_detail or (
                    not release_detail["yanked"]
                    and (
                        "requires_python" not in release_detail
                        or not release_detail["requires_python"]
                        or current_python_version
                        in SpecifierSet(release_detail["requires_python"])
                    )
                ):
                    my_release = version_parse(release)

                    if str(my_release) == str(release) and (
                        current_is_prerelease or not my_release.is_prerelease
                    ):
                        latest = release

            if not latest:
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not find a suitable release of '{package_name}'"
                    )
                )

            return latest

        self.stdout.write(
            self.style.WARNING(f"Package '{package_name}' is not registered in PyPI")
        )

        return None

    def _import_from_imicusfat(self) -> None:
        """
        Start the import
        :return:
        :rtype:
        """

        # First, we check if the target tables are empty ...
        current_afat_count = AFat.objects.all().count()
        current_afat_links_count = AFatLink.objects.all().count()
        current_afat_linktype_count = AFatLinkType.objects.all().count()
        current_afat_clickduration_count = ClickAFatDuration.objects.all().count()

        if (
            current_afat_count > 0
            or current_afat_links_count > 0
            or current_afat_linktype_count > 0
            or current_afat_clickduration_count > 0
        ):
            self.stdout.write(
                self.style.WARNING(
                    "You already have FAT data with the aFAT module. "
                    "Import cannot be continued."
                )
            )

            return

        # Before we do anything, remove all "deleted" FATlinks and FATs
        IFatLink.all_objects.filter(deleted_at__isnull=False).hard_delete()
        IFat.all_objects.filter(deleted_at__isnull=False).hard_delete()

        # Import fat link type
        imicusfat_fleettypes = IFatLinkType.objects.all()
        for imicusfat_fleettype in imicusfat_fleettypes:
            self.stdout.write(f"Importing fleet type '{imicusfat_fleettype.name}'.")

            afat_fleettype = AFatLinkType()

            afat_fleettype.id = imicusfat_fleettype.id
            afat_fleettype.name = imicusfat_fleettype.name
            afat_fleettype.is_enabled = imicusfat_fleettype.is_enabled

            afat_fleettype.save()

        # Import FAT links
        imicusfat_fatlinks = IFatLink.objects.all()
        for imicusfat_fatlink in imicusfat_fatlinks:
            fleet = imicusfat_fatlink.fleet
            fatlink_hash = imicusfat_fatlink.hash
            fatlink_name = imicusfat_fatlink.fleet
            fatlink_creator = imicusfat_fatlink.creator

            self.stdout.write(
                f"Importing FAT link for fleet '{fleet}' with hash '{fatlink_hash}'."
            )

            afatlink = AFatLink()

            afatlink.id = imicusfat_fatlink.id
            afatlink.afattime = imicusfat_fatlink.ifattime
            afatlink.fleet = (
                imicusfat_fatlink.fleet
                if imicusfat_fatlink.fleet is not None
                else fatlink_hash
            )
            afatlink.hash = fatlink_hash
            afatlink.creator_id = imicusfat_fatlink.creator_id
            afatlink.link_type_id = imicusfat_fatlink.link_type_id
            afatlink.is_esilink = imicusfat_fatlink.is_esilink

            afatlink.save()

            # Write to log table
            if imicusfat_fatlink.is_esilink:
                log_text = (
                    f"ESI FAT link {fatlink_hash} with name {fatlink_name} "
                    f"was created by {fatlink_creator}"
                )
            else:
                try:
                    fleet_duration = ClickIFatDuration.objects.get(
                        fleet_id=imicusfat_fatlink.id
                    )

                    log_text = (
                        f"FAT link {fatlink_hash} with name {fatlink_name} and a "
                        f"duration of {fleet_duration.duration} minutes was created "
                        f"by {fatlink_creator}"
                    )
                except ClickIFatDuration.DoesNotExist:
                    log_text = (
                        f"FAT link {fatlink_hash} with name {fatlink_name} "
                        f"was created by {fatlink_creator}"
                    )

            afatlog = AFatLog()
            afatlog.log_time = imicusfat_fatlink.ifattime
            afatlog.log_event = AFatLogEvent.CREATE_FATLINK
            afatlog.log_text = log_text
            afatlog.user_id = imicusfat_fatlink.creator_id
            afatlog.save()

        # Import FATs
        imicustaf_fats = IFat.objects.all()
        for imicusfat_fat in imicustaf_fats:
            self.stdout.write(f"Importing FATs for FAT link ID '{imicusfat_fat.id}'.")

            afat = AFat()

            afat.id = imicusfat_fat.id
            afat.system = imicusfat_fat.system
            afat.shiptype = imicusfat_fat.shiptype
            afat.character_id = imicusfat_fat.character_id
            afat.afatlink_id = imicusfat_fat.ifatlink_id

            afat.save()

        # Import click FAT durations
        imicusfat_clickfatdurations = ClickIFatDuration.objects.all()
        for imicusfat_clickfatduration in imicusfat_clickfatdurations:
            self.stdout.write(
                f"Importing FAT duration with ID '{imicusfat_clickfatduration.id}'."
            )

            afat_clickfatduration = ClickAFatDuration()

            afat_clickfatduration.id = imicusfat_clickfatduration.id
            afat_clickfatduration.duration = imicusfat_clickfatduration.duration
            afat_clickfatduration.fleet_id = imicusfat_clickfatduration.fleet_id

            afat_clickfatduration.save()

        # Import manual fat to log table
        imicusfat_manualfats = ManualIFat.objects.all()
        for imicusfat_manualfat in imicusfat_manualfats:
            self.stdout.write(
                f"Importing manual FAT with ID '{imicusfat_manualfat.id}'."
            )

            fatlink = IFatLink.objects.get(manualifat=imicusfat_manualfat)
            pilot_name = imicusfat_manualfat.character.character_name
            log_text = (
                f"Pilot {pilot_name} was manually added to "
                f'FAT link with hash "{fatlink.hash}"'
            )

            if imicusfat_manualfat.created_at is not None:
                afatlog = AFatLog()
                afatlog.log_time = imicusfat_manualfat.created_at
                afatlog.log_event = AFatLogEvent.MANUAL_FAT
                afatlog.log_text = log_text
                afatlog.user_id = imicusfat_manualfat.creator_id
                afatlog.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Import complete! "
                "You can now deactivate the ImicusFAT module in your local.py"
            )
        )

    def handle(self, *args, **options):
        """
        Ask before running ...
        :param args:
        :type args:
        :param options:
        :type options:
        :return:
        :rtype:
        """

        if imicusfat_installed():
            has_conflict = False

            self.stdout.write(
                self.style.SUCCESS("ImicusFAT module is active, let's go!")
            )

            self.stdout.write("Checking for potentially available updates ...")

            ifat_version_available = self.latest_version_available(
                package_name="allianceauth-imicusfat"
            )

            afat_version_available = self.latest_version_available(
                package_name="allianceauth-afat"
            )

            # Check if updates for ImicusFAT are available
            if ifat_version_available is not None:
                if version_parse(ifat_version_installed) < version_parse(
                    ifat_version_available
                ):
                    self.stdout.write(
                        self.style.WARNING(
                            "ImicusFAT is outdated. "
                            "Please update to the latest ImicusFAT version first."
                        )
                    )

                    self.stdout.write(
                        self.style.WARNING(
                            f"ImicusFAT version installed: {ifat_version_installed}"
                        )
                    )

                    self.stdout.write(
                        self.style.WARNING(
                            f"ImicusFAT version available: {ifat_version_available}"
                        )
                    )

                    has_conflict = True
            else:
                has_conflict = True

            # Check if updates for aFAT are available
            if afat_version_available is not None:
                if version_parse(afat_version_installed) < version_parse(
                    afat_version_available
                ):
                    self.stdout.write(
                        self.style.WARNING(
                            "aFAT is outdated. "
                            "Please update to the latest aFAT version first."
                        )
                    )

                    self.stdout.write(
                        self.style.WARNING(
                            f"aFAT version installed: {afat_version_installed}"
                        )
                    )

                    self.stdout.write(
                        self.style.WARNING(
                            f"aFAT version available: {afat_version_available}"
                        )
                    )

                    has_conflict = True
            else:
                has_conflict = True

            if has_conflict is False:
                self.stdout.write(
                    "Importing all FAT/FAT link data from ImicusFAT module. "
                    "This can only be done once during the very first installation. "
                    "As soon as you have data collected with your AFAT module, "
                    "this import will fail!"
                )

                user_input = get_input("Are you sure you want to proceed? (yes/no)?")

                if user_input == "yes":
                    self.stdout.write("Starting import. Please stand by.")
                    self._import_from_imicusfat()
                else:
                    self.stdout.write(self.style.WARNING("Aborted."))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "ImicusFAT module is not active. "
                    "Please make sure you have it in your "
                    "INSTALLED_APPS in your local.py! "
                    "Aborting."
                )
            )
