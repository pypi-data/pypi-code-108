from .crud import KeycloakCRUD
from .targets import Targets
from .url import RestURL
import requests, json


def AuthenticationFlowURLBuilder(url):
    return Targets.makeWithURL(url).addResources(['flows'])

# The keycloak API is a bit crazy here they add with: 
# Post /parentId/executions/execution 
# 
# But they delete with: 
#
# DELETE /executions/<id>
#
# Sadly we need to customize the URL's in order to make it work.
#

def BuildAction(kcCRUD, parentFlow, actionType):
    parentFlowAlias = parentFlow['alias']
    kcCRUD.targets.addResourcesFor('create',[parentFlowAlias, 'executions', actionType])
    kcCRUD.targets.addResourcesFor('update',[parentFlowAlias, 'executions'])
    kcCRUD.targets.addResourcesFor('read',[parentFlowAlias, 'executions'])

    kcCRUD.targets.getDeleteMethod().replaceResource('flows', 'executions')

    return kcCRUD


class AuthenticationFlows(KeycloakCRUD):
    def setURL(self, url):
        super().setURL(url)
        self.targets.addResources(['flows'])


    def _load(self, token, targets): 
        flow = KeycloakCRUD()    
        flow.token = token 
        flow.targets = targets.copy()
        return flow

    # Generate a CRUD object pointing to /realm/<realm>/authentication/flow_alias/executions/flow
    def flows(self, authFlow):
        flow = self._load(self.token, self.targets)

        return BuildAction( 
                kcCRUD=flow, 
                parentFlow=authFlow,
                actionType='flow')

    # Generate a CRUD object pointing to /realm/<realm>/authentication/flow_alias/executions/execution
    def executions(self, execution):
        flow = self._load(self.token, self.targets)

        return BuildAction( 
                kcCRUD=flow, 
                parentFlow=execution,
                actionType='execution')

           





