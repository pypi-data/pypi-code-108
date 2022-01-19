from django.core.management.base import BaseCommand, CommandError
import os
import string
import random
import subprocess
import importlib.util


class Command(BaseCommand):
    help = "Prints a list of environment variables for eb setenv"

    def add_arguments(self, parser):
        parser.add_argument("environment", type=str)

    def handle(self, *args, **options):
        local_settings = "local_settings.py"
        try:
            if not os.path.isfile(local_settings):
                for dd in os.listdir():
                    if os.path.isdir(dd):
                        test_path = os.path.join(dd, local_settings)
                        if os.path.isfile(test_path):
                            local_settings = test_path
                            break
            if not os.path.isfile(local_settings):
                print("\n\nCould not find local_settings.py\n")
                exit(1)
        except Exception as ee:
            print(f"ERROR: {ee}")
            exit(1)

        try:
            print(f"Using {local_settings}")
            app_name = os.path.dirname(local_settings)
            print(f"Application: {app_name}\n")

            # Generate a new secret key
            chars = (
                string.ascii_uppercase
                + string.ascii_lowercase
                + string.digits
                + "!@#$%^&*"
            )
            secret_key = "".join(random.choice(chars) for _ in range(50))

            # Prepare expected vars and default values where possible
            env = options["environment"].upper()
            eb_vars = {
                "CAS_SERVER_URL": f"https://sso{'-stage.oit' if env == 'STAGE' else ''}.pdx.edu/idp/profile/cas/login",
                "DEBUG": False,
                "DJANGO_SETTINGS_MODULE": f"{app_name}.settings",
                "EMAIL_HOST_USER": "cefr-app-mail",
                "ENVIRONMENT": env,
                "FINTI_TOKEN": None,
                "FINTI_URL": f"https://ws{'-test' if env == 'STAGE' else ''}.oit.pdx.edu",
                "SECRET_KEY": secret_key,
                "HOST_NAME": None,
                "USE_SENTRY": True,
                # Guess at URL:
                "HOST_URL": f"{app_name}{'-stage' if env == 'STAGE' else ''}.campus.wdt.pdx.edu",
            }

            # Import values from local_settings.py
            spec = importlib.util.spec_from_file_location("*", local_settings)
            settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings)

            # Get eb environment status to find host_name
            # Run command
            print("Checking eb status...")
            process = subprocess.Popen(
                ["eb", "status"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )
            (output, stderr) = process.communicate()

            # If not initialized
            if output and 'You must first run "eb init"' in str(output):
                print(
                    "You must run 'eb init' before you can generate environment variables"
                )
                exit(2)

            if output:
                for ll in output.decode("utf-8").splitlines():
                    line = ll.strip()
                    if line.startswith("CNAME"):
                        eb_vars["HOST_NAME"] = line.replace("CNAME:", "").strip()
                        break

            # Ignore some settings:
            ignored = [
                "ALLOWED_HOSTS",
                "SECRET_KEY",
                "DEBUG",
                "ENVIRONMENT",
                "USE_SENTRY",
                "CAS_SERVER_URL",
                "FINTI_URL",  # Different than values used in development
                "FINTI_SAVE_RESPONSES",
                "FINTI_SIMULATE_WHEN_POSSIBLE",
                "DISABLE_GRAVATAR",
                "ELEVATE_DEVELOPER_ACCESS",
                "SESSION_COOKIE_AGE",
            ]

            for var_name in dir(settings):
                if var_name in ignored:
                    continue
                # Only use uppercase attributes (settings)
                if var_name != var_name.upper():
                    continue

                eb_vars[var_name] = getattr(settings, var_name)

            print("\n\nReview Generated Settings:")
            for ss, vv in eb_vars.items():
                print(f"  {ss} = {vv}")

            print("\n\nCommand:\n")
            print("eb setenv", end=" ")
            for ss, vv in eb_vars.items():
                print(f"{ss}='{vv}'", end=" ")
            print("\n\n")

        except Exception as ee:
            print(f"ERROR: {ee}")
            exit(3)
