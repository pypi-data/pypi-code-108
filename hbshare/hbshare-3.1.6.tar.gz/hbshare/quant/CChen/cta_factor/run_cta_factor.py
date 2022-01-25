if __name__ == '__main__':
    from db_cons import sql_write_path_work, sql_user_work
    from hbshare.quant.CChen.cta_factor.hsjy_to_local import (
        hsjy_fut_pro_info,
        hsjy_fut_wr,
        hsjy_fut_com_info,
        hsjy_fut_com,
        hsjy_fut_member,
    )
    from hbshare.quant.CChen.cta_factor.hsjy_func import hsjy_fut_index
    from hbshare.quant.CChen.cta_factor.factor_index import run
    from hbshare.quant.CChen.cta_factor.factor_func import index_gen
    import hbshare as hbs

    hbs.set_token('830ca3e1998947f8a99ebb7f3e563623')

    hsjy_fut_pro_info(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_wr(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_com_info(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_com(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_member(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_index(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    run(
        sql_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    index_gen(
        sql_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
