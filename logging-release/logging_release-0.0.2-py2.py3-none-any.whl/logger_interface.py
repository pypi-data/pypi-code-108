from .logger import set_logger_level
from .logger_manager import LoggerManager


def set_main_logger_name(name: str):
    LoggerManager.set_main_logger_name(name)


def main_set_level(level):
    set_logger_level(LoggerManager.main_logger_name, level)


def main_info(message, indent_level=1):
    LoggerManager.main_logger.info(message, indent_level)


def main_debug(message, indent_level=1):
    LoggerManager.main_logger.debug(message, indent_level)


def main_warning(message, indent_level=1):
    LoggerManager.main_logger.warning(message, indent_level)


def main_exception(message, indent_level=1):
    LoggerManager.main_logger.exception(message, indent_level)


def main_critical(message, indent_level=1):
    LoggerManager.main_logger.critical(message, indent_level)


def main_tqdm(generator, desc="", indent_level=1, logger=LoggerManager().main_logger):
    """a TQDM style wrapper for logging something like a loop.
    e.g.
    for item in main_tqdm(alist, desc=""):
        do something

    Parameters
    ----------
    generator : [type]
        same as what you put in tqdm
    desc : str, optional
        description of your progress
    """
    return LoggerManager.progress_logger(generator, logger=logger, progress_name=desc, indent_level=indent_level)


def main_log_time():
    LoggerManager.main_logger.log_time()


def main_silence():
    LoggerManager.main_logger.setLevel(logging.CRITICAL + 100)


def main_finish_progress(progress_name=""):
    LoggerManager.main_logger.finish_progress(progress_name=progress_name)


def main_info_insert_adata(key, adata_attr="obsm", indent_level=1, *args, **kwargs):
    LoggerManager.main_logger.info_insert_adata(key, adata_attr=adata_attr, indent_level=indent_level, *args, **kwargs)


def main_info_insert_adata_var(key, indent_level=1, *args, **kwargs):
    main_info_insert_adata(key, "var", indent_level, *args, **kwargs)


def main_info_insert_adata_uns(key, indent_level=1, *args, **kwargs):
    main_info_insert_adata(key, "uns", indent_level, *args, **kwargs)


def main_info_insert_adata_obsm(key, indent_level=1, *args, **kwargs):
    main_info_insert_adata(key, "obsm", indent_level, *args, **kwargs)


def main_info_insert_adata_obs(key, indent_level=1, *args, **kwargs):
    main_info_insert_adata(key, "obs", indent_level, *args, **kwargs)


def main_info_insert_adata_layer(key, indent_level=1, *args, **kwargs):
    main_info_insert_adata(key, "layers", indent_level, *args, **kwargs)


def main_info_verbose_timeit(msg):
    LoggerManager.main_logger.info(msg)
