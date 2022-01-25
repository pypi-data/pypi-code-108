###################################################################################################
#
#   @brief: this class contains KB interface functions (API)
#
#
#   @Context: developed for the PACo project
#
#
#   @Brief : Basic API function library
#                       -
#
###################################################################################################
#          @ Author: Bert Van Acker
#
#                              revision
#   date             Who rel ver              Remarks
#  28/06/2021        BVA v0.1                 Setup basic structure
#  13/12/2021        BVA v0.2                 KB v6 support
###################################################################################################
#imports
import os
import re
from pyecore.ecore import EClass
from pyecore.resources import ResourceSet, URI
from pyecore.resources.xmi import XMIResource
from pyecore.utils import DynamicEPackage

#import helper functions
from .HelperFunctions import *
#import ASG functions
from .ASGFunctions import *
#import DFA functions
from .DFAFunctions import *
#import DFA functions
from .PerformanceFunctions import *
#import Contract functions
from .ContractFunctions import *

#interface objects
from .InterfaceObjects import ASG,StopCondition,DFARule,Product,Parameter,ProductPart,AssemblySequence,Operation



class KB_Interface():

    def __init__(self,DEBUG):
        self.DEBUG = DEBUG
        self.MM = None
        self.model_instance = None
        self.model = None
        self.KB_path = ""
        self.ECORE_path = ""





#-----------------------------------------------------------------------------------------------------------
#
#   ASG extension
#
# -----------------------------------------------------------------------------------------------------------
    def getASG(self,AssemblySystemName):
        """
              Function to fetch the Assembly Sequence Generation (ASG) configuration using the name as identifier.
              The function returns an interface block of the ASG

              :param string AssemblySystemName: Name identifier of the assemlbySystem

              :return object ASGModel: Interface object of the ASG (-1 = error)
        """
        return getASG(AssemblySystemName,self.model,self.KB_path)

    def updateASG(self,AssemblySystemName, interfaceObject):
        """
              Function to update the  complete Assembly Sequence Generation (ASG) configuration using the name as identifier.
              The ASG interface object is used to interface with the function.
              The function returns whether or not the function is performed correctly

              :param string AssemblySystemName: Name identifier of the assemlbySystem
              :param object ASGModel: Interface object of the ASG

              :return int Error: -1 = error, 1= function performed correcly
        """

        return updateASG(AssemblySystemName,interfaceObject, self.model, self.KB_path)

    def setASG(self, AssemblySystemName, InterfaceObject):
        """
              Function to add a complete ASG model to an blank KB (no existing ASG part).
              The function returns whether or not the function is performed correctly (NOT YET)

              :param string AssemblySystemName: Name identifier of the assemlbySystem
              :param object ASGModel: Interface object of the ASGModel model

              :return int Error: -1 = error, 1= function performed correcly
        """
        setASG(AssemblySystemName, InterfaceObject,self.model,self.KB_path,self.ECORE_path,self.MM,self)

# -----------------------------------------------------------------------------------------------------------
#
#   DFA extension
#
# -----------------------------------------------------------------------------------------------------------
    def getASG_DFARules(self, AssemblySystemName, component):
        """
             Function to fetch the ASG contained rules using the name as identifier and component as selection mechanism.
             The function returns object list of DFA rules

             :param string AssemblySystemName: Name identifier of the assemlbySystem
             :param string component: Identify the rule container (Selector/Evaluator)

             :return objectlist DFARules: List of DFA rules (-1 = error)
        """
        return getASG_DFARules(AssemblySystemName, component,self.model)

    def updateASG_DFARules(self, AssemblySystemName, component,rule):
        """
             Function to update a single the DFA rules within the given container.
             The function returns whether or not the function is performed correctly (NOT YET)

             :param string AssemblySystemName: Name identifier of the assemlbySystem
             :param object ruleContainer: container object containing the DFA rules
             :param object rule: The DFA rules

             :return int Error: -1 = error, 1= function performed correcly
        """
        return updateASG_DFARules(AssemblySystemName, component,rule,self.model,self.KB_path)

    def getDFArules(self,ruleContainer):
        """
             Function to fetch the DFA rules within the given container.
             The function returns object list of DFA rules

             :param object ruleContainer: container object containing the DFA rules

             :return objectlist DFARules: List of DFA rules (-1 = error)
        """
        return getDFArules(ruleContainer)

    def updateDFArule(self, ruleContainer,rule):
        """
             Function to update a single the DFA rules within the given container.
             The function returns whether or not the function is performed correctly (NOT YET)

             :param object ruleContainer: container object containing the DFA rules
             :param object rule: The DFA rules

             :return int Error: -1 = error, 1= function performed correcly
        """
        updateDFArule( ruleContainer,rule)

    def addASG_DFARule(self, AssemblySystemName, component, rule):
        """
             Function to update a single the DFA rules within the given container.
             The function returns whether or not the function is performed correctly (NOT YET)

             :param string AssemblySystemName: Name identifier of the assemlbySystem
             :param object ruleContainer: container object containing the DFA rules
             :param object rule: The DFA rules

             :return int Error: -1 = error, 1= function performed correcly
        """
        addASG_DFARule(AssemblySystemName,component,rule,self.model,self.KB_path,self)

    def addASG_DFARules(self, AssemblySystemName, component, ruleList):
        """
             Function to update multiple DFA rules within the given container.
             The function returns whether or not the function is performed correctly (NOT YET)

             :param string AssemblySystemName: Name identifier of the assemlbySystem
             :param object ruleContainer: container object containing the DFA rules
             :param object rule: The DFA rules

             :return int Error: -1 = error, 1= function performed correcly
        """
        addASG_DFARules(AssemblySystemName,component,ruleList,self.model,self.KB_path,self)
# -----------------------------------------------------------------------------------------------------------
#
#   PERFORMANCE extension
#
# -----------------------------------------------------------------------------------------------------------

    def getPerformance(self, OptimizationProblemName):
        """
          Function to fetch the complete performance model using the name as identifier.
          The function returns an interface block of the performance model

          :param string OptimizationProblemName: Name identifier of the optimization problem

          :return object PerformanceModel: Interface object of the performance model (-1 = error)
        """
        return getPerformance(OptimizationProblemName,self.model)

    def updatePerformance(self, interfaceObject):
        """
              Function to update the complete performance model matching the name as identifier.
              The performance interface object is used to interface with the function.
              The function returns whether or not the function is performed correctly

              :param object PerformanceModel: Interface object of the performance model

              :return int Error: -1 = error, 1= function performed correcly
        """
        return updatePerformance(interfaceObject,self.model,self.KB_path)

    def setPerformance(self, interfaceObject):
        """
             Function to add a complete performance model to an blank KB (no existing performance part).
             The performance interface object is used to interface with the function.
             The function returns whether or not the function is performed correctly

             :param object PerformanceModel: Interface object of the performance model

             :return int Error: -1 = error, 1= function performed correcly
        """
        return setPerformance(interfaceObject,self.model,self.KB_path,self)



# -----------------------------------------------------------------------------------------------------------
#
#   Product (request Pavel)
#           TODO: to add parameters, we need to specify the model, can we add this to the API signature?
# -----------------------------------------------------------------------------------------------------------
    def getProduct(self):
        """
         Function to fetch the Product .
         The function returns an interface block of the Product


         :return object ProductModel: Interface object of the Product model (-1 = error)
        """

        if len(self.model.includesProduct.items) != 0:
            product = Product(Name=self.model.includesProduct.items[0].hasProductName,STEPFile=self.model.includesProduct.items[0].hasSTEPfile)
            #TODO: add the parameters-> discuss which parameters
            return product

        else:
            return -1

    def updateProduct(self,interfaceObject):
        """
              Function to update the Product matching the name as identifier.
              The Product interface object is used to interface with the function.
              The function returns whether or not the function is performed correctly

              :param object ProductModel: Interface object of the Product model

              :return int Error: -1 = error, 1= function performed correcly
        """

        if len(self.model.includesProduct.items) != 0:
            if interfaceObject.Name ==self.model.includesProduct.items[0].hasProductName:
                self.model.includesProduct.items[0].hasProductName=interfaceObject.Name
                self.model.includesProduct.items[0].hasSTEPfile=interfaceObject.STEPFile
            #   TODO: add the parameters-> discuss which parameters

                self.updateKBv6()
                return 1
            else:
                return -1

        else:
            return -1

    def setProduct(self, interfaceObject):
        """
             Function to add a Product model to an blank KB .
             The Product interface object is used to interface with the function.
             The function returns whether or not the function is performed correctly

             :param object ProductModel: Interface object of the Product model

             :return int Error: -1 = error, 1= function performed correcly
        """
        if len(self.model.includesProduct.items) != 0:
            #Product already exists!
            print("Product already exists, use updateProduct() instead")
            return -1
        else:

            self.initialize(self.ECORE_path)
            product = self.create("Product")
            product.hasProductName = interfaceObject.Name
            product.hasSTEPfile = interfaceObject.STEPFile
            # TODO: discuss what is set via the setProduct function e.g. do we already set the analysis model?


            #self.model.includesProduct.items.append(product)
            self.updateKBv6()
            return 1

# -----------------------------------------------------------------------------------------------------------
#
#   Product part
#
# -----------------------------------------------------------------------------------------------------------
    def getProductPart(self,ProductPartName):
        """
         Function to fetch the ProductPart using the name as identifier .
         The function returns an interface block of the ProductPart

        :param string ProductPartName: Name identifier of the ProductPart

         :return object ProductPartModel: Interface object of the ProductPart model (-1 = error)
        """
        if len(self.model.includesProductPart.items) != 0:
            for productPart in self.model.includesProductPart.items:
                if ProductPartName == productPart.hasPartName:
                    part = ProductPart(Name=productPart.hasPartName,ProductType=productPart.hasPartType,Quantity=1)        #TODO:Quantity not in MM v6
                    #link the parameters
                    part.parameterList = []
                    try:
                        for par in productPart.hasModel.hasModelParameter.items:
                            p = Parameter(Name='Not defined',Key=par.hasKey,Value=par.hasValue,Stopcriteria='Not defined')  #TODO: no complete parameter description is given!
                            part.parameterList.append(p)
                    except:
                        if self.DEBUG:print("No model added to ProductPart")

                    #link the product parts - Recursive!
                    part.partList = []
                    for subPart in productPart.hasCompositionEdge.items:
                        p = self.getProductPart(subPart.hasPartName)
                        part.partList.append(p)

                    #link the contactFeatures
                    #TODO: not yet implemented

                    #material
                    try:
                        part.material = [productPart.hasMaterial.hasName,productPart.hasMaterial.hasCost,productPart.hasMaterial.hasDamping,productPart.hasMaterial.hasDensity,productPart.hasMaterial.hasTransparency,productPart.hasMaterial.hasStiffness.hasScalarMatrix6x6]
                    except:
                        if self.DEBUG: print("No material added to ProductPart")

                    return part

        else:
            return -1  # no ProductPart instance

    def updateProductPart(self,interfaceObject):
        """
              Function to update the ProductPart matching the name as identifier.
              The ProductPart interface object is used to interface with the function.
              The function returns whether or not the function is performed correctly

              :param object ProductPartModel: Interface object of the ProductPart model

              :return int Error: -1 = error, 1= function performed correcly
        """
        if len(self.model.includesProductPart.items) != 0:
            for productPart in self.model.includesProductPart.items:
                if interfaceObject.Name == productPart.hasPartName:
                    productPart.hasPartName=interfaceObject.Name
                    #productPart.hasDescription = interfaceObject.Description       # TODO:Quantity not in MM v6
                    productPart.hasPartType=interfaceObject.ProductType
                    #productPart.Quantity = interfaceObject.Quantity                 # TODO:Quantity not in MM v6


                    # update the parameters
                    for par in productPart.hasModel.hasModelParameter.items:
                        for par_new in interfaceObject.parameterList:
                            if par_new.Key == par.hasKey:
                                par.hasKey = par_new.Key
                                par.hasValue = par_new.Value


                    # link the product parts - Recursive!
                    for par in productPart.hasCompositionEdge.items:
                        for par_new in interfaceObject.partList:
                            if par_new.Name == par.hasPartName:
                                #TODO:update the subproduct
                                error = self.updateProductPart(par_new)


                    # link the contactFeatures
                    # TODO: not yet implemented

                    # material
                    productPart.hasMaterial.hasName=interfaceObject.material[0]
                    productPart.hasMaterial.hasCost=interfaceObject.material[1]
                    productPart.hasMaterial.hasDamping=interfaceObject.material[2]
                    productPart.hasMaterial.hasDensity=interfaceObject.material[3]
                    productPart.hasMaterial.hasTransparency=interfaceObject.material[4]
                    productPart.hasMaterial.hasStiffness.hasScalarMatrix6x6=interfaceObject.material[5]

                    self.updateKBv6()
                    return 1

        else:
            return -1  # no ProductPart instance

    def setProductPart(self, interfaceObject):
        """
             Function to add a ProductPart model to an blank KB .
             The ProductPart interface object is used to interface with the function.
             The function returns whether or not the function is performed correctly

             :param object ProductPartModel: Interface object of the ProductPart model

             :return int Error: -1 = error, 1= function performed correcly
        """
        self.initialize(self.ECORE_path)
        #setup a eCore class of a productPart
        part = self.create("ProductPart")

        part.hasPartName = interfaceObject.Name
        # productPart.hasDescription = interfaceObject.Description       # TODO:Quantity not in MM v6
        part.hasPartType = interfaceObject.ProductType
        # productPart.Quantity = interfaceObject.Quantity                 # TODO:Quantity not in MM v6


        #TODO: material and model not correctly added!

        #add model to ProductPart
        model = self.create("Model")
        part.hasModel = model
        # update the parameters
        parameter = self.create("Parameter")
        for par_new in interfaceObject.parameterList:
            parameter.hasKey = par_new.Key
            parameter.hasValue = par_new.Value
            part.hasModel.hasModelParameter.items.append(parameter)

        # link the product parts - Recursive!
        #for par in productPart.hasCompositionEdge.items:
        #    for par_new in interfaceObject.partList:
        #        if par_new.Name == par.hasPartName:
        #            # TODO:update the subproduct
        #            error = self.updateProductPart(par_new)

        # link the contactFeatures
        # TODO: not yet implemented

        # material
        material = self.create("Material")
        part.hasMaterial = material
        part.hasMaterial.hasName = interfaceObject.material[0]
        part.hasMaterial.hasCost = interfaceObject.material[1]
        part.hasMaterial.hasDamping = interfaceObject.material[2]
        part.hasMaterial.hasDensity = interfaceObject.material[3]
        part.hasMaterial.hasTransparency = interfaceObject.material[4]
        stiffness = self.create("Stiffness")
        part.hasMaterial.hasStiffness = stiffness
        part.hasMaterial.hasStiffness.hasScalarMatrix6x6 = interfaceObject.material[5]

        self.updateKBv6()

        return 1


    def getAllProductParts(self):
        """
         Function to fetch all ProductParts within the KB .
         The function returns a list of interface block of the ProductPart


         :return objectlist ProductPartList: List of Interface object of the ProductPart model (-1 = error)
        """
        if len(self.model.includesProductPart.items) != 0:
            list = []
            for productPart in self.model.includesProductPart.items:
                p=self.getProductPart(productPart.hasPartName)
                list.append(p)

            return list
        else:
            return -1

    def updateAllProductParts(self, interfaceObjectList):
        """
              Function to update all ProductParts within the KB.
              A list of ProductPart interface objects is used to interface with the function.
              The function returns whether or not the function is performed correctly

              :param objectlist interfaceObjectList: List of interface object of the ProductPart model

              :return int Error: -1 = error, 1= function performed correcly
        """
        error_overall = 1
        for interfaceObject in interfaceObjectList:
            error = self.updateProductPart(interfaceObject)
            if error==-1:
                error_overall = -1

        return error_overall

    def setAllProductParts(self, interfaceObjectList):
        """
             Function to add all ProductParts to an blank KB .
             A list of ProductPart interface objects is used to interface with the function.
             The function returns whether or not the function is performed correctly

             :param objectlist interfaceObjectList: List of interface object of the ProductPart model

             :return int Error: -1 = error, 1= function performed correcly
        """
        error_overall = 1
        for interfaceObject in interfaceObjectList:
            error = self.setProductPart(interfaceObject)
            if error == -1:
                error_overall = -1

        return error_overall

# -----------------------------------------------------------------------------------------------------------
#
#   Product Analysis (request Pavel)
#           #TODO:update the functions (get,update,set)
# -----------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------------------
#
#   Assembly Sequence
#           #TODO:update the functions (get,update,set) -> allSequences AND Sequence('Name')
#           #TODO: implemented via references instead of composition -> can we change this to allign with other modeled parts?
#           #TODO: assembly contains lots of components without an ID or name (e.g. orientation, geometry), can we adapt this to enable re-use?
#           #TODO: hasFastner links to productPart, is that correct?
# ---------------------------------------------------------------------------------------------------------------------------------------------
    def getAssemblySequence(self,AssemblySystemName):
        """
         Function to fetch the Assembly sequence using the name of the assemblySystem as identifier.
         The function returns an interface block of the AssemblySequence

        :param string AssemblySystemName: Name identifier of the assemblySystem

         :return object AssemblySequenceModel: Interface object of the AssemblySequence model (-1 = error)
        """
        if len(self.model.includesAssemblySystem.items) != 0:
            for AssemblySystem in self.model.includesAssemblySystem.items:
                if AssemblySystem.hasName == AssemblySystemName:
                    try:
                        s_temp = AssemblySystem.hasAssemblySequence
                        #assemblyMetric
                        assemblyMetric = [s_temp.hasAssemblyMetric.items[0].hasName,s_temp.hasAssemblyMetric.items[0].hasValue]
                        #assemblyOption - recursive
                        assemblyOptions = self.getAssemblyOption(s_temp.hasAssemblyOption)

                        sequence = AssemblySequence(Name=assemblyOptions[0], Description="NOT IN MM",AssemblyMetric=assemblyMetric,AssemblyOptions=assemblyOptions)

                        return sequence

                    except:
                        return -1
                else:
                    return -1
        else:
            return -1


    def updateAssemblySequence(self,AssemblySystemName,IntefaceObject):
        """
              Function to update the AssemblySequence using the name of the assemblySystem as identifier
              The AssemblySequence interface object is used to interface with the function.
              The function returns whether or not the function is performed correctly

              :param string AssemblySystemName: Name identifier of the assemblySystem
              :param object AssemblySequenceModel: Interface object of the AssemblySequence model

              :return int Error: -1 = error, 1= function performed correcly
        """
        x=10
        return -1


    def setAssemblySequence(self,AssemblySystemName,IntefaceObject):
        """
             Function to add a AssemblySequence model to an existing AssemblySystem using the name of the assemblySystem as identifier.
             The AssemblySequence interface object is used to interface with the function.
             The function returns whether or not the function is performed correctly

             :param string AssemblySystemName: Name identifier of the assemblySystem
              :param object AssemblySequenceModel: Interface object of the AssemblySequence model

             :return int Error: -1 = error, 1= function performed correcly
        """
        x = 10
        return -1


    def getAssemblyOption(self,AssemblyOption):
        """
         Helper function to fetch the Assembly options for each Assembly step .
         The function returns a recursive AssemblyOption List

        :param object AssemblyOption: Assembly option ecore object

         :return List AssemblyOptionList: list of assembly options RECURSIVE (-1 = error)
        """
        AssemblyOptionList = []
        assembly = None
        try:
            # operations
            operationList = []
            for operation in AssemblyOption.hasOperation.items:
                op = Operation(Name=operation.hasName, Description="NOT IN MM")
                op.OperationMetric = [operation.hasOperationMetric.items[0].hasName, operation.hasOperationMetric.items[
                    0].hasValue]  # TODO: in MM, multiple metrics can be added -> is this necessary?
                # operators
                operatorList = []
                for operator in operation.hasOperator.items:
                    operator_temp = [operator.hasName, operator.hasCostPerHour, operator.hasHeight,
                                     operator.hasMaxLiftingWeight, operator.hasReach]
                    operatorList.append(operator_temp)
                op.Operators = operatorList
                # Tools
                ToolList = []
                for tool in operation.hasTool.items:
                    requiredOperators = []
                    for r_operator in operation.hasOperator.items:
                        requiredOperators.append(r_operator.hasName)  # TODO: only name reference added, ok?
                    Tool_temp = [tool.hasName, tool.hasMass, tool.hasCost, tool.hasOrientation.hasData,
                                 tool.hasGeometry.hasDataInStepFile, requiredOperators]
                    ToolList.append(Tool_temp)
                op.Tool = ToolList
                # Fastners
                FastnersList = []
                for fastner in operation.hasFastner.items:
                    FastnersList.append(fastner.hasPartName)  # TODO: only name reference added, ok?
                op.Fastners = FastnersList
                operationList.append(op)



            #Linking the recursive operations!
            subAssemblyOptions = []
            for recursive_option in AssemblyOption.hasRecursiveAssemblyOption:
                subAssemblyOptions.append(self.getAssemblyOption(recursive_option))

            AssemblyOptionList = [AssemblyOption.hasName, operationList,subAssemblyOptions]

            return AssemblyOptionList

        except:
            return -1




# -----------------------------------------------------------------------------------------------------------
#
#   Contract-Ontology extension
#
# -----------------------------------------------------------------------------------------------------------
    def getContract(self,ContractName):
        """
          Function to fetch a contract model using the name as identifier.
          The function returns an interface block of the contract model

          :param string ContractName: Name identifier of the Contract

          :return object ContractModel: Interface object of the contract model (-1 = error)
        """
        return getContract(ContractName,self.model)

    def updateContract(self,interfaceObject):
        """
              Function to update a contract matching the name as identifier.
              The contract interface object is used to interface with the function.
              The function returns whether or not the function is performed correctly

              :param object ContractModel: Interface object of the Contract model

              :return int Error: -1 = error, 1= function performed correcly
            """
        return updateContract(interfaceObject, self.model, self.KBPath)

    def setContract(self,interfaceObject):
        """
                 Function to add a contract to an blank KB.
                 The contract interface object is used to interface with the function.
                 The function returns whether or not the function is performed correctly

                 :param object ContractModel: Interface object of the Contract model

                 :return int Error: -1 = error, 1= function performed correcly
        """
        return setContract(interfaceObject, self.model, self.KBPath)

    def getOntology(self):
        """
          Function to fetch the complete ontology model.
          The function returns an interface block of the ontology model

          :return object OntologyModel: Interface object of the ontology model (-1 = error)
        """

        return getOntology(self.model)

    def updateOntology(self,interfaceObject):
        """
              Function to update the complete ontology model.
              The ontology interface object is used to interface with the function.
              The function returns whether or not the function is performed correctly

              :param object OntologyModel: Interface object of the ontology model

              :return int Error: -1 = error, 1= function performed correcly
            """

        error = -1
        return updateOntology(interfaceObject, self.model, self.KBPath)

    def setOntology(self,interfaceObject):
        """
                 Function to add the ontology model to a blank KB.
                 The ontology interface object is used to interface with the function.
                 The function returns whether or not the function is performed correctly

                 :param object OntologyModel: Interface object of the ontology model

                 :return int Error: -1 = error, 1= function performed correcly
        """
        error = -1
        return setOntology(interfaceObject, self.model, self.KBPath)








# -----------------------------------------------------------------------------------------------------------
#
#   HELPER FUNCTIONS
#
# -----------------------------------------------------------------------------------------------------------

    def updateKB(self):
        """
              For internal use only!
            """
        updateKB(self.model)

    def updateKBv6(self):
        """
              For internal use only!
            """
        # TODO: update the current MM instead of the new one
        updateKBv6(self.KB_path, self.model)

    def resolvePath(self, relativePath):
        """
              For internal use only!
            """
        return resolvePath(relativePath)

    def importInstanceModel(self, path_ecore, path_instance, VERBOSE=False):
        """
              For internal use only!
            """
        self.model = importInstanceModel(path_ecore, path_instance, VERBOSE=False)
        return self.model

    def addXMLResource(self, rset):
        """
              For internal use only!
            """
        return addXMLResource(rset)

    def initialize(self, model_uri):
        """
              For internal use only!
            """
        self.MM, self.model_instance = initialize(model_uri)

    def serialize(self, xmi_uri):
        """
              For internal use only!
            """
        serialize(xmi_uri, self.model)

    def create(self, e_class):
        """
              For internal use only!
            """
        return create(e_class, self.MM, self.model)

    def create_custom(self, parent, e_class):
        """
              For internal use only!
            """
        return create_custom(parent, e_class, self.MM)

    def create_noPlatformRoot(self, e_class):
        """
              For internal use only!
            """
        return create_noPlatformRoot(e_class, self.MM, self.model)

    # export the meta model to a file
    def export_metamodel(self, output_file):
        """
              For internal use only!
            """
        export_metamodel(output_file, self.model)


# -----------------------------------------------------------------------------------------------------------
#
#   Possible usefull input/code
#
# -----------------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------------------
    # PAVEL INPUT ==>
    #            - ModelFile String
    #            - AnalysisType String
    #            - substepNum Integer
    #            - MeshType [string1,string2]
    #            -boundaryconditions    [bc1,bc2]
    #            -Loads    [Load1,Load2]
    #            -Contacts    [c1,c2]
    # --------------------------------------------------------------------------------------------------------------
    def setProductAnalysis(self, AnalysisList):
        if self.model.includesAnalysis.items != 0:
            for an_new in AnalysisList:
                found = 0
                for an_old in self.model.includesAnalysis.items:
                    if an_new[1] == an_old.hasAnalysisType:  # TODO: for now matched on the type but better on name?
                        found = 1
                        print("Performance Model already added - Do we need to update them?")
                        old = an_old
                        new = an_new
                        # self.updateAnalysis(old,new)

                if found == 0:  # no matching productPart found -> add?
                    print("Performance Model not found - Do we need to add them?")
                    part = self.createAnalysis(an_new)
                    self.model.includesAnalysis.items.append(part)


        else:
            for an_new in AnalysisList:  # assuming that no performance models are added yet
                part = self.createAnalysis(an_new)
                self.model.includesAnalysis.items.append(part)
        self.updateKB()

    # -------------------------------------------
    #
    #       HELPER FUNCTION TO CREATE PRODUCT PART
    # -------------------------------------------
    def createAnalysis(self, analysis):
        part = None

        an_new = self.create("Analysis")
        # an_new.hasName = analysis[0]   #TODO: not in current MM
        an_new.hasAnalysisType = analysis[1]

        # add model
        # model = self.create('AnalysisModel')
        # model.hasName = ""                  #TODO:not yet in API call signature
        # model.hasDescription = ""  # TODO:not yet in API call signature
        # model.hasVersion = ""  # TODO:not yet in API call signature
        # model.hasFile = analysis[2]  # TODO:not yet MM
        # an_new.hasAnalysisModel = model

        # add optional boundary conditions
        if len(analysis[5]) != 0:
            x = 0
        else:
            print("No Boundary Conditions specified")

        # add optional loads
        if len(analysis[6]) != 0:
            for l in analysis[6]:
                load = self.create('Load')
                load.hasMagnitude = l[1]
                load.hasLoadType = l[0]
                # applicationArea = self.create('ApplicationArea')    #TODO: this is underspecified in the API call => needs reference to productPart, contactFeature,...

                an_new.hasLoad.items.append(load)
        else:
            print("No Loads specified")

        # add optional contacts
        if len(analysis[7]) != 0:
            x = 0
        else:
            print("No Contacts specified")

        return an_new

    # -------------------------------------------------------------------------------------------------------------
    # PAVEL INPUT ==>
    #            - add model parameters (helper function)
    #            - parameter as [hasName,hasDescription,hasKey,hasValue]
    # --------------------------------------------------------------------------------------------------------------
    def addModelParameters(self, modelName, modelType, parameterList):

        model = self.create("Model")
        model.hasName = modelName
        model.hasModelType = modelType
        for par in parameterList:
            p = self.create("Parameter")
            p.hasName = par[0]
            p.hasDescription = par[1]
            p.hasKey = par[2]
            p.hasValue = par[3]
            model.hasModelParameter.items.append(p)

        return model



# ----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                 SECONDARY FUNCTIONS
#                       TODO: discuss which of the secondary functions is required
# ----------------------------------------------------------------------------------------------------------------------------------------------------

    # # ---------------------------------node: Product attribute: Name--------------------------------------------------------------------
#     # def getProductName(self):
#     #     """
#     #      Function to fetch the Product name.
#     #
#     #
#     #      :return string Name: Product name (-1 = error)
#     #     """
#     #     if len(self.model.includesProduct.items) != 0:
#     #         value = self.model.includesProduct.items[0].hasProductName
#     #         return value
#     #     else:
#     #         return -1  # no Product instance
#     #
#     # def setProductName(self, att):
#     #     """
#     #      Function to set the Product name.
#     #
#     #      :param string name: Product name
#     #     """
#     #     self.model.includesProduct.items[0].hasProductName = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     #
#     # # ---------------------------------node: Product attribute: STEPfile--------------------------------------------------------------------
#     # def getProductSTEPfile(self):
#     #     """
#     #      Function to fetch the Product STEP file.
#     #
#     #      :return string STEPfile: path to the product STEP file (-1 = error)
#     #     """
#     #     if len(self.model.includesProduct.items) != 0:
#     #         value = self.model.includesProduct.items[0].hasSTEPfile  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -1  # no Product instance
#     #
#     # def setProductSTEPfile(self, att):
#     #     """
#     #         Function to set the STEP file
#     #     :param att: path to the STEP file
#     #     """
#     #     self.model.includesProduct.items[0].hasSTEPfile = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: GroundPosition attribute: X--------------------------------------------------------------------
#     # def getGroundPositionX(self):
#     #     """
#     #      Function to fetch the GroundPositionX.
#     #
#     #
#     #      :return float GroundPositionX: GroundPositionX (-1 = error)
#     #     """
#     #     if len(self.model.includesAssemblySystem.items) != 0:
#     #         value = self.model.includesAssemblySystem.items[0].hasGroundPosition.hasX  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -1  # no GroundPosition instance
#     #
#     # def setGroundPositionX(self, att):
#     #     """
#     #         Function to set the ground position X
#     #     :param float GroundPositionX: GroundPositionX
#     #     """
#     #     self.model.includesAssemblySystem.items[0].hasGroundPosition.hasX = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: GroundPosition attribute: Y--------------------------------------------------------------------
#     # def getGroundPositionY(self):
#     #     """
#     #      Function to fetch the GroundPositionY.
#     #
#     #
#     #      :return float GroundPositionY: GroundPositionY (-1 = error)
#     #     """
#     #     if len(self.model.includesAssemblySystem.items) != 0:
#     #         value = self.model.includesAssemblySystem.items[0].hasGroundPosition.hasY  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no GroundPosition instance
#     #
#     # def setGroundPositionY(self, att):
#     #     """
#     #         Function to set the ground position Y
#     #     :param float GroundPositionY: GroundPositionY
#     #     """
#     #     self.model.includesAssemblySystem.items[0].hasGroundPosition.hasY = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: GroundPosition attribute: Z--------------------------------------------------------------------
#     # def getGroundPositionZ(self):
#     #     """
#     #      Function to fetch the GroundPositionZ.
#     #
#     #
#     #      :return float GroundPositionZ: GroundPositionZ (-1 = error)
#     #     """
#     #     if len(self.model.includesAssemblySystem.items) != 0:
#     #         value = self.model.includesAssemblySystem.items[0].hasGroundPosition.hasZ  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no GroundPosition instance
#     #
#     # def setGroundPositionZ(self, att):
#     #     """
#     #         Function to set the ground position Z
#     #         :param float GroundPositionZ: GroundPositionZ
#     #     """
#     #     self.model.includesAssemblySystem.items[0].hasGroundPosition.hasZ = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: GravityDirection attribute: X--------------------------------------------------------------------
#     # def getGravityDirectionX(self):
#     #     """
#     #      Function to fetch the GravityDirectionX.
#     #
#     #
#     #      :return float GravityDirectionX: GravityDirectionX (-1 = error)
#     #     """
#     #     if len(self.model.includesAssemblySystem.items) != 0:
#     #         value = self.model.includesAssemblySystem.items[0].hasGravityDirection.hasX  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no GravityDirection instance
#     #
#     # def setGravityDirectionX(self, att):
#     #     """
#     #         Function to set the gravitation position X
#     #     :param float GravityDirectionX: GravityDirectionX
#     #     """
#     #     self.model.includesAssemblySystem.items[0].hasGravityDirection.hasX = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: GravityDirection attribute: Y--------------------------------------------------------------------
#     # def getGravityDirectionY(self):
#     #     """
#     #      Function to fetch the GravityDirectionY.
#     #
#     #
#     #      :return float GravityDirectionY: GravityDirectionY (-1 = error)
#     #     """
#     #     if len(self.model.includesAssemblySystem.items) != 0:
#     #         value = self.model.includesAssemblySystem.items[0].hasGravityDirection.hasY  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no GravityDirection instance
#     #
#     # def setGravityDirectionY(self, att):
#     #     """
#     #         Function to set the gravitation position Y
#     #     :param float GravityDirectionY: GravityDirectionY
#     #     """
#     #     self.model.includesAssemblySystem.items[0].hasGravityDirection.hasY = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: GravityDirection attribute: Z--------------------------------------------------------------------
#     # def getGravityDirectionZ(self):
#     #     """
#     #      Function to fetch the GravityDirectionZ.
#     #
#     #
#     #      :return float GravityDirectionZ: GravityDirectionZ (-1 = error)
#     #     """
#     #     if len(self.model.includesAssemblySystem.items) != 0:
#     #         value = self.model.includesAssemblySystem.items[0].hasGravityDirection.hasZ  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no GravityDirection instance
#     #
#     # def setGravityDirectionZ(self, att):
#     #     """
#     #         Function to set the gravitation position Z
#     #     :param float GravityDirectionZ: GravityDirectionZ
#     #     """
#     #     self.model.includesAssemblySystem.items[0].hasGravityDirection.hasZ = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     #
#     # # ---------------------------------node: ProductPart attribute: name--------------------------------------------------------------------
#     # def setProductPartname(self,name, att):
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == name:
#     #             productPart.hasPartName = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: ProductPart attribute: type--------------------------------------------------------------------
#     # def getProductPartType(self, name):
#     #     """
#     #      Function to fetch the ProductPartType.
#     #
#     #
#     #      :return string ProductPartType: ProductPartType (-1 = error)
#     #     """
#     #     value = None
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == name:
#     #             value = productPart.hasPartType  # TODO:update according to MM
#     #     return value
#     #
#     # def setProductParttype(self,name, att):
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == name:
#     #             productPart.hasPartType = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Operator attribute: name--------------------------------------------------------------------
#     # def getOperatorname(self):
#     #     """
#     #      Function to fetch the Operatorname.
#     #
#     #
#     #      :return string Operatorname: Operatorname (-1 = error)
#     #     """
#     #     value = None
#     #     if len(self.model.includesOperator.items) != 0:
#     #         value = self.model.includesOperator.items[0].hasname  # TODO:update according to MM
#     #     return value
#     #
#     #
#     # def setOperatorname(self, att):
#     #     self.model.includesOperator.items[0].hasname = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Operator attribute: reach--------------------------------------------------------------------
#     # def getOperatorreach(self):
#     #     """
#     #      Function to fetch the Operatorreach.
#     #
#     #
#     #      :return float Operatorreach: Operatorreach (-1 = error)
#     #     """
#     #     if len(self.model.includesOperator.items) != 0:
#     #         value = self.model.includesOperator.items[0].hasreach  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no Operator instance
#     #
#     # def setOperatorreach(self, att):
#     #     self.model.includesOperator.items[0].hasreach = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Operator attribute: height--------------------------------------------------------------------
#     # def getOperatorheight(self):
#     #     """
#     #      Function to fetch the Operatorheight.
#     #
#     #
#     #      :return float Operatorheight: Operatorheight (-1 = error)
#     #     """
#     #     if len(self.model.includesOperator.items) != 0:
#     #         value = self.model.includesOperator.items[0].hasheight  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no Operator instance
#     #
#     # def setOperatorheight(self, att):
#     #     self.model.includesOperator.items[0].hasheight = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Operator attribute: maxLiftingWeight--------------------------------------------------------------------
#     # def getOperatormaxLiftingWeight(self):
#     #     """
#     #      Function to fetch the OperatormaxLiftingWeight.
#     #
#     #
#     #      :return float OperatormaxLiftingWeight: OperatormaxLiftingWeight (-1 = error)
#     #     """
#     #     if len(self.model.includesOperator.items) != 0:
#     #         value = self.model.includesOperator.items[0].hasmaxLiftingWeight  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no Operator instance
#     #
#     # def setOperatormaxLiftingWeight(self, att):
#     #     self.model.includesOperator.items[0].hasmaxLiftingWeight = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Operator attribute: costPerHour--------------------------------------------------------------------
#     # def getOperators(self):
#     #     operatorList = []
#     #     if len(self.model.includesOperator.items) != 0:
#     #         for operator in self.model.includesOperator.items:
#     #             operatorList.append([operator.hasName,operator.reach,operator.height,operator.maxLiftingWeight,operator.costPerHour])
#     #     return operatorList
#     #
#     # def setOperators(self, list):
#     #     for op in list:       #list = [operator1,operator2,...,operatorn] with operator = [name,reach,height,maxLiftingWeight,costPerHour]
#     #         #create and add operator
#     #         operator = self.create("Operator")
#     #         operator.hasName = op[0]
#     #         operator.reach = op[1]
#     #         operator.height = op[2]
#     #         operator.maxLiftingWeight = op[3]
#     #         operator.costPerHour = op[4]
#     #         self.model.includesOperator.items.append(operator)
#     #
#     #     self.updateKB()
#     #
#     #
#     # # ---------------------------------node: Analysis attribute: analysisFile--------------------------------------------------------------------
#     # def getAnalysis(self):
#     #     if len(self.model.includesAnalysis.items) != 0:
#     #         analysisList = []
#     #         for analysis in self.model.includesAnalysis.items:
#     #             analysisList.append([analysis.hasAnalysisType])  # TODO:update according to MM
#     #         return analysisList
#     #     else:
#     #         return -2  # no ProductPart instance
#     #
#     # def getAnalysisFile(self,type):
#     #     for analysis in self.model.includesAnalysis.items:
#     #         if analysis.hasAnalysisType == type:
#     #             return analysis.hasAnalysisFile   # TODO:update according to MM
#     #
#     # def setAnalysisanalysisFile(self,type, att):
#     #     for analysis in self.model.includesAnalysis.items:
#     #         if analysis.hasAnalysisType == type:
#     #             analysis.hasAnalysisFile = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Analysis attribute: type--------------------------------------------------------------------
#     # def getAnalysistype(self,type):
#     #     for analysis in self.model.includesAnalysis.items:
#     #         if analysis.hasAnalysisType == type:
#     #             return analysis.hasAnalysisType  # TODO:update according to MM
#     #
#     # def setAnalysistype(self,type, att):
#     #     for analysis in self.model.includesAnalysis.items:
#     #         if analysis.hasAnalysisType == type:
#     #             analysis.hasAnalysisType =att
#     #     self.updateKB()
#     #
#     # def getAnalysisResponsePoints(self,type):
#     #     responsePointList = []
#     #     for analysis in self.model.includesAnalysis.items:
#     #         if analysis.hasAnalysisType == type:
#     #             for responsPoint in analysis.hasResponsePoint.items:
#     #                 x = responsPoint.hasPosition.hasX
#     #                 y = responsPoint.hasPosition.hasY
#     #                 z = responsPoint.hasPosition.hasZ
#     #                 responsePointList.append([responsPoint.hasResponseType,[x,y,z]])
#     #     return responsePointList
#     #
#     # def setAnalysisResponsePoints(self,type, list):     #TODO: responspoints = [point1,point2,...,pointn] with point[type,X,Y,Z]
#     #     for analysis in self.model.includesAnalysis.items:
#     #         if analysis.hasAnalysisType == type:
#     #             for responsepoint in list:
#     #                 #create and add position
#     #                 position = self.create("Position")
#     #                 position.hasX = responsepoint[1]
#     #                 position.hasY = responsepoint[2]
#     #                 position.hasZ = responsepoint[3]
#     #                 #add responsePoint
#     #                 point = self.create("ResponsePoint")
#     #                 point.hasResponseType = responsepoint[0]
#     #                 point.hasPosition = position
#     #                 analysis.hasResponsePoint.items.append(point)
#     #             x = 0
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Analysis attribute: BoundaryCondition--------------------------------------------------------------------
#     # def getAnalysisBoundaryCondition(self,analysisID):
#     #     value = None
#     #     productPart = None
#     #     contactFeatures = []
#     #     blockDOF = []
#     #     if len(self.model.includesAnalysis.items) != 0:
#     #         for analysis in self.model.includesAnalysis.items:
#     #             if analysis.hasAnalysisType == analysisID:  #TODO: ADAPT THIS TO THE ID
#     #                 #get the applicationArea - contact features
#     #                 if len(analysis.hasBoundaryCondition.items[0].hasApplicationArea.hasContactFeature.items) != 0:
#     #                     for feature in analysis.hasBoundaryCondition.items[0].hasApplicationArea.hasContactFeature.items:
#     #                         contactFeatures.append(feature.hasFeatureStepFile)
#     #                 # get the applicationArea - product parts
#     #                     productPart = analysis.hasBoundaryCondition.items[0].hasApplicationArea.hasProductPart.hasPartName
#     #                 #get the blockDOFs
#     #                 if len(analysis.hasBoundaryCondition.items)!= 0:
#     #                     blockDOF = [analysis.hasBoundaryCondition.items[0].hasBlockedDOF.DOF1,analysis.hasBoundaryCondition.items[0].hasBlockedDOF.DOF2,analysis.hasBoundaryCondition.items[0].hasBlockedDOF.DOF3,analysis.hasBoundaryCondition.items[0].hasBlockedDOF.DOF4,analysis.hasBoundaryCondition.items[0].hasBlockedDOF.DOF5,analysis.hasBoundaryCondition.items[0].hasBlockedDOF.DOF6]
#     #
#     #
#     #         return productPart,contactFeatures,blockDOF
#     #     else:
#     #         return -2  # no Analysis instance
#     #
#     #
#     # def setAnalysisBoundaryCondition(self, att):
#     #     self.model.includesAnalysis.items[0].hasBoundaryCondition = att  # TODO:update according to MM
#     #
#     #
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: AnalysisParameter attribute: type--------------------------------------------------------------------
#     # def getAnalysisParameters(self,analysisID):
#     #     parameterList = []
#     #     if len(self.model.includesAnalysis.items) != 0:
#     #         for analysis in self.model.includesAnalysis.items:
#     #             if analysis.hasAnalysisType == analysisID:  # TODO: ADAPT THIS TO THE ID
#     #                 if len(analysis.hasAnalysisParameter.items) != 0:
#     #                     for parameter in analysis.hasAnalysisParameter.items:
#     #                         key = parameter.hasKey
#     #                         value = parameter.hasValue
#     #                         parameterList.append([key,value])
#     #
#     #
#     #     return parameterList
#     #
#     # def setAnalysisParametertype(self, att):
#     #     self.model.includesAnalysisParameter.items[0].hastype = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: AnalysisParameter attribute: name--------------------------------------------------------------------
#     # def getAnalysisParametername(self):
#     #     if len(self.model.includesAnalysisParameter.items) != 0:
#     #         value = self.model.includesAnalysisParameter.items[0].hasname  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no AnalysisParameter instance
#     #
#     # def setAnalysisParametername(self, att):
#     #     self.model.includesAnalysisParameter.items[0].hasname = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: AnalysisParameter attribute: value--------------------------------------------------------------------
#     # def getAnalysisParametervalue(self):
#     #     if len(self.model.includesAnalysisParameter.items) != 0:
#     #         value = self.model.includesAnalysisParameter.items[0].hasvalue  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no AnalysisParameter instance
#     #
#     # def setAnalysisParametervalue(self, att):
#     #     self.model.includesAnalysisParameter.items[0].hasvalue = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Parameter attribute: parameterEffect--------------------------------------------------------------------
#     # def getParameterparameterEffect(self):
#     #     if len(self.model.includesParameter.items) != 0:
#     #         value = self.model.includesParameter.items[0].hasparameterEffect  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no Parameter instance
#     #
#     # def setParameterparameterEffect(self, att):
#     #     self.model.includesParameter.items[0].hasparameterEffect = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Load attribute: type--------------------------------------------------------------------
#     # def getLoad(self,analysisID):
#     #     LoadList = []
#     #     contactFeatures = []
#     #     productPart = None
#     #     direction = []
#     #     LoadType = None
#     #     LoadMagnitude = 0.0
#     #     if len(self.model.includesAnalysis.items) != 0:
#     #         for analysis in self.model.includesAnalysis.items:
#     #             if analysis.hasAnalysisType == analysisID:  # TODO: ADAPT THIS TO THE ID
#     #                 # get the applicationArea - contact features
#     #                 if len(analysis.hasLoad.items[0].hasApplicationArea.hasContactFeature.items) != 0:
#     #                     for feature in analysis.hasBoundaryCondition.items[
#     #                         0].hasApplicationArea.hasContactFeature.items:
#     #                         contactFeatures.append(feature.hasFeatureStepFile)
#     #                 # get the applicationArea - product parts
#     #                 productPart = analysis.hasLoad.items[0].hasApplicationArea.hasProductPart.hasPartName
#     #                 # get load attributes
#     #                 if len(analysis.hasLoad.items) != 0:
#     #                     for load in analysis.hasLoad.items:
#     #                         LoadType = load.hasLoadType
#     #                         LoadMagnitude = load.hasMagnitude
#     #                         # get load direction
#     #                         direction = [load.hasDirection.hasX,load.hasDirection.hasY,load.hasDirection.hasZ]
#     #                 LoadList.append([LoadType,LoadMagnitude,contactFeatures,productPart,direction])
#     #         return LoadList
#     #     else:
#     #         return -2  # no Load instance
#     #
#     # def setLoad(self,analysisID, att):
#     #     self.model.includesLoad.items[0].hastype = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Tool attribute: name--------------------------------------------------------------------
#     # def getToolname(self):
#     #     if len(self.model.includesTool.items) != 0:
#     #         value = self.model.includesTool.items[0].hasname  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no Tool instance
#     #
#     # def setToolname(self, att):
#     #     self.model.includesTool.items[0].hasname = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Tool attribute: mass--------------------------------------------------------------------
#     # def getToolmass(self):
#     #     if len(self.model.includesTool.items) != 0:
#     #         value = self.model.includesTool.items[0].hasmass  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no Tool instance
#     #
#     # def setToolmass(self, att):
#     #     self.model.includesTool.items[0].hasmass = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Tool attribute: cost--------------------------------------------------------------------
#     # def getTools(self):
#     #     toolList = []
#     #     if len(self.model.includesTool.items) != 0:
#     #         for tool in self.model.includesTool.items:
#     #             toolList.append([tool.hasName,tool.hasCost,tool.hasMass,tool.hasOrientation.hasData,tool.hasGeometry.hasDataInStepFile])
#     #     return toolList
#     #
#     #
#     # def setTools(self, list):
#     #
#     #     for t in list:      #list with [tool1,tool2,...,tooln] with tool = [name,cost,mass,orientationData,[Operator],geomestryData] with operator = [name,reach,height,maxLift,costPerHour]
#     #         #create tool
#     #         tool = self.create("Tool")
#     #         tool.hasName = t[0]
#     #         tool.hasCost = t[1]
#     #         tool.hasMass = t[2]
#     #
#     #         #create orientation
#     #         orientation = self.create("Orientation")
#     #         orientation.hasData = t[3]
#     #         tool.hasOrientation = orientation
#     #
#     #         # create operator   #TODO==> do we need to search for existing operators??
#     #             #search for existing operators
#     #
#     #             #if no matching existing operator, make new
#     #         operator = self.create("Operator")
#     #         operator.hasName = t[4][0]
#     #         operator.reach = t[4][1]
#     #         operator.height = t[4][2]
#     #         operator.maxLiftingWeight = t[4][3]
#     #         operator.costPerHour = t[4][4]
#     #
#     #         # create geometry
#     #         geometry = self.create("Geometry")
#     #         geometry.hasDataInStepFile = t[5]
#     #         tool.hasGeometry = geometry
#     #         self.model.includesTool.items.append(tool)
#     #
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: OperationMetric attribute: name--------------------------------------------------------------------
#     # def getOperationMetricname(self):
#     #     if len(self.model.includesOperationMetric.items) != 0:
#     #         value = self.model.includesOperationMetric.items[0].hasName  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no OperationMetric instance
#     #
#     # def setOperationMetricname(self, att):
#     #     self.model.includesOperationMetric.items[0].hasName = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: OperationMetric attribute: value--------------------------------------------------------------------
#     # def getOperationMetricvalue(self):
#     #     if len(self.model.includesOperationMetric.items) != 0:
#     #         value = self.model.includesOperationMetric.items[0].hasValue  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -2  # no OperationMetric instance
#     #
#     # def setOperationMetricvalue(self, att):
#     #     self.model.includesOperationMetric.items[0].hasValue = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: AssemblyMetric attribute: value--------------------------------------------------------------------
#     # def getAssemblyMetricvalue(self):
#     #     if len(self.model.includesAssemblyMetric.items) != 0:
#     #         value = self.model.includesAssemblyMetric.items[0].hasvalue  # TODO:update according to MM
#     #         return value
#     #     else:
#     #         return -1  # no AssemblyMetric instance
#     #
#     # def setAssemblyMetricvalue(self, att):
#     #     self.model.includesAssemblyMetric.items[0].hasvalue = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Material attribute: name--------------------------------------------------------------------
#     #
#     # def getMaterialname(self, partName):
#     #     value = None
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             value = productPart.hasMaterial.hasName  # TODO:update according to MM
#     #
#     #     return value
#     #
#     # def setMaterialname(self, partName, att):
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             productPart.hasMaterial.hasName = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     #     # ---------------------------------node: Material attribute: density--------------------------------------------------------------------
#     #
#     # def getMaterialdensity(self, partName):
#     #     value = None
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             value = productPart.hasMaterial.hasDensity  # TODO:update according to MM
#     #
#     #     return value
#     #
#     # def setMaterialdensity(self, partName, att):
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             productPart.hasMaterial.hasDensity = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     #     # ---------------------------------node: Material attribute: cost--------------------------------------------------------------------
#     #
#     # def getMaterialcost(self, partName):
#     #     value = None
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             value = productPart.hasMaterial.hasCost  # TODO:update according to MM
#     #
#     #     return value
#     #
#     # def setMaterialcost(self, partName, att):
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             productPart.hasMaterial.hasCost = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     #     # ---------------------------------node: Material attribute: damping--------------------------------------------------------------------
#     #
#     # def getMaterialdamping(self, partName):
#     #     value = None
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             value = productPart.hasMaterial.hasDamping  # TODO:update according to MM
#     #
#     #     return value
#     #
#     # def setMaterialdamping(self, partName, att):
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             productPart.hasMaterial.hasDamping = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     #     # ---------------------------------node: Material attribute: youngModulus--------------------------------------------------------------------
#     #
#     # def getMaterialyoungModulus(self, partName):
#     #     value = None
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             value = productPart.hasMaterial.hasYoungModulus  # TODO:update according to MM
#     #
#     #     return value
#     #
#     # def setMaterialyoungModulus(self, partName, att):
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             productPart.hasMaterial.hasYoungModulus = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     #     # ---------------------------------node: Material attribute: poissonRatio--------------------------------------------------------------------
#     #
#     # def getMaterialpoissonRatio(self, partName):
#     #     value = None
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             value = productPart.hasMaterial.hasPoissonRatio  # TODO:update according to MM
#     #
#     #     return value
#     #
#     # def setMaterialpoissonRatio(self, partName, att):
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             productPart.hasMaterial.hasPoissonRatio = att  # TODO:update according to MM
#     #     self.updateKB()
#     #
#     # # ---------------------------------node: Material attribute: transparency--------------------------------------------------------------------
#     #
#     # def getMaterialtransparency(self, partName):
#     #     value = None
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             value = productPart.hasMaterial.hasTransparency  # TODO:update according to MM
#     #
#     #     return value
#     #
#     # def setMaterialtransparency(self, partName, att):
#     #     for productPart in self.model.includesProductPart.items:
#     #         if productPart.hasPartName == partName:
#     #             productPart.hasMaterial.hasTransparency = att  # TODO:update according to MM
#     #     self.updateKB()










