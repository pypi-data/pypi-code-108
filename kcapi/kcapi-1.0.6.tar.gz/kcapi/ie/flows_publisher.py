class AuthFlowsPublisher(): 
    def __init__(self, authenticationFlowAPI): 
        self.flowAPI = authenticationFlowAPI

    def __flow(self, flow):
        alias = flow['displayName'] 
        pid = None if not 'provider' in flow else flow['providerId'] 
        provider = 'registration-page-flow' if not pid else pid 
        flow_type = 'basic-flow' if not pid else 'form-flow' 

        # WARN: The value description is not well validated in Keycloak, it can return 500.
        return {
                "alias":alias,
                "type": flow_type,
                "description":"empty", 
                "provider": provider,
        }

    def __executions(self, execution):
        provider = execution['providerId'] 
        return {'provider': provider} 

    def __isAuthFlow(self, body): 
        return 'authenticationFlow' in body 

    def __getNodeLevel(self, node):
        return node['level']

    def __updateOtherFields(self, parent, flow): 
        publishedFlows = parent.all()

        for publishedFlow in publishedFlows: 
            displayIsEqual = publishedFlow['displayName'] == flow['displayName']
            levelIsEqual = publishedFlow['level'] == flow['level']
            indexIsEqual = publishedFlow['index'] == flow['index']

            if displayIsEqual and levelIsEqual and indexIsEqual: 
                publishedFlow['requirement'] = flow['requirement']
                parent.update(obj=publishedFlow).isOk()
                return True


        return False


    def publish(self, rootNode, flows):  
        if not isinstance(flows, list):  
            raise Exception("Bad Parameters for Authentication Flow: auth_flow parameter should be an array.")

        rootNode = rootNode    
        nodes = { 0: rootNode } 
        current_level = 0

        rootFlow = self.flowAPI.executions(rootNode)
        
        for flow in flows:
            current_level = self.__getNodeLevel(flow)
            parent = nodes[current_level]

            if self.__isAuthFlow(flow):
               authenticationFlow = self.__flow(flow) 
               nodes[current_level + 1] = authenticationFlow
               self.flowAPI.flows(parent).create(authenticationFlow).isOk()
            else:
               execution = self.__executions(flow)
               self.flowAPI.executions(parent).create(execution).isOk()

        
            if not self.__updateOtherFields(rootFlow, flow):
                raise Exception('There is an inconsistency problem: Changes are not taking place in the server, latency problems ?.')



 
