"""
Database modules for connectivity for HEA resources. There is one module per supported database system. Each module must
have at least one function, init(app, config) that accepts a required aiohttp app object and an optional
configparser.ConfigParser object. The init function must set an application context property called db with an object
for executing database queries.
"""

