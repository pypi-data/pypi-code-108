from jcutil.server.envars import CONFIG_PATH
import logging
from jcutil import consul as kv, chalk
from jcutil.drivers import smart_load


context = {}


def load_config(*args, v=True):
    """
    初始化配置，并自动加载配置中的各种底层驱动

    **如只需要读取配置信息，请勿使用此方法**
    Parameters
    ----------
    v
    args

    Returns
    -------

    """
    print(CONFIG_PATH)
    conf = kv.fetch_key(CONFIG_PATH, fmt=kv.ConfigFormat.Yaml)
    if len(args) > 0:
        needed_conf = {}
        for key in ['server', *args]:
            assert key in conf, f'not found [{key}] in kv server.'
            needed_conf[key] = conf[key]
        conf = needed_conf
    v and print(chalk.GreenChalk(conf))
    try:
        smart_load(conf)
        context['conf'] = conf
    except Exception as err:
        logging.error('read config failed: %s', err)
