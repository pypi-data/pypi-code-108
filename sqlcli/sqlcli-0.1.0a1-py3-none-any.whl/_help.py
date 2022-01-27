"""
A module to store help strings that are shared by multiple commands.
"""

database_url_help = """
A database connection string. If no connection string is provided sqlcli will
check for a connection string in the environment variable `DATABASE_URL`.
""".strip().replace(
    "\n", ""
)

models_path_help = """
The location of the python script(s) that contain the SQLModels. If no argument
is provided sqlcli will check for a path in the environment variable
`MODELS_PATH`.
""".strip().replace(
    "\n", ""
)

table_name_help = """
The name of the table to query.
""".strip().replace(
    "\n", ""
)
