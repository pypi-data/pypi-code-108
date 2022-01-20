from .targets import Targets


# The Keycloak guys decided to use another resource DELETE /roles-by-id, instead of sticking to DELETE /roles.
def RolesURLBuilder(url):
    targets = Targets.makeWithURL(url)
    targets.getDeleteMethod().replaceResource('roles', 'roles-by-id')
    return targets