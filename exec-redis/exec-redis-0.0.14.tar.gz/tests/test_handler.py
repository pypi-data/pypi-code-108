from execredis import ExecMappingData
from tests.test_connection import redis_client


m = ExecMappingData(proj_name='test', redis_app=redis_client.redis)


class MappingData:
    PROJ_PREFIX = m.hget("PROJ_PREFIX", f"test.")


if __name__ == '__main__':
    # print(MappingData.PROJ_PREFIX)
    m.setup_mapping_data(MappingData, MappingData.PROJ_PREFIX, 'test1.')
