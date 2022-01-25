#interface objects
from .InterfaceObjects import Parameter,PerformanceModel,StopCondition,Constraint,Objective,DecisionVariable
#import helper functions
from .HelperFunctions import *

#-----------------------------------------------------------------------------------------------------------
#
#   Performance extension
#
#       TODO:
#
# -----------------------------------------------------------------------------------------------------------


def getPerformance( OptimizationProblemName,model):
    """
      Function to fetch the complete performance model using the name as identifier.
      The function returns an interface block of the performance model

      :param string OptimizationProblemName: Name identifier of the optimization problem
      :param object model: Metamodel instance model

      :return object PerformanceModel: Interface object of the performance model (-1 = error)
    """

    #define performance model interface object
    pModel = PerformanceModel()
    pModel.clean()  # Flushing the pModel

    found = 0
    if len(model.includesOptimizationProblem.items) != 0:
        # match the assemblySystem by Name
        for optimizationProblem in model.includesOptimizationProblem.items:
            if OptimizationProblemName == optimizationProblem.hasName:
                found = 1
                pModel.Name=optimizationProblem.hasName
                pModel.Description = optimizationProblem.hasDescription

                # fetch the analysysDescription
                pModel.OptimizationMethod=[optimizationProblem.hasOptimizationAnalysisdDescription.hasOptimizationMethod.hasName,optimizationProblem.hasOptimizationAnalysisdDescription.hasOptimizationMethod.hasDescription,optimizationProblem.hasOptimizationAnalysisdDescription.hasOptimizationMethod.hasAlgorithmClass.name]
                StopList = []
                for STP in optimizationProblem.hasOptimizationAnalysisdDescription.hasStopCriterion.items:
                    s = StopCondition(Name=STP.hasName,Description=STP.hasDescription,Value=STP.hasValue,Stopcriteria=STP.hasStopCriterion.name)
                    StopList.append(s)
                pModel.StopConditionList=StopList

                # fetch the Optimization targets
                for designTarget in optimizationProblem.hasOptimizationTargetDescription.hasDesignTarget.items:
                    # check the typing
                    x = str(type(designTarget))
                    if 'Constraint' in x:
                        cstr = Constraint(Name=designTarget.hasName,Description=designTarget.hasDescription)

                        for term in designTarget.hasExpression.hasTerm.items:                       #TODO:this needs to be reworked!
                            TERM = []
                            if "LEFT" in term.hasInfixPosition.name:
                                TERM.append('LEFT')
                            if "RIGHT" in term.hasInfixPosition.name:
                                TERM.append('RIGHT')
                            x = str(type(term))
                            if 'Textual' in x:  # textual term
                                TERM.append(term.hasValue)
                            if 'Numerical' in x:  # numerical term
                                TERM.append(term.hasValue)
                            if 'Variable' in x:  # variable term
                                TERM.append(term.hasDecisionVariable.hasName)
                                TERM.append(term.hasDecisionVariable.hasDescription)
                                TERM.append(term.hasDecisionVariable.hasOptimum)
                            cstr.Expression.append(TERM)
                        #add the expression operator
                        operator  = designTarget.hasExpression.hasExpressionOperator.hasValue
                        cstr.Expression.append(operator)

                        pModel.ConstraintList.append(cstr)

                    if 'Objective' in x:
                        OBJ_O = Objective(Name=designTarget.hasName, Description=designTarget.hasDescription)

                        x = str(type(designTarget.hasTerm))
                        if 'Textual' in x:  # textual term
                            OBJ_O.ObjectiveOption = designTarget.hasTerm.hasValue
                        if 'Numerical' in x:  # numerical term
                            OBJ_O.ObjectiveOption = designTarget.hasTerm.hasValue
                        if 'Variable' in x:  # variable term
                            OBJ_O.ObjectiveOption = [designTarget.hasTerm.hasDecisionVariable.hasName,designTarget.hasTerm.hasDecisionVariable.hasDescription,designTarget.hasTerm.hasDecisionVariable.hasOptimum]
                        pModel.ObjectiveList.append(OBJ_O)

                # fetch the design variables
                for variable in optimizationProblem.hasOptimizationTargetDescription.hasDecisionVariable.items:
                    dv = DecisionVariable(Name=variable.hasName,Description=variable.hasDescription,InitialValue=variable.hasInitialValue,MaxValue=variable.hasMaxValue,MinValue=variable.hasMinValue,Optimum=variable.hasOptimum,Resolution=variable.hasResolution)
                    try:
                        par = Parameter(Name=variable.hasParameter.hasName,Description=variable.hasParameter.hasDescription,Key=variable.hasParameter.hasKey, GUID=variable.hasParameter.hasGUID,Value=variable.hasParameter.hasValue)
                        dv.parameterList.append(par)
                    except:
                        par = []

                    pModel.parameterList.append(dv)



        if found:
            return pModel
        else:
            return -1
    else:
        return -1  # no Optimization Problem!


def updatePerformance(interfaceObject,model,KBPath):
    """
          Function to update the complete performance model matching the name as identifier.
          The performance interface object is used to interface with the function.
          The function returns whether or not the function is performed correctly

          :param object PerformanceModel: Interface object of the performance model
          :param object model: Metamodel instance model
          :param string KBPath: Absolute path to the metamodel instance model

          :return int Error: -1 = error, 1= function performed correcly
        """

    #find the optimization model
    found = 0
    if len(model.includesOptimizationProblem.items) != 0:
        # match the assemblySystem by Name
        for optimizationProblem in model.includesOptimizationProblem.items:
            if interfaceObject.Name == optimizationProblem.hasName:
                found = 1
                optimizationProblem.hasName=interfaceObject.Name
                optimizationProblem.hasDescription=interfaceObject.Description
                #analysisDescription
                optimizationProblem.hasOptimizationAnalysisdDescription.hasOptimizationMethod.hasName = interfaceObject.OptimizationMethod[0]
                optimizationProblem.hasOptimizationAnalysisdDescription.hasOptimizationMethod.hasDescription = interfaceObject.OptimizationMethod[1]
                optimizationProblem.hasOptimizationAnalysisdDescription.hasOptimizationMethod.hasAlgorithmClass.name = interfaceObject.OptimizationMethod[2]

                StopList = []
                for STP in optimizationProblem.hasOptimizationAnalysisdDescription.hasStopCriterion.items:
                    for STP_NEW in interfaceObject.StopConditionList:
                        if STP_NEW.Name == STP.hasName:
                            STP.hasName=STP_NEW.Name
                            STP.hasDescription=STP_NEW.Description
                            STP.hasValue=STP_NEW.Value
                            STP.hasStopCriterion.name=STP_NEW.StopCriteria

                #Objectives and constraints
                for designTarget in optimizationProblem.hasOptimizationTargetDescription.hasDesignTarget.items:
                    # check the typing
                    x = str(type(designTarget))
                    if 'Constraint' in x:
                        for constraint_new in interfaceObject.ConstraintList:
                            if constraint_new.Name ==designTarget.hasName:
                                designTarget.hasName=constraint_new.Name
                                designTarget.hasDescription=constraint_new.Description
                                for term in designTarget.hasExpression.hasTerm.items:
                                    y=1
                                    #TODO: using the current KB (version6), updating the expressions is not possible! discuss if needed


                    if 'Objective' in x:
                        for obj_new in interfaceObject.ObjectiveList:
                            designTarget.hasName = obj_new.Name
                            designTarget.hasDescription=obj_new.Description
                        x = str(type(designTarget.hasTerm))
                        if 'Textual' in x:  # textual term
                            designTarget.hasTerm.hasValue = obj_new.ObjectiveOption[0]
                        if 'Numerical' in x:  # numerical term
                            designTarget.hasTerm.hasValue = obj_new.ObjectiveOption[0]
                        if 'Variable' in x:  # variable term
                            designTarget.hasTerm.hasDecisionVariable.hasName= obj_new.ObjectiveOption[0]
                            designTarget.hasTerm.hasDecisionVariable.hasDescription= obj_new.ObjectiveOption[1]
                            designTarget.hasTerm.hasDecisionVariable.hasOptimum = obj_new.ObjectiveOption[2]



                #Decision Variables
                for variable in optimizationProblem.hasOptimizationTargetDescription.hasDecisionVariable.items:
                    for variable_new in interfaceObject.parameterList:
                        if variable.hasName == variable_new.Name:
                            variable.hasName=variable_new.Name
                            variable.hasInitialValue=variable_new.InitialValue
                            variable.hasMaxValue=variable_new.MaxValue
                            variable.hasMinValue=variable_new.MinValue
                            variable.hasOptimum=variable_new.Optimum
                            variable.hasResolution=variable_new.Resolution
                            for par in variable_new.parameterList:
                                if variable.hasParameter.hasName==par.Name:
                                    variable.hasParameter.hasName = par.Name
                                    variable.hasParameter.hasDescription = par.Description
                                    variable.hasParameter.hasKey = par.Key
                                    variable.hasParameter.hasGUID = par.GUID
                                    variable.hasParameter.hasValue = str(par.Value) #TODO: this needs to be a real value?


        if found:
            updateKBv6(KBPath, model)
            return 1
        else:
            return -1
    else:
        return -1  # no Optimization Problem!


def setPerformance(interfaceObject,model,KBPath,API):
    """
             Function to add a complete performance model to an blank KB (no existing performance part).
             The performance interface object is used to interface with the function.
             The function returns whether or not the function is performed correctly

             :param object PerformanceModel: Interface object of the performance model
             :param object model: Metamodel instance model
             :param string KBPath: Absolute path to the metamodel instance model

             :return int Error: -1 = error, 1= function performed correcly
    """
    API.initialize(API.ECORE_path)
    # generate a new ASG config and configure
    optimizationProblem = API.create("OptimizationProblem")
    optimizationProblem.hasName=interfaceObject.Name
    optimizationProblem.hasDescription=interfaceObject.Description
    #analysisDescription
    OptimizationAnalysisdDescription = API.create_noPlatformRoot("OptimizationAnalysisDescription")

    #add the method
    OptimizationMethod = API.create_noPlatformRoot("OptimizationMethod")
    OptimizationMethod.hasName = interfaceObject.OptimizationMethod[0]
    OptimizationMethod.hasDescription = interfaceObject.OptimizationMethod[1]
    OptimizationMethod.hasAlgorithmClass.name = interfaceObject.OptimizationMethod[2]
    OptimizationAnalysisdDescription.hasOptimizationMethod = OptimizationMethod

    #add the stop criteria
    for STP_NEW in interfaceObject.StopConditionList:
        StopCriterion = API.create_noPlatformRoot("StopCriterion")
        StopCriterion.hasName = STP_NEW.Name
        StopCriterion.hasDescription = STP_NEW.Description
        StopCriterion.hasValue = STP_NEW.Value
        StopCriterion.hasStopCriterion.name = STP_NEW.StopCriteria
        OptimizationAnalysisdDescription.hasStopCriterion.items.append(StopCriterion)

    optimizationProblem.hasOptimizationAnalysisdDescription = OptimizationAnalysisdDescription

    OptimizationTargetDescription = API.create_noPlatformRoot("OptimizationTargetDescription")
    #TODO:implement!
    #Objectives and constraints
    for constraint_new in interfaceObject.ConstraintList:
        constraint = API.create_noPlatformRoot("Constraint")
        constraint.hasName=constraint_new.Name
        constraint.hasDescription=constraint_new.Description

        #TODO: using the current KB (version6), updating the expressions is not possible! discuss if needed

        OptimizationTargetDescription.hasDesignTarget.append(constraint)

    for obj_new in interfaceObject.ObjectiveList:
        objective = API.create_noPlatformRoot("Objective")
        objective.hasName = obj_new.Name
        objective.hasDescription=obj_new.Description
        expression = API.create_noPlatformRoot("Expression")

        #TODO: using the current KB (version6), updating the expressions is not possible! discuss if needed

        OptimizationTargetDescription.hasDesignTarget.append(objective)


    #Decision Variables
    for variable_new in interfaceObject.parameterList:
        variable = API.create_noPlatformRoot("Variable")
        variable.hasName=variable_new.Name
        variable.hasInitialValue=variable_new.InitialValue
        variable.hasMaxValue=variable_new.MaxValue
        variable.hasMinValue=variable_new.MinValue
        variable.hasOptimum=variable_new.Optimum
        variable.hasResolution=variable_new.Resolution
        for par in variable_new.parameterList:
            subvariable = API.create_noPlatformRoot("Variable")
            subvariable.hasName = par.Name
            subvariable.hasDescription = par.Description
            subvariable.hasKey = par.Key
            subvariable.hasGUID = par.GUID
            subvariable.hasValue = str(par.Value) #TODO: this needs to be a real value?

        OptimizationTargetDescription.hasDecisionVariable.append(variable)

    optimizationProblem.hasOptimizationTargetDescription = OptimizationTargetDescription


    updateKBv6(KBPath, model)
    return 1
