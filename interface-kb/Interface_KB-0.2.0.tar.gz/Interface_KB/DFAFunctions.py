#interface objects
from .InterfaceObjects import ASG,StopCondition,DFARule
#import helper functions
from .HelperFunctions import *

#-----------------------------------------------------------------------------------------------------------
#
#   DFA extension
#
#       TODO:
#
# -----------------------------------------------------------------------------------------------------------
def getASG_DFARules( AssemblySystemName, component,model):
    """
             Function to fetch the linked DFA rules within the ASG component
             The function returns a list of interface blocks of the DFA rule

             :param string AssemblySystemName: Name identifier of the assemlbySystem
             :param object model: Metamodel instance model
             :param string component: identify the ASG element ("Selector"|"Evaluator")

             :return objectList DFARuleList: list of interface object of the DFA rule (-1 = error)
    """
    # match the AssemblySystem-of-interest
    DFARuleList = []
    if len(model.includesAssemblySystem.items) != 0:
        # match the assemblySystem by Name
        for assemblySystem in model.includesAssemblySystem.items:
            if AssemblySystemName == assemblySystem.hasName:
                # check if ASG config exist
                if assemblySystem.hasAssemblyAlgorithmConfiguration is not None:
                    ASG_temp = assemblySystem.hasAssemblyAlgorithmConfiguration
                    if component == "Selector":
                        # check if rule selector is available
                        try:
                            cmp = ASG_temp.hasRuleSelector
                            DFARuleList = getDFArules(cmp)
                            return DFARuleList
                        except:
                            x = "No Rule selector available"
                            pass

                    if component == "Evaluator":
                        # check if rule selector is available
                        try:
                            cmp = ASG_temp.hasRuleEvaluator
                            DFARuleList = getDFArules(cmp)
                            return DFARuleList
                        except:
                            x = "No Rule evaluator available"
                            pass

                else:
                    return -1  # error - No ASG = No DFA rules

def updateASG_DFARules( AssemblySystemName, component,rule,model,KBPath):
    """
      Function to update the linked DFA rules within the ASG component
      The DFA rule interface object is used to interface with the function.
      The function returns whether or not the function is performed correctly

      :param string AssemblySystemName: Name identifier of the assemlbySystem
      :param string component: identify the ASG element ("Selector"|"Evaluator")
      :param object DFARule: Interface object of the DFA rule model
      :param object model: Metamodel instance model
      :param string KBPath: Absolute path to the metamodel instance model

      :return int Error: -1 = error, 1= function performed correcly
    """
    # match the AssemblySystem-of-interest
    DFARuleList = []
    if len(model.includesAssemblySystem.items) != 0:
        # match the assemblySystem by Name
        for assemblySystem in model.includesAssemblySystem.items:
            if AssemblySystemName == assemblySystem.hasName:
                # check if ASG config exist
                if assemblySystem.hasAssemblyAlgorithmConfiguration is not None:
                    ASG_temp = assemblySystem.hasAssemblyAlgorithmConfiguration
                    if component=="Selector":
                        #check if rule selector is available
                        try:
                            cmp = ASG_temp.hasRuleSelector
                            updateDFArule(cmp,rule)
                            updateKBv6(KBPath,model)
                        except:
                            x = "No Rule selector available"
                            pass

                    if component=="Evaluator":
                        #check if rule selector is available
                        try:
                            cmp = ASG_temp.hasRuleEvaluator
                            updateDFArule(cmp, rule)
                            updateKBv6(KBPath,model)
                        except:
                            x = "No Rule evaluator available"
                            pass

                else:
                    return -1   #error - No ASG = No DFA rules
    else:
        return -1

def getDFArules( ruleContainer):
    """
      For internal use only!
    """
    ruleList = []  # rulelist = [rule1,rule2,...,rulen] with rule = [name,description,isAppliedToProduct,isAppliedToProductPart,isAppliedToAssemblySequence,hasScorePropagation,hasScoreType,[DFArule.hasPreprocessesData.items[0].hasDataType,DFArule.hasPreprocessesData.items[0].hasDataReference]]
    for DFArule in ruleContainer.hasDFARule.items:
        ruleDefinition = []

        x = str(type(DFArule))
        if 'DFA_MaxValue' in x:
            ruleDefinition.append("DFA_MaxValue")
        elif 'DFA_MinValue' in x:
            ruleDefinition.append("DFA_MinValue")
        elif 'DFA_BoundValue' in x:
            ruleDefinition.append("DFA_BoundValue")
        elif 'DFA_StandardParts' in x:
            ruleDefinition.append("DFA_StandardParts")
        elif 'DFA_Translation' in x:
            ruleDefinition.append(DFArule.hasTranslationType)
        elif 'DFA_Gravity' in x:
            ruleDefinition.append("DFA_Gravity")
        elif 'DFA_Misplacement' in x:
            ruleDefinition.append("DFA_Misplacement")
        elif 'DFA_Tool' in x:
            ruleDefinition.append("DFA_Tool")
        elif 'DFA_Reachability' in x:
            ruleDefinition.append("DFA_Reachability")
        elif 'DFA_Visibility' in x:
            ruleDefinition.append("DFA_Visibility")
        else:
            ruleDefinition.append("Generic_DFA")
        ruleDefinition.append(DFArule.hasName)
        ruleDefinition.append(DFArule.hasDescription)
        ruleDefinition.append(DFArule.isAppliedToProduct)
        ruleDefinition.append(DFArule.isAppliedToProductPart)
        ruleDefinition.append(DFArule.isAppliedToAssemblySequence)
        ruleDefinition.append(DFArule.hasScorePropagation)
        ruleDefinition.append(DFArule.hasScoreType)
        if DFArule.hasPreprocessedData is not None:  # TODO:check if with items or not
            ruleDefinition.append([DFArule.hasPreprocessesData.items[0].hasDataType,
                                   DFArule.hasPreprocessesData.items[0].hasDataReference])
        optionList = []
        if len(DFArule.hasOption.items) != 0:  # TODO:check if with items or not
            for option in DFArule.hasOption.items:
                optList = []
                try:
                    if option.hasValue is not None:  # TODO: check if we can do this like that!
                        optList.append(option.hasValue)
                except:
                    x = 10
                try:
                    if option.hasX is not None:
                        optList.append(option.hasX)
                except:
                    x = 10
                try:
                    if option.hasY is not None:
                        optList.append(option.hasY)
                except:
                    x = 10
                try:
                    if option.hasZ is not None:
                        optList.append(option.hasZ)
                except:
                    x = 10
                try:
                    if option.hasAdHocFeature is not None:
                        optList.append(option.hasAdHocFeature)
                except:
                    x = 10

                optionList.append([option.hasName, optList])  # TODO: check the other options how to check
        ruleDefinition.append(optionList)

        # check the subtyping
        try:
            if DFArule.hasProperty is not None:  # AS-indeptendent

                try:
                    if DFArule.hasValue is not None:
                        ruleDefinition.append([DFArule.hasProperty, DFArule.hasValue])
                except:
                    x = 10

                try:
                    if DFArule.hasMinValue is not None:
                        ruleDefinition.append([DFArule.hasProperty, DFArule.hasMinValue, DFArule.hasMaxValue])
                except:
                    x = 10

        except:  # AS-deptendent
            x = 1  # TODO

        # transform to interface object for DFA rule
        rule_interface = DFARule(RuleType=ruleDefinition[0], Name=ruleDefinition[1],
                                 Description=ruleDefinition[2], isAppliedToProduct=ruleDefinition[3],
                                 isAppliedToProductPart=ruleDefinition[4],
                                 isAppliedToAssemblySequence=ruleDefinition[5],
                                 hasScorePropagation=ruleDefinition[6], hasScoreType=ruleDefinition[7])
        if DFArule.hasPreprocessedData is not None:  # TODO:check if with items or not
            rule_interface.preprocessedData = ruleDefinition[8]
        rule_interface.optionList = optionList
        try:
            if DFArule.hasProperty is not None:
                rule_interface.property = ruleDefinition[9]
        except:
            x = 10

        # ruleList.append(ruleDefinition)
        ruleList.append(rule_interface)

    return ruleList

def addASG_DFARule( AssemblySystemName, component,rule,model,KBPath,API):
    #     """
    #       Function to add a single DFA rules within the ASG component
    #       The DFA rule interface object is used to interface with the function.
    #       The function returns whether or not the function is performed correctly
    #
    #       :param string AssemblySystemName: Name identifier of the assemlbySystem
    #       :param string component: identify the ASG element ("Selector"|"Evaluator")
    #       :param object DFARule: Interface object of the DFA rule model
    #       :param object model: Metamodel instance model
    #       :param string KBPath: Absolute path to the metamodel instance model
    #       :param object API: API object
    #
    #       :return int Error: -1 = error, 1= function performed correcly
    #     """
    #     # match the AssemblySystem-of-interest
    DFARuleList = []
    if len(model.includesAssemblySystem.items) != 0:
        # match the assemblySystem by Name
        for assemblySystem in model.includesAssemblySystem.items:
            if AssemblySystemName == assemblySystem.hasName:
                # check if ASG config exist
                if assemblySystem.hasAssemblyAlgorithmConfiguration is not None:
                    ASG_temp = assemblySystem.hasAssemblyAlgorithmConfiguration
                    if component=="Selector":
                        #check if rule selector is available
                        try:
                            cmp = ASG_temp.hasRuleSelector
                            addDFArule(cmp,rule,API)
                            updateKBv6(KBPath,model)
                        except:
                            x = "No Rule selector available"
                            pass

                    if component=="Evaluator":
                        #check if rule selector is available
                        try:
                            cmp = ASG_temp.hasRuleEvaluator
                            addDFArule(cmp, rule,API)
                            updateKBv6(KBPath,model)
                        except:
                            x = "No Rule evaluator available"
                            pass

                else:
                    return -1   #error - No ASG = No DFA rules
    else:
        return -1

def addASG_DFARules( AssemblySystemName, component,ruleList,model,KBPath,API):
    #     """
    #       Function to add multiple DFA rules within the ASG component
    #       The DFA rule interface object is used to interface with the function.
    #       The function returns whether or not the function is performed correctly
    #
    #       :param string AssemblySystemName: Name identifier of the assemlbySystem
    #       :param string component: identify the ASG element ("Selector"|"Evaluator")
    #       :param object DFARule: Interface object of the DFA rule model
    #       :param object model: Metamodel instance model
    #       :param string KBPath: Absolute path to the metamodel instance model
    #       :param object API: API object
    #
    #       :return int Error: -1 = error, 1= function performed correcly
    #     """
    #     # match the AssemblySystem-of-interest
    DFARuleList = []
    if len(model.includesAssemblySystem.items) != 0:
        # match the assemblySystem by Name
        for assemblySystem in model.includesAssemblySystem.items:
            if AssemblySystemName == assemblySystem.hasName:
                # check if ASG config exist
                if assemblySystem.hasAssemblyAlgorithmConfiguration is not None:
                    ASG_temp = assemblySystem.hasAssemblyAlgorithmConfiguration
                    if component=="Selector":
                        #check if rule selector is available
                        try:
                            cmp = ASG_temp.hasRuleSelector
                            for rule in ruleList:
                                addDFArule(cmp,rule,API)
                            updateKBv6(KBPath,model)
                        except:
                            x = "No Rule selector available"
                            pass

                    if component=="Evaluator":
                        #check if rule selector is available
                        try:
                            cmp = ASG_temp.hasRuleEvaluator
                            for rule in ruleList:
                                addDFArule(cmp, rule, API)
                            updateKBv6(KBPath,model)
                        except:
                            x = "No Rule evaluator available"
                            pass

                else:
                    return -1   #error - No ASG = No DFA rules
    else:
        return -1

def updateDFArule(self, ruleContainer, rule):
    """
      For internal use only!
    """
    for DFArule in ruleContainer.hasDFARule.items:
        if DFArule.hasName == rule[1]:
            DFArule.hasName = rule.Name
            DFArule.hasDescription = rule.Description
            DFArule.isAppliedToProduct = rule.isAppliedToProduct
            DFArule.isAppliedToProductPart = rule.isAppliedToProductPart
            DFArule.isAppliedToAssemblySequence = rule.isAppliedToAssemblySequence
            # DFArule.hasScorePropagation  = rule[6]
            # DFArule.hasScoreType  = rule[7]
            # update the preprocess data
            if DFArule.hasPreprocessedData is not None:  # TODO:check if with items or not
                DFArule.hasPreprocessesData.items[0].hasDataType = rule[8][0]
                DFArule.hasPreprocessesData.items[0].hasDataReference = rule[8][1]
            # update the options
            # TODO!!!

def addDFArule(ruleContainer, newRule,API):
    """
      For internal use only!
    """
    API.initialize(API.ECORE_path)
    # generate a new ASG config and configure
    rule = API.create_noPlatformRoot("DFA_Rule")
    rule.hasName = newRule.Name
    rule.hasDescription = newRule.Description
    rule.isAppliedToProduct = newRule.isAppliedToProduct
    rule.isAppliedToProductPart = newRule.isAppliedToProductPart
    rule.isAppliedToAssemblySequence = newRule.isAppliedToAssemblySequence
    # DFArule.hasScorePropagation  = rule[6]
    # DFArule.hasScoreType  = rule[7]
    # update the preprocess data
    if rule.hasPreprocessedData is not None:  # TODO:check if with items or not
        rule.hasPreprocessesData.items[0].hasDataType = newRule[8][0]
        rule.hasPreprocessesData.items[0].hasDataReference = newRule[8][1]
        # update the options
        # TODO!!!

    ruleContainer.hasDFARule.items.append(rule)