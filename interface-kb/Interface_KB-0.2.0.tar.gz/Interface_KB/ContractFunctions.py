#interface objects
from .InterfaceObjects import Contract,Relation,Ontology,DomainVariable
#import helper functions
from .HelperFunctions import *

#-----------------------------------------------------------------------------------------------------------
#
#   Contract-Ontology extension
#
#       TODO:
#
# -----------------------------------------------------------------------------------------------------------


def getContract( ContractName,model):
    """
      Function to fetch a contract model using the name as identifier.
      The function returns an interface block of the contract model

      :param string ContractName: Name identifier of the Contract
      :param object model: Metamodel instance model

      :return object ContractModel: Interface object of the contract model (-1 = error)
    """

    contract=None
    try:
        for c in model.includesCodesignProblem.hasContracts.items:
            if c.hasName == ContractName:
                contract = Contract(Name=c.hasName,Description=c.hasDescription)
                #assumptions
                for asmpt in c.hasAssumption.items:
                    temp = []
                    for term in asmpt.expression.hasTerm.items:
                        if 'LEFT' in term.hasInfixPosition.name:
                            x = str(type(term))
                            if 'VariableTerm' in x:
                                v = DomainVariable(Name=term.hasDomainVariable.hasName,Description=term.hasDomainVariable.hasDescription,Unit=term.hasDomainVariable.hasUnit)
                                temp.append(v)
                            else:
                                temp.append(term.hasValue)
                        if 'RIGHT' in term.hasInfixPosition.name:
                            temp.append(asmpt.expression.hasExpressionOperator.hasValue)
                            x = str(type(term))
                            if 'VariableTerm' in x:
                                v = DomainVariable(Name=term.hasDomainVariable.hasName,
                                                   Description=term.hasDomainVariable.hasDescription,
                                                   Unit=term.hasDomainVariable.hasUnit)
                                temp.append(v)
                            else:
                                temp.append(term.hasValue)
                    contract.Assumptions.append(temp)


                #guarantees
                for grnt in c.hasGuarantee.items:
                    temp = []
                    for term in grnt.hasExpression.hasTerm.items:
                        if 'LEFT' in term.hasInfixPosition.name:
                            x = str(type(term))
                            if 'VariableTerm' in x:
                                v = DomainVariable(Name=term.hasDomainVariable.hasName,
                                                   Description=term.hasDomainVariable.hasDescription,
                                                   Unit=term.hasDomainVariable.hasUnit)
                                temp.append(v)
                            else:
                                temp.append(term.hasValue)
                        if 'RIGHT' in term.hasInfixPosition.name:
                            temp.append(grnt.hasExpression.hasExpressionOperator.hasValue)
                            x = str(type(term))
                            if 'VariableTerm' in x:
                                v = DomainVariable(Name=term.hasDomainVariable.hasName,
                                                   Description=term.hasDomainVariable.hasDescription,
                                                   Unit=term.hasDomainVariable.hasUnit)
                                temp.append(v)
                            else:
                                temp.append(term.hasValue)
                    contract.Guarantees.append(temp)

        return contract
    except:
        return -1



def updateContract(interfaceObject,model,KBPath):
    """
          Function to update a contract matching the name as identifier.
          The contract interface object is used to interface with the function.
          The function returns whether or not the function is performed correctly

          :param object ContractModel: Interface object of the Contract model
          :param object model: Metamodel instance model
          :param string KBPath: Absolute path to the metamodel instance model

          :return int Error: -1 = error, 1= function performed correcly
        """

    error = -1
    return error


def setContract(interfaceObject,model,KBPath):
    """
             Function to add a contract to an blank KB.
             The contract interface object is used to interface with the function.
             The function returns whether or not the function is performed correctly

             :param object ContractModel: Interface object of the Contract model
             :param object model: Metamodel instance model
             :param string KBPath: Absolute path to the metamodel instance model

             :return int Error: -1 = error, 1= function performed correcly
    """
    error = -1
    return error


def getOntology(model):
    """
      Function to fetch the complete ontology model.
      The function returns an interface block of the ontology model

      :param object model: Metamodel instance model

      :return object OntologyModel: Interface object of the ontology model (-1 = error)
    """
    ontology = None
    try:
        ontology_import = model.includesCodesignProblem.hasOntology
        ontology = Ontology(Name="Not in MM",Description="Not in MM")
        for relation in ontology_import.hasRelation.items:
            source = DomainVariable(Name=relation.hasSource.hasDomainvariable.hasName,Description=relation.hasSource.hasDomainvariable.hasDescription,Unit=relation.hasSource.hasDomainvariable.hasUnit)
            destination = DomainVariable(Name=relation.hasDestination.hasDomainvariable.hasName,Description=relation.hasDestination.hasDomainvariable.hasDescription, Unit=relation.hasDestination.hasDomainvariable.hasUnit)
            r = Relation(Name=relation.hasName, Description=relation.hasDescription, Source=source,Destination=destination)

            x = str(type(relation))
            if 'L1_FuzzyCognitiveRelation' in x:
                r.SensitivityDirection = relation.SensitivityDirection.name
            if 'L2_FuzzyCognitiveRelation' in x:
                r.SensitivityDirection = relation.SensitivityDirection.name
                r.Weight = relation.WeightIndex
            if 'L2_Relation' in x:
                r.Weight = relation.WeightIndex

            ontology.Relations.append(r)
        return ontology
    except:
        return -1





def updateOntology(interfaceObject,model,KBPath):
    """
          Function to update the complete ontology model.
          The ontology interface object is used to interface with the function.
          The function returns whether or not the function is performed correctly

          :param object OntologyModel: Interface object of the ontology model
          :param object model: Metamodel instance model
          :param string KBPath: Absolute path to the metamodel instance model

          :return int Error: -1 = error, 1= function performed correcly
        """

    error = -1
    return error


def setOntology(interfaceObject,model,KBPath):
    """
             Function to add the ontology model to a blank KB.
             The ontology interface object is used to interface with the function.
             The function returns whether or not the function is performed correctly

             :param object OntologyModel: Interface object of the ontology model
             :param object model: Metamodel instance model
             :param string KBPath: Absolute path to the metamodel instance model

             :return int Error: -1 = error, 1= function performed correcly
    """
    error = -1
    return error