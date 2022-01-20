from .targets import Targets


def IdentityProviderURLBuilder(url):
    targets = Targets.makeWithURL(url)
    targets.removeLast()
    targets.addResources(['identity-provider' , 'instances'])

    return targets
