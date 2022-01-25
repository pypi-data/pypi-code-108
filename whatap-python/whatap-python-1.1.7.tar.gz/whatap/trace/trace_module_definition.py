PLUGIN = {}
IMPORT_HOOKS = {}



DEFINITION = {
    'plugin': [
        ('', 'instrument_plugin'),
    ],
    'httpc_httplib': [
        ('httplib', 'instrument_httplib'),
        ('http.client', 'instrument_httplib'),
        ('httplib2', 'instrument_httplib2'),
    ],
    'httpc_requests': [
        ('requests.sessions', 'instrument_requests'),
    ],
    'httpc_urllib3': [
        ('urllib3.request', 'instrument_urllib3'),
        # ('requests.packages.urllib3.request', 'instrument_urllib3'),
    ],
    'httpc_django': [
        ('revproxy.views', 'instrument_revproxy_views'),
    ],
    'database_mysql': [
        ('MySQLdb', 'instrument_MySQLdb'),
        ('MySQLdb.cursors', 'instrument_MySQLdb_cursors'),
        ('pymysql', 'instrument_pymysql'),
        ('pymysql.cursors', 'instrument_pymysql_cursors'),
    ],
    'database_postgresql': [
        ('psycopg2', 'instrument_psycopg2'),
        ('psycopg2._psycopg', 'instrument_psycopg2_connection'),
        ('psycopg2.extensions', 'instrument_psycopg2_extensions'),
    ],
    'database_toolkit': [
        ('sqlalchemy.orm.session', 'instrument_sqlalchemy'),
        ('sqlalchemy.engine.default', 'instrument_sqlalchemy_engine'),
        ('sqlalchemy.engine.create', 'instrument_sqlalchemy_engine_basic'),
        ('sqlalchemy.engine', 'instrument_sqlalchemy_engine_basic'),
    ],
    'application_wsgi': [
        ('', ''),
    ],
    'application_bottle': [
        ('bottle', 'instrument'),
    ],
    'application_cherrypy': [
        ('cherrypy', 'instrument'),
    ],
    'application_django': [
        ('django.core.handlers.wsgi', 'instrument'),
        ('django.core.handlers.base', 'instrument_handlers_base'),
        ('django.views.generic.base', 'instrument_generic_base'),
        ('django.contrib.staticfiles.handlers', 'instrument_handlers_static'),

        # Django==1.10
        ('django.urls.resolvers', 'instrument_url_resolvers', False),
        ('django.urls.base', 'instrument_urls_base', False),
        ('django.core.handlers.exception', 'instrument_handlers_exception',
         False),
    ],
    'application_flask': [
        ('flask', 'instrument'),
    ],
    'application_tornado': [
        ('tornado.web', 'instrument'),
    ],
    'application_celery': [
        # ('celery.task.base', 'instrument_task_base'),
        #('celery.app.task', 'instrument_app_task'),
        #('celery.worker', 'instrument_celery_worker'),
        #('celery.concurrency.processes', 'instrument_celery_worker'),
        #('celery.concurrency.prefork', 'instrument_celery_worker'),
        ('celery.execute.trace', 'instrument_celery_execute_trace'),
        ('celery.task.trace', 'instrument_celery_execute_trace'),
        ('celery.app.trace', 'instrument_celery_execute_trace'),
        #('billiard.pool', 'instrument_billiard_pool'),
    ],
    'database_redis':[
        ('redis','instrument_redis_connection'),
    ],
    'email_smtp':[
        ('smtplib','instrument_smtp'),
    ],
    # 'amqp_kombu':[
    #     ('kombu','instrument_kombu'),
    # ],
    'amqp_pika':[
        ('pika.channel','instrument_pika'),
    ],
    'application_nameko': [
        ('nameko.containers', 'instrument_nameko_spawn_worker'),
        ('spsengine.containers', 'instrument_nameko_spawn_worker'),
    ],
    'application_graphql':[
        #('graphql','instrument_graphql'),
        ('graphql.execution.executor','instrument_graphql'),
    ],
    'database_mongo':[
        ('pymongo','instrument_mongo_client'),
    ],
}
