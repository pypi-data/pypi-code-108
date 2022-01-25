import logging
from dataclasses import asdict, dataclass, field
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List, Dict

import yaml

from fastly_bouncer.utils import are_filled_validator
from fastly_bouncer.fastly_api import FastlyAPI


@dataclass
class CrowdSecConfig:
    lapi_key: str
    lapi_url: str = "http://localhost:8080/"

    def __post_init__(self):
        are_filled_validator(**{key: getattr(self, key) for key in asdict(self).keys()})


@dataclass
class FastlyServiceConfig:
    id: str
    recaptcha_site_key: str
    recaptcha_secret_key: str
    reference_version: str
    clone_reference_version: bool = True
    activate: bool = False
    max_items: int = 5000
    captcha_cookie_expiry_duration: str = "1800"

    def __post_init__(self):
        are_filled_validator(**{key: getattr(self, key) for key in asdict(self).keys()})


@dataclass
class FastlyAccountConfig:
    account_token: str
    services: List[FastlyServiceConfig]


def fastly_config_from_dict(data: Dict) -> List[FastlyAccountConfig]:
    account_configs: List[FastlyAccountConfig] = []
    for account_cfg in data:
        service_configs: List[FastlyServiceConfig] = []
        for service_cfg in account_cfg["services"]:
            service_configs.append(FastlyServiceConfig(**service_cfg))
        account_configs.append(
            FastlyAccountConfig(
                account_token=account_cfg["account_token"], services=service_configs
            )
        )
    return account_configs


@dataclass
class Config:
    log_level: str
    log_mode: str
    log_file: str
    update_frequency: int
    crowdsec_config: CrowdSecConfig
    cache_path: str = "/var/lib/crowdsec/crowdsec-fastly-bouncer/cache/fastly-cache.json"
    fastly_account_configs: List[FastlyAccountConfig] = field(default_factory=list)

    def get_log_level(self) -> int:
        log_level_by_str = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
        }
        return log_level_by_str.get(self.log_level.lower())

    def __post_init__(self):
        for i, account_config in enumerate(self.fastly_account_configs):
            if not account_config.account_token:
                raise ValueError(f" {i+1}th has no token specified in config")
            if not account_config.services:
                raise ValueError(f" {i+1}th has no service specified in config")


def parse_config_file(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Config file at {path} doesn't exist")
    with open(path) as f:
        data = yaml.safe_load(f)
        return Config(
            crowdsec_config=CrowdSecConfig(**data["crowdsec_config"]),
            fastly_account_configs=fastly_config_from_dict(data["fastly_account_configs"]),
            log_level=data["log_level"],
            log_mode=data["log_mode"],
            log_file=data["log_file"],
            update_frequency=int(data["update_frequency"]),
            cache_path=data["cache_path"],
        )


def default_config():
    return Config(
        log_level="info",
        log_mode="stdout",
        log_file="/var/log/crowdsec-fastly-bouncer.log",  # FIXME: This needs root permissions
        crowdsec_config=CrowdSecConfig(lapi_key="<LAPI_KEY>"),
        update_frequency="10",
    )


class ConfigGenerator:
    service_name_by_service_id: Dict[str, str] = {}

    @staticmethod
    def generate_config(
        comma_separated_fastly_tokens: str, base_config: Config = default_config()
    ) -> Config:
        fastly_tokens = comma_separated_fastly_tokens.split(",")
        fastly_tokens = list(map(lambda token: token.strip(), fastly_tokens))
        with ThreadPool(len(fastly_tokens)) as tp:
            account_configs = tp.map(ConfigGenerator.generate_config_for_account, fastly_tokens)
        base_config.fastly_account_configs = account_configs
        return ConfigGenerator.add_comments(yaml.safe_dump(asdict(base_config)))

    @staticmethod
    def add_comments(config: str):
        lines = config.split("\n")
        for i, line in enumerate(lines):
            for (
                service_id,
                service_name,
            ) in ConfigGenerator.service_name_by_service_id.items():
                has_service_id = False
                if service_id in line:
                    lines[i] = f"{line}  # {service_name}"
                    has_service_id = True
                    break
                if has_service_id:
                    break

            if "activate:" in line:
                lines[i] = f"{line}  # Set to true, to activate the new config in production"
                continue

            if "clone_reference_version:" in line:
                lines[
                    i
                ] = f"{line}  # Set to false, to modify 'reference_version' instead of cloning it "
                continue

            if "reference_version:" in line:
                lines[i] = f"{line}  # Service version to clone/modify"
                continue

            if "captcha_cookie_expiry_duration" in line:
                lines[
                    i
                ] = f"{line}  # Duration(in second) to persist the cookie containing proof of solving captcha"
                continue

        return "\n".join(lines)

    def generate_config_for_service(api: FastlyAPI, service_id: str):
        ref_version = api.get_version_to_clone(service_id)
        return FastlyServiceConfig(
            id=service_id,
            recaptcha_site_key="<RECAPTCHA_SITE_KEY>",
            recaptcha_secret_key="<RECAPTCHA_SECRET_KEY>",
            activate=False,
            clone_reference_version=True,
            reference_version=ref_version,
        )

    def generate_config_for_account(fastly_token: str) -> FastlyAccountConfig:
        api = FastlyAPI(fastly_token)
        service_ids_with_name = api.get_all_service_ids(with_name=True)
        for service_id, service_name in service_ids_with_name:
            ConfigGenerator.service_name_by_service_id[service_id] = service_name
        service_ids = list(map(lambda x: x[0], service_ids_with_name))
        service_configs: List[FastlyServiceConfig] = []

        with ThreadPool(len(service_ids)) as tp:
            args = [(api, service_id) for service_id in service_ids]
            service_configs = tp.starmap(ConfigGenerator.generate_config_for_service, args)

        return FastlyAccountConfig(account_token=fastly_token, services=service_configs)


def print_config(cfg, o_arg):
    if not o_arg:
        print(cfg)
    else:
        with open(o_arg, "w") as f:
            f.write(cfg)
