# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
# /usr/local/opt/python@3.7/bin/pip install hydra-core

from omegaconf import DictConfig, OmegaConf

import hydra


@hydra.main(config_path="conf", config_name="config")
def my_app(cfg: DictConfig) -> None:
    """
    python my_app.py +db.driver=mysql +db.user=omry +db.password=secret
    ++覆盖
    @param cfg:
    @return:
    """
    print(cfg)
    print(OmegaConf.to_yaml(cfg))


if __name__ == "__main__":
    my_app()
