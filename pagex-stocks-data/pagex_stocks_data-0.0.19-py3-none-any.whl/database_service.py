from sqlalchemy import update
import pandas as pd
from pandas import DataFrame


def create(entity) -> None:
    from pagexdata.database import db_session
    try:
        db_session.add(entity)
        db_session.commit()
        db_session.close()
    except Exception as ex:
        db_session.rollback()
        raise ex


def create_all(entity_list) -> None:
    from pagexdata.database import db_session
    try:
        db_session.add_all(entity_list)
        db_session.commit()
        db_session.close()
    except Exception as ex:
        db_session.rollback()
        raise ex


def read_all(entity_class_):
    from pagexdata.database import db_session
    result = db_session.query(entity_class_).all()
    db_session.close()
    return result


def read_all_by(entity_class_, query_filter=None, query_order_by=None, order_by_desc=False):
    from pagexdata.database import db_session
    query = db_session.query(entity_class_)
    if query_filter is not None:
        query = query.filter(*query_filter)
    if query_order_by is not None and order_by_desc:
        query = query.order_by(query_order_by.desc())
    elif query_order_by is not None and not order_by_desc:
        query = query.order_by(query_order_by)
    result = query.all()
    db_session.close()
    return result


# def read_all_by(entity_class_, query_filter, query_order_by, desc=False):
#     from pagexdata.database import db_session
#     #stmt = select(users_table).order_by(desc(users_table.c.name))
#     result = db_session.query(entity_class_).filter(*query_filter).order_by(query_order_by)
#     db_session.close()
#     return result


def read_all_as_dataframe(entity_class_) -> DataFrame:
    from pagexdata.database import url
    return pd.read_sql(entity_class_.__tablename__, url.render_as_string(hide_password=False))


def delete_all(entity_class_) -> None:
    from pagexdata.database import db_session
    try:
        result = db_session.query(entity_class_).all()
        for element in result:
            db_session.delete(element)
            db_session.commit()
            db_session.close()
    except Exception as ex:
        db_session.rollback()
        raise ex


def update_reddit_hits_ranking(date, subreddits, ticker_symbols, df, dataframe_reddithit_columns):
    from pagexdata.database import db_session
    try:
        from pagexdata.entities import RedditHits
        for subreddit in subreddits:
            for symbol in ticker_symbols:
                key = (df[dataframe_reddithit_columns.COLUMN_DATE] == date) & \
                      (df[dataframe_reddithit_columns.COLUMN_TICKER_SYMBOL] == symbol) & \
                      (df[dataframe_reddithit_columns.COLUMN_SUBREDDIT] == subreddit)
                db_session.execute(update(RedditHits)
                    .where(RedditHits.date == date)
                    .where(RedditHits.subreddit == subreddit)
                    .where(RedditHits.ticker_symbol == symbol)
                    .values(rank=int(df.loc[key][dataframe_reddithit_columns.COLUMN_RANK]),
                            previous_rank=int(df.loc[key][dataframe_reddithit_columns.COLUMN_PREVIOUS_RANK]),
                            change_rank=int(df.loc[key][dataframe_reddithit_columns.COLUMN_CHANGE_RANK]),
                            change_hits_one_day=int(df.loc[key][dataframe_reddithit_columns.COLUMN_CHANGE_HITS_1_DAY]),
                            change_hits_two_days=int(df.loc[key][dataframe_reddithit_columns.COLUMN_CHANGE_HITS_2_DAYS]),
                            change_hits_three_days=int(df.loc[key][dataframe_reddithit_columns.COLUMN_CHANGE_HITS_3_DAYS]),
                            change_hits_one_week=int(df.loc[key][dataframe_reddithit_columns.COLUMN_CHANGE_HITS_1_WEEK]),
                            change_hits_two_weeks=int(df.loc[key][dataframe_reddithit_columns.COLUMN_CHANGE_HITS_2_WEEKS]),
                            change_hits_four_weeks=int(df.loc[key][dataframe_reddithit_columns.COLUMN_CHANGE_HITS_4_WEEKS]),
                            hits_volatility_one_week=float(df.loc[key][dataframe_reddithit_columns.COLUMN_HITS_VOLATILITY_1_WEEK]),
                            hits_volatility_two_weeks=float(df.loc[key][dataframe_reddithit_columns.COLUMN_HITS_VOLATILITY_2_WEEKS])))
        db_session.commit()
        db_session.close()
    except Exception as ex:
        db_session.rollback()
        raise ex
