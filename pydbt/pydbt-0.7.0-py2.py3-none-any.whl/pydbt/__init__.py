from dbt.version import get_installed_version

dbt_version = get_installed_version()
dbt_version = str(dbt_version).replace("=", "")
