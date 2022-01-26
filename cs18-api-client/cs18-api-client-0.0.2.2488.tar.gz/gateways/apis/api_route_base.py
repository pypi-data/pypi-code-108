from gateways.apis.api_about import ApiAbout
from gateways.apis.api_account import ApiAccount
from gateways.apis.api_account_cost import ApiAccountCost
from gateways.apis.api_achievements import ApiAchievements
from gateways.apis.api_agent_connector import ApiAgentConnector
from gateways.apis.api_artifacts_repository import ApiArtifactsRepository
from gateways.apis.api_blueprint import ApiBlueprint
from gateways.apis.api_blueprint_validation import ApiBlueprintValidation
from gateways.apis.api_catalog import ApiCatalog
from gateways.apis.api_cost import ApiCost
from gateways.apis.api_debugging import ApiDebugging
from gateways.apis.api_oauth_redirect import ApiOauthRedirect
from gateways.apis.api_parameter_store import ParameterStore
from gateways.apis.api_production import ApiProduction
from gateways.apis.api_qualiy import ApiQualiY
from gateways.apis.api_sandbox import ApiSandbox
from gateways.apis.api_settings import ApiSettings
from gateways.apis.api_spaces import ApiSpaces
from gateways.apis.api_token import ApiToken


class ApiRoot:
    def __init__(self, api_address: str, space: str = None, version: str = None):
        self.about = ApiAbout(api_address, version)
        self.account = ApiAccount(api_address, version)
        self.account_cost = ApiAccountCost(api_address, version)
        self.achievements = ApiAchievements(api_address, version)
        self.artifacts_repository = ApiArtifactsRepository(api_address, version)
        self.blueprint = ApiBlueprint(api_address, version)
        self.blueprint_validation = ApiBlueprintValidation(api_address, version)
        self.catalog = ApiCatalog(api_address, version)
        self.oauth_redirect = ApiOauthRedirect(api_address, version)
        self.production = ApiProduction(api_address, space, version)
        self.qualiy = ApiQualiY(api_address, space, version)
        self.sandbox = ApiSandbox(api_address, space, version)
        self.settings = ApiSettings(api_address, version)
        self.agent_connector = ApiAgentConnector(api_address, version)
        self.spaces = ApiSpaces(api_address, version)
        self.token = ApiToken(api_address, version)
        self.cost = ApiCost(api_address, version)
        self.debugging = ApiDebugging(api_address, version)
        self.parameterStore = ParameterStore(api_address, version)
