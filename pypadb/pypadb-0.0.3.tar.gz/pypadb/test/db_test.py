from conf import db_configurer
import connection_pool

if __name__ == '__main__':
    db_configurer.DbConfigurer().end()
    connection_pool.connection()