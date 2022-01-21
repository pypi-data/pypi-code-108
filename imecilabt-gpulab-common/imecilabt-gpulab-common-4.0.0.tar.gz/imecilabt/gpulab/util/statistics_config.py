from typing import Optional, Dict

from imecilabt.gpulab.util.gpulab_config import BaseConfig

class StatisticsConfig(BaseConfig):
    def __init__(self):
        super(StatisticsConfig, self).__init__()

        self.stats_active: bool = False
        self.stats_host: Optional[str] = None
        self.stats_username: Optional[str] = None
        self.stats_password: Optional[str] = None
        self.stats_database: Optional[str] = None
        self.stats_port: Optional[str] = None

        self.clickhouse_stats_active: bool = False
        self.clickhouse_stats_host: Optional[str] = None
        self.clickhouse_stats_username: Optional[str] = None
        self.clickhouse_stats_password: Optional[str] = None
        self.clickhouse_stats_database: Optional[str] = None
        self.clickhouse_stats_port: Optional[str] = None
        self.clickhouse_secure: bool = True

    def load_from_dict(self, cfg: Dict, *, backward_compatible=False):
        # super().load_from_dict(cfg, backward_compatible=backward_compatible)

        def mandatory(keys):
            raise Exception('Argument is required: {}   \n   Was not found in {}'.format(keys, cfg))

        self.stats_active = BaseConfig._get_bool_from_dict(cfg, False, 'stats', 'active')
        self.stats_host = BaseConfig._get_from_dict(cfg, mandatory if self.stats_active else None, 'stats', 'host')
        self.stats_username = BaseConfig._get_from_dict(cfg, mandatory if self.stats_active else None, 'stats', 'username')
        self.stats_password = BaseConfig._get_from_dict(cfg, mandatory if self.stats_active else None, 'stats', 'password')
        self.stats_database = BaseConfig._get_from_dict(cfg, mandatory if self.stats_active else None, 'stats', 'database')
        self.stats_port = BaseConfig._get_from_dict(cfg, 8086, 'stats', 'port')

        self.clickhouse_stats_active = BaseConfig._get_bool_from_dict(cfg, False, 'clickhouse_stats', 'active')
        self.clickhouse_stats_host = BaseConfig._get_from_dict(cfg, mandatory if self.clickhouse_stats_active else None, 'clickhouse_stats', 'host')
        self.clickhouse_stats_username = BaseConfig._get_from_dict(cfg, mandatory if self.clickhouse_stats_active else None, 'clickhouse_stats', 'username')
        self.clickhouse_stats_password = BaseConfig._get_from_dict(cfg, mandatory if self.clickhouse_stats_active else None, 'clickhouse_stats', 'password')
        self.clickhouse_stats_database = BaseConfig._get_from_dict(cfg, mandatory if self.clickhouse_stats_active else None, 'clickhouse_stats', 'database')
        self.clickhouse_stats_port = BaseConfig._get_from_dict(cfg, 9440, 'clickhouse_stats', 'port')
        self.clickhouse_secure = BaseConfig._get_from_dict(cfg, True, 'clickhouse_stats', 'secure')

    def save_to_dict(self) -> Dict:
        res = dict()
        BaseConfig._to_dict(res, self.stats_active, 'stats', 'active')
        BaseConfig._to_dict(res, self.stats_host, 'stats', 'host')
        BaseConfig._to_dict(res, self.stats_username, 'stats', 'username')
        BaseConfig._to_dict(res, self.stats_password, 'stats', 'password')
        BaseConfig._to_dict(res, self.stats_database, 'stats', 'database')
        BaseConfig._to_dict(res, self.stats_port, 'stats', 'port')

        BaseConfig._to_dict(res, self.clickhouse_stats_active, 'clickhouse_stats', 'active')
        BaseConfig._to_dict(res, self.clickhouse_stats_host, 'clickhouse_stats', 'host')
        BaseConfig._to_dict(res, self.clickhouse_stats_username, 'clickhouse_stats', 'username')
        BaseConfig._to_dict(res, self.clickhouse_stats_password, 'clickhouse_stats', 'password')
        BaseConfig._to_dict(res, self.clickhouse_stats_database, 'clickhouse_stats', 'database')
        BaseConfig._to_dict(res, self.clickhouse_stats_port, 'clickhouse_stats', 'port')
        BaseConfig._to_dict(res, self.clickhouse_secure, 'clickhouse_stats', 'secure')
        return res
