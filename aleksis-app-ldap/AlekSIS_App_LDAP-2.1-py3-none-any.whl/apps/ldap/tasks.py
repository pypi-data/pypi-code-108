from aleksis.core.celery import app

from .util.ldap_sync import mass_ldap_import


@app.task
def ldap_import():
    mass_ldap_import()
