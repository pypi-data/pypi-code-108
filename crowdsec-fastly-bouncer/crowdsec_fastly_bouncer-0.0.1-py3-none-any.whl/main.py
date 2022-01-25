import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import signal
from pathlib import Path
from math import ceil
from time import sleep
from typing import List
from multiprocessing.pool import ThreadPool
from threading import Thread
from importlib.metadata import version

from pycrowdsec.client import StreamClient


from fastly_bouncer.fastly_api import ACL_CAPACITY, FastlyAPI
from fastly_bouncer.service import ACLCollection, Service
from fastly_bouncer.utils import (
    with_suffix,
    SUPPORTED_ACTIONS,
    get_default_logger,
    CustomFormatter,
)
from fastly_bouncer.config import (
    Config,
    ConfigGenerator,
    FastlyAccountConfig,
    FastlyServiceConfig,
    parse_config_file,
    print_config,
)


VERSION = version("crowdsec-fastly-bouncer")

acl_collections: List[ACLCollection] = []
services: List[Service] = []

logger: logging.Logger = get_default_logger()

exiting = False


def sigterm_signal_handler(signum, frame):
    global exiting
    exiting = True
    logger.info("exiting")


signal.signal(signal.SIGTERM, sigterm_signal_handler)
signal.signal(signal.SIGINT, sigterm_signal_handler)


def setup_fastly_infra(config: Config, cleanup_mode):
    p = Path(config.cache_path)
    if p.exists():
        logger.info("cache file exists")
        with open(config.cache_path) as f:
            s = f.read()

            if not s:
                logger.warning(f"cache file at {config.cache_path} is empty")
            else:
                cache = json.loads(s)
                services.extend(list(map(Service.from_jsonable_dict, cache)))
                logger.info(f"loaded exisitng infra using cache")
                if not cleanup_mode:
                    return
    else:
        p.parent.mkdir(exist_ok=True, parents=True)

    if cleanup_mode:
        logger.info("cleaning fastly infra")
    else:
        logger.info("setting up fastly infra")

    def setup_account(account_cfg: FastlyAccountConfig):
        fastly_api = FastlyAPI(token=account_cfg.account_token)

        def setup_service(service_cfg: FastlyServiceConfig) -> Service:
            if service_cfg.clone_reference_version or (
                cleanup_mode
                and fastly_api.is_service_version_locked(
                    service_cfg.id, service_cfg.reference_version
                )
            ):
                comment = None
                if cleanup_mode:
                    comment = "Clone cleaned from CrowdSec resources"
                version = fastly_api.clone_version_for_service_from_given_version(
                    service_cfg.id, service_cfg.reference_version, comment
                )
                logger.info(
                    with_suffix(
                        f"new version {version} for service created",
                        service_id=service_cfg.id,
                    )
                )
            else:
                version = service_cfg.reference_version
                logger.info(
                    with_suffix(
                        f"using existing version {service_cfg.reference_version}",
                        service_id=service_cfg.id,
                    )
                )

            logger.info(
                with_suffix(
                    f"cleaning existing crowdsec resources (if any)",
                    service_id=service_cfg.id,
                    version=version,
                )
            )

            fastly_api.clear_crowdsec_resources(service_cfg.id, version)
            if cleanup_mode:
                return

            logger.info(
                with_suffix(
                    f"cleaned existing crowdsec resources (if any)",
                    service_id=service_cfg.id,
                    version=version,
                )
            )

            def setup_action_for_service(action: str) -> ACLCollection:
                acl_count = ceil(service_cfg.max_items / ACL_CAPACITY)
                acl_collection = ACLCollection(
                    api=fastly_api,
                    service_id=service_cfg.id,
                    version=version,
                    action=action,
                    state=set(),
                )
                logger.info(
                    with_suffix(
                        f"creating acl collection of {acl_count} acls for {action} action",
                        service_id=service_cfg.id,
                    )
                )
                acl_collection.create_acls(acl_count)
                logger.info(
                    with_suffix(
                        f"created acl collection for {action} action",
                        service_id=service_cfg.id,
                    )
                )
                return acl_collection

            with ThreadPool(len(SUPPORTED_ACTIONS)) as tp:
                acl_collections = tp.map(setup_action_for_service, SUPPORTED_ACTIONS)
                acl_collection_by_action = {
                    acl_collection.action: acl_collection for acl_collection in acl_collections
                }

            return Service(
                api=fastly_api,
                recaptcha_secret=service_cfg.recaptcha_secret_key,
                recaptcha_site_key=service_cfg.recaptcha_site_key,
                acl_collection_by_action=acl_collection_by_action,
                service_id=service_cfg.id,
                version=version,
                activate=service_cfg.activate,
                captcha_expiry_duration=service_cfg.captcha_cookie_expiry_duration,
            )

        with ThreadPool(len(account_cfg.services)) as service_tp:
            services.extend(list(service_tp.map(setup_service, account_cfg.services)))

    with ThreadPool(len(config.fastly_account_configs)) as account_tp:
        account_tp.map(setup_account, config.fastly_account_configs)


def set_logger(config: Config):
    global logger
    list(map(logger.removeHandler, logger.handlers))
    logger.setLevel(config.get_log_level())
    if config.log_mode == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif config.log_mode == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    elif config.log_mode == "file":
        handler = RotatingFileHandler(config.log_file, mode="a+")
    formatter = CustomFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info(f"Starting fastly-bouncer-v{VERSION}")


def run(config: Config):
    crowdsec_client = StreamClient(
        lapi_url=config.crowdsec_config.lapi_url,
        api_key=config.crowdsec_config.lapi_key,
        scopes=["ip", "range", "country", "as"],
        interval=config.update_frequency,
    )

    crowdsec_client.run()
    sleep(2)  # Wait for initial polling by bouncer, so we start with a hydrated state
    while True and not exiting:
        new_state = crowdsec_client.get_current_decisions()
        with ThreadPool(len(services)) as tp:
            tp.map(lambda service: service.transform_state(new_state), services)
        new_states = list(map(lambda service: service.as_jsonable_dict(), services))
        with open(config.cache_path, "w") as f:
            f.write(json.dumps(new_states, indent=4))
        if exiting:
            return
        sleep(config.update_frequency)


def start(config: Config, cleanup_mode):
    setup_fastly_infra(config, cleanup_mode)
    if cleanup_mode:
        if Path(config.cache_path).exists():
            logger.info("cleaning cache")
            with open(config.cache_path, "w") as f:
                pass
        return
    run(config)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-c",
        type=Path,
        help="Path to configuration file.",
        default=Path("/etc/crowdsec/bouncers/crowdsec-fastly-bouncer.yaml"),
    )
    arg_parser.add_argument("-d", help="Whether to cleanup resources.", action="store_true")
    arg_parser.add_argument("-g", type=str, help="Comma separated tokens to generate config for.")
    arg_parser.add_argument("-o", type=str, help="Path to file to output the generated config.")
    arg_parser.add_help = True
    args = arg_parser.parse_args()
    if not args.c.exists():
        print(f"config at {args.c} doesn't exist", file=sys.stderr)
        if args.g:
            gc = ConfigGenerator().generate_config(args.g)
            print_config(gc, args.o)
            sys.exit(0)

        arg_parser.print_help()
        sys.exit(1)
    try:
        config = parse_config_file(args.c)
        if args.d:  # We want to display this to stderr
            config.log_mode = "stderr"
        set_logger(config)
    except Exception as e:
        logger.error(f"got error {e} while parsing config at {args.c}")
        sys.exit(1)

    if args.g:
        gc = ConfigGenerator().generate_config(args.g, base_config=config)
        print_config(gc, args.o)
        sys.exit(0)

    logger.info("parsed config successfully")
    t1 = Thread(target=start, args=([config, args.d]))
    t1.start()


if __name__ == "__main__":
    main()
