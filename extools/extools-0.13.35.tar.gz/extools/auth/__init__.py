"""Authentication helpers."""
try:
    from accpac import *
except ImportError as e:
    pass

def has_permission(program, resource, user=None, org=None, version=None):
    if not user:
        user = user()
    if not org:
        org = org()
    if not version:
        version = "67A"  # TODO: get the current version from the DB.

    # Sage allows the user to be assigned one group per program (i.e. VI)
    # Determine the user's group for the program.
    try:
        with exview("AS0002", seek_to={"PGMID": program,
                                       "COMPANYID": org,
                                       "USERID": user}) as exv:
            group = exv.get("PROFILEID")
    except ExViewRecordDoesNotExistError as e:
        # The user has not been assigned a group for the program, no access.
        return False

    # The user has a group, does that group have the permission we need?
    try:
        with exview("AS0001", seek_to={"PGMID": program,
                                       "PGMVER": version,
                                       "PROFILEID": group,
                                       "RESOURCEID": resource}) as exv:
            # There exists such a record, the group can access the resource.
            return True
    except ExViewRecordDoesNotExistError as e:
        # The user has not been permission to the resource, no access.
        return False



