import json


class ASG():
    """
        ASG: Class representing the Assembly Sequence Generation (ASG) algorithm

         :param string Name: Name of the ASG
         :param string Description: Description of the ASG
         :param enum ProcessingType: ProcessingType of the ASGASG
         :param list Generator: Generator description of the ASG
         :param list Selector: Selector description of the ASG
         :param list Evaluator: Evaluator description of the ASG
         :param list StopConditionList: StopConditionList description of the ASG
         :param objectlist SelectorDFARuleList: list of DFA rules linked to the ASG selector
         :param objectlist EvaluatorDFARuleList: list of DFA rules linked to the ASG evaluator
    """
    def __init__(self,JSONDescriptor=None,Name="",Description="",ProcessingType="Full",Generator=[],Selector=[],SelectorDFARules = [],Evaluator=[],EvaluatorDFARules = [],StopConditions=[],DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.ProcessingType = str(ProcessingType)   #TODO: ENUM not serializable!
            #ASG GENERATOR config
            self.Generator = Generator
            # ASG SELECTOR config
            self.Selector = Selector
            self.SelectorDFARuleList = SelectorDFARules
            # ASG EVALUATOR config
            self.Evaluator = Evaluator
            self.EvaluatorDFARuleList = EvaluatorDFARules
            # ASG Terminator config
            self.StopConditionList=StopConditions
        else:
            self.json2object(JSONDescriptor)
            x=10

    def json2object(self,jsonDescriptor):
        """
             Function to generate a ASG object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the DFA rule

        """
        #--interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)
        #--setup object--
        self.Name = jsonObject['Name']
        self.Description = jsonObject['Description']
        self.ProcessingType = jsonObject['ProcessingType']
        self.Generator = jsonObject['Generator']
        self.Selector = jsonObject['Selector']
        self.Evaluator = jsonObject['Evaluator']
        self.Generator = jsonObject['Generator']
        self.StopConditionList = []
        for terminator in jsonObject['StopConditionList']:
            s = StopCondition(None, terminator['Name'], terminator['Description'],terminator['Value'], terminator['StopCriteria'])
            self.StopConditionList.append(s)
        #TODO: discuss if we need to add the rules at once?


    def object2json(self):
        """
            Function to generate a json file from the ASG
        """
        return json.dumps(self, default=lambda o: o.__dict__,indent=4)

    def object2yaml(self):
        """
            Function to generate a yaml file from the ASG - PROTOTYPE
        """
        return -1 #yaml.dump(self,indent=4)

class DFARule():
    """
        DFARule: Class representing the DFA rule

         :param string Name: Name of the DFA rule
         :param string Description: Description of the DFA rule
         :param string RuleType: RuleType of the DFA rule
         :param bool isAppliedToProduct: Identify if DFA rule is applied to product
         :param bool isAppliedToProductPart: Identify if DFA rule is applied to product part
         :param bool isAppliedToAssemblySequence: Identify if DFA rule is applied to assembly sequence
         :param enum hasScorePropagation: hasScorePropagation of the DFA rule
         :param enum hasScoreType: hasScoreType of the DFA rule
         :param objectlist optionList: List of options of the DFA rule
         :param object property: Referenced property of the DFA rule
         :param list preprocessedData: preprocessedData of the DFA rule

    """
    def __init__(self, JSONDescriptor=None, Name="", Description="", RuleType='',isAppliedToProduct=False, isAppliedToProductPart=False,isAppliedToAssemblySequence=False,hasScorePropagation="ScorePropagation=Best",hasScoreType="ScoreType=Score",preprocessedData=[],optionList = [], DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.RuleType = RuleType
            self.isAppliedToProduct = isAppliedToProduct
            self.isAppliedToProductPart = isAppliedToProductPart
            self.isAppliedToAssemblySequence = isAppliedToAssemblySequence
            self.hasScorePropagation = str(hasScorePropagation)
            self.hasScoreType=str(hasScoreType)
            self.optionList = optionList
            self.property = None
            self.preprocessedData = preprocessedData
        else:
            # TODO: import json descriptor to setup object
            self.json2object(JSONDescriptor)

    def json2object(self,jsonDescriptor):
        """
             Function to generate a DFA object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the DFA rule

        """
        #--interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)
        #--setup object--
        self.Name = jsonObject['DFARule']['Name']
        self.Description = jsonObject['DFARule']['Description']
        self.RuleType = jsonObject['DFARule']['RuleType']
        if 'True' in jsonObject['DFARule']['isAppliedToProduct']:self.isAppliedToProduct = True
        else:self.isAppliedToProduct = False
        if 'True' in jsonObject['DFARule']['isAppliedToProductPart']:self.isAppliedToProductPart = True
        else:self.isAppliedToProductPart = False
        if 'True' in jsonObject['DFARule']['isAppliedToAssemblySequence']:self.isAppliedToAssemblySequence = True
        else:self.isAppliedToAssemblySequence = False
        if '1' in jsonObject['DFARule']['hasScorePropagation']:self.hasScorePropagation = 1
        else:self.hasScorePropagation = 0
        if '1' in jsonObject['DFARule']['hasScoreType']:self.hasScoreType = 1
        else:self.hasScoreType = 0
        self.optionList = []
        for option in jsonObject['DFARule']['optionList']:
            temp = []
            temp.append(option['Name'])
            temp.append(option['Value1'])
            temp.append(option['Value2'])
            self.optionList.append(temp)
        for property in jsonObject['DFARule']['property']:
            temp = []
            temp.append(property['Name'])
            temp.append(property['Value1'])
            temp.append(property['Value2'])
            self.property=temp

        #self.preprocessedData = preprocessedData       #TODO!


    def object2json(self):
        """
            Function to generate a json file from the DFA rule
        """
        return json.dumps(self.__dict__,indent=4)

class PerformanceModel():
    """
       PerformanceModel: Class representing the complete performance model

        :param string Name: Name of the performance model
        :param string Description: Description of the performance model
        :param list OptimizationMethod: OptimizationMethod of the performance model
        :param objectlist StopConditionList: List of stop conditions
        :param list MethodPerformance: List of stop performance metrics
        :param list RAWResults: List of RAW optimization results
        :param list interpretedResults: List of interpreted optimization results
        :param objectlist parameterList: list of linked parameters
        :param objectlist ObjectiveList: list of optimization objectives
        :param objectlist ConstraintList: list of optimization constraints
    """
    def __init__(self, JSONDescriptor=None, Name="", Description="",OptimizationMethod=[],MethodPerformance=[],RAWResults=[],parameterlist = [],StopConditions = [],ObjectiveList=[],ConstraintList=[],interpretedResults=[],DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            #OptimizationMethod + Stop
            self.OptimizationMethod = OptimizationMethod
            self.StopConditionList = StopConditions
            # OptimizationResult
            self.MethodPerformance = MethodPerformance
            self.RAWResults = RAWResults
            self.interpretedResults=interpretedResults
            #parameter list
            self.parameterList = parameterlist
            # DESIGN TARGETS
            self.ObjectiveList = ObjectiveList
            self.ConstraintList = ConstraintList

        else:
            # TODO: import json descriptor to setup object
            self.json2object(JSONDescriptor)

    def json2object(self, jsonDescriptor):
        """
             Function to generate a performance model from a JSON file

             :param string jsonDescriptor: absolute path to the json file for performance model

        """
        # --interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)
        # --setup object--
        self.Name = jsonObject['Name']
        self.Description = jsonObject['Description']
        self.OptimizationMethod = [jsonObject['OptimizationMethod'][0],jsonObject['OptimizationMethod'][1],jsonObject['OptimizationMethod'][2]]
        #stopConditions
        self.StopConditionList = []
        for stp in jsonObject["StopConditionList"]:
            stopC = StopCondition(Name=stp["Name"],Description=stp["Description"],Value=stp["Value"],Stopcriteria=stp["StopCriteria"])
            self.StopConditionList.append(stopC)

        #Method results TODO: this is not complete yet
        self.MethodPerformance = jsonObject['MethodPerformance']
        self.RAWResults = jsonObject['RAWResults']
        self.interpretedResults = jsonObject['interpretedResults']

        # DecisionVariables
        self.parameterList = []
        for var in jsonObject["parameterList"]:
            pList = []
            for p in var["parameterList"]:
                par = Parameter(Name=p["Name"], Description=p["Description"],Key=p["Key"],GUID=p["GUID"], Value=p["Value"], Stopcriteria=p["StopCriteria"])
                pList.append(par)
            decisionvariable = DecisionVariable(Name=var["Name"], Description=var["Description"], InitialValue=var["InitialValue"],MinValue=var["MinValue"], MaxValue=var["MaxValue"], Optimum=var["Optimum"],Resolution = var["Resolution"],parameters=pList)
            self.parameterList.append(decisionvariable)

        # Objectives
        self.ObjectiveList = []
        for objective in jsonObject["ObjectiveList"]:
            obj_ = Objective(Name=objective["Name"], Description=objective["Description"], ObjectiveOption=objective["ObjectiveOption"])
            self.ObjectiveList.append(obj_)

        # Constraints
        self.ConstraintList = []
        for cnstr in jsonObject["ConstraintList"]:
            cnstr_ = Constraint(Name=cnstr["Name"], Description=cnstr["Description"],Expression=cnstr["Expression"])
            self.ConstraintList.append(cnstr_)

    def clean(self):
        self.parameterList = []
        # DESIGN TARGETS
        self.ObjectiveList = []
        self.ConstraintList = []

    def object2json(self):
        """
               Function to generate a json file from the performance model
        """
        return json.dumps(self, default=lambda o: o.__dict__,indent=4)

class StopCondition():
    """
        StopCondition: Class representing the algorithm stop conditions

         :param string Name: Name of the object
         :param string Description: Description of the object
         :param string Value: Value of the object
         :param enum StopCriteria: StopCriteria of the object

    """
    def __init__(self, JSONDescriptor=None, Name="", Description="", Value=0.0, Stopcriteria="maxDepth=0", DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.Value = Value
            self.StopCriteria = Stopcriteria
        else:
            # TODO: import json descriptor to setup object
            x = 10

class Parameter():
    """
            Parameter: Class representing the parameter

             :param string Name: Name of the parameter
             :param string Description: Description of the parameter
             :param string Key: Key of the parameter
             :param string GUID: Global unique identifier of the parameter
             :param float Value: Value of the parameter
             :param enum StopCriteria: StopCriteria of the parameter
    """
    def __init__(self, JSONDescriptor=None, Name="", Description="",Key="",GUID="", Value=0.0, Stopcriteria="maxDepth=0", DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.Key = Key
            self.GUID = GUID
            self.Value = Value
            self.StopCriteria = Stopcriteria
        else:
            # TODO: import json descriptor to setup object
            x = 1

class Objective():
    """
        Objective: Class representing the optimization Objective

         :param string Name: Name of the Objective
         :param string Description: Description of the Objective
         :param enum ObjectiveOption: ObjectiveOption of the Objective
    """
    def __init__(self, JSONDescriptor=None, Name="", Description="",ObjectiveOption="Minimize", DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.ObjectiveOption = ObjectiveOption

        else:
            # TODO: import json descriptor to setup object
            x = 10

class Constraint():
    """
        Constraint: Class representing the optimization Constraint

         :param string Name: Name of the constraint
         :param string Description: Description of the constraint
         :param list Expression: Expression of the constraint
    """
    def __init__(self, JSONDescriptor=None, Name="", Description="",Expression=[], DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.Expression = Expression

        else:
            # TODO: import json descriptor to setup object
            x = 10

class DecisionVariable():
    """
        DecisionVariable: Class representing the optimization Objective

         :param string Name: Name of the DecisionVariable
         :param string Description: Description of the DecisionVariable
         :param float InitialValue: InitialValue of the DecisionVariable
         :param float MinValue: MinValue of the DecisionVariable
         :param float MaxValue: MaxValue of the DecisionVariable
         :param float Optimum: Optimum of the DecisionVariable
         :param float Resolution: Resolution of the DecisionVariable
         :param objectlist parameterList: list of linked parameters
    """
    def __init__(self, JSONDescriptor=None, Name="", Description="",InitialValue=0.0,MinValue=0.0, MaxValue=0.0, Optimum=0.0,Resolution = 0.0,parameters=[], DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.InitialValue = InitialValue
            self.MinValue = MinValue
            self.MaxValue = MaxValue
            self.Optimum = Optimum
            self.Resolution = Resolution
            self.parameterList = parameters
        else:
            # TODO: import json descriptor to setup object
            x = 1

class Product():
    """
        Product: Class representing the Product

         :param string Name: Name of the Product
         :param string STEPFile: Absolute path to the Product STEP file
         :param objectlist parameterList: list of linked parameters
    """
    def __init__(self, JSONDescriptor=None, Name="", Description="",STEPFile='',parameters = [], DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.STEPFile = STEPFile
            self.parameterList = parameters

        else:
            self.json2object(JSONDescriptor)
            x = 10

    def json2object(self,jsonDescriptor):
        """
             Function to generate a Product object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the Product

        """
        #--interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)
        #--setup object--
        self.Name = jsonObject['Name']
        self.Description = jsonObject['Description']
        self.STEPFile = jsonObject['STEPFile']

        self.parameterList = []
        for par in jsonObject['parameterList']:
            p = Parameter(None, Name=par['Name'], Description=par['Description'],Key=par['Key'], GUID=par['GUID'],Value=par['Value'],Stopcriteria=par['StopCriteria'])
            self.parameterList.append(p)
        #TODO: discuss if we need to add the rules at once?

    def object2json(self):
        """
               Function to generate a json file from the Product model
        """
        return json.dumps(self, default=lambda o: o.__dict__,indent=4)

class ProductPart():
    """
        Product: Class representing the Product Part

         :param string Name: Name of the Product
         :param string ProductType: Product part type
         :param int Quantity: Number of same product parts in product
         :param objectlist parameterList: list of linked parameters
         :param objectlist partList: list of linked product parts
         :param list material: list of the material properties
    """
    def __init__(self, JSONDescriptor=None, Name="", Description="",ProductType='',Quantity=0,parameters = [],partList=[],material = [], DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.ProductType = ProductType
            self.Quantity = Quantity
            self.parameterList = parameters
            self.partList = partList
            self.material = material    #TODO: Stiffness not yet correct

        else:
            self.json2object(JSONDescriptor)
            x = 10

    def json2object(self,jsonDescriptor):
        """
             Function to generate a ProductPart object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the ProductPart

        """

        #--interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)
        #--setup object--
        self.Name = jsonObject['Name']
        self.Description = jsonObject['Description']
        self.ProductType = jsonObject['ProductType']
        self.Quantity = jsonObject['Quantity']
        self.parameterList = []
        for par in jsonObject['parameterList']:
            p = Parameter(None, Name=par['Name'], Description=par['Description'], Key=par['Key'], GUID=par['GUID'],Value=par['Value'], Stopcriteria=par['StopCriteria'])
            self.parameterList.append(p)
        self.partList = []
        for subPart in jsonObject['partList']:
            p = self.getInstance(subPart)
            self.partList.append(p)
        self.material = jsonObject['material']  # TODO: Stiffness not yet correct

    def object2json(self):
        """
               Function to generate a json file from the ProductPart model
        """
        return json.dumps(self, default=lambda o: o.__dict__,indent=4)

    def getInstance(self,subPart):
        """
               Function to fetch a ProductPart model recursively
        """
        part_temp = ProductPart(Name=subPart['Name'],Description=subPart['Description'],ProductType=subPart['ProductType'],Quantity=subPart['Quantity'])

        part_temp.parameterList = []
        for par in subPart['parameterList']:
            p = Parameter(None, Name=par['Name'], Description=par['Description'], Key=par['Key'], GUID=par['GUID'], Value=par['Value'], Stopcriteria=par['StopCriteria'])
            part_temp.parameterList.append(p)
        part_temp.partList = []
        for subPart in subPart['partList']:
            p = self.getInstance(subPart)
            part_temp.partList.append(p)
        part_temp.material = subPart['material']  # TODO: Stiffness not yet correct
        return part_temp

class AssemblySequence():
    """
        Product: Class representing the AssemblySequence

         :param string Name: Name of the AssemblySequence
         :param string Description: Description of the AssemblySequence
         :param list AssemblyMetric: AssemblyMetric identification
         :param objectList assemblyOptions: list of assemblyOption objects
    """

    def __init__(self, JSONDescriptor=None, Name="", Description="", AssemblyMetric=[],AssemblyOptions=None, DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.AssemblyMetric = AssemblyMetric
            self.AssemblyOptions = AssemblyOptions

        else:
            self.json2object(JSONDescriptor)
            x = 10

    def json2object(self, jsonDescriptor):
        """
             Function to generate a AssemblySequence object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the AssemblySequence

        """

        # --interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)


    def object2json(self):
        """
               Function to generate a json file from the AssemblySequence model
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

class Operation():       #
    """
        Product: Class representing the Operation

         :param string Name: Name of the Operation
         :param string Description: Description of the Operation
         :param list Fastner: Fastner identification
         :param list OperationMetric: Operation Metric identification
         :param list Operators: Operators identification
         :param list Tool: Tool identification
         :param objectList AssemblyOperationList: list of assemblyOperations
    """

    def __init__(self, JSONDescriptor=None, Name="", Description="", Fastners=[],OperationMetric=[],Operators = [], Tool=[], DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.Fastners = Fastners
            self.OperationMetric = OperationMetric
            self.Operators = Operators
            self.Tool = Tool


        else:
            self.json2object(JSONDescriptor)
            x = 10

    def json2object(self, jsonDescriptor):
        """
             Function to generate a Operation object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the Operation

        """

        # --interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)


    def object2json(self):
        """
               Function to generate a json file from the Operation model
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

class Contract():       #
    """
        Contract: Class representing the Contract

         :param string Name: Name of the Contract
         :param string Description: Description of the Contract
         :param list Assmuptions: list of contract assumptions
         :param list Guarantees: list of contract guarantees
    """

    def __init__(self, JSONDescriptor=None, Name="", Description="", Assumptions=[],Guarantees=[], DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.Assumptions = Assumptions
            self.Guarantees = Guarantees


        else:
            self.json2object(JSONDescriptor)
            x = 10

    def json2object(self, jsonDescriptor):
        """
             Function to generate a Contract object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the Contract

        """

        # --interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)

            self.Name = jsonObject['Name']
            self.Description = jsonObject['Description']
            self.Assumptions = []
            for asmpt in jsonObject['Assumptions']:
                temp = []
                dv = DomainVariable(Name=asmpt[0]["Name"],Description=asmpt[0]["Description"],Unit=asmpt[0]["Unit"])
                temp.append(dv)
                temp.append(asmpt[1])
                temp.append(asmpt[2])
                self.Assumptions.append(temp)

            self.Guarantees = []
            for grnt in jsonObject['Guarantees']:
                temp = []
                dv = DomainVariable(Name=grnt[0]["Name"], Description=grnt[0]["Description"], Unit=grnt[0]["Unit"])
                temp.append(dv)
                temp.append(grnt[1])
                temp.append(grnt[2])
                self.Guarantees.append(temp)


    def object2json(self):
        """
               Function to generate a json file from the Contract model
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

class Ontology():       #
    """
        Ontology: Class representing the Ontology

         :param string Name: Name of the Ontology
         :param string Description: Description of the Ontology
         :param objectlist Relations: list of relation objects
    """

    def __init__(self, JSONDescriptor=None, Name="", Description="", Relations=[], DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.Relations = Relations


        else:
            self.json2object(JSONDescriptor)
            x = 10

    def json2object(self, jsonDescriptor):
        """
             Function to generate a Ontology object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the Ontology

        """

        # --interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)

            self.Name = jsonObject['Name']
            self.Description = jsonObject['Description']
            self.Relations = []
            for relation in jsonObject['Relations']:
                temp = []
                source = DomainVariable(Name=relation['Source']['Name'],
                                        Description=relation['Source']['Description'],
                                        Unit=relation['Source']['Unit'])
                destination = DomainVariable(Name=relation['Destination']['Name'],
                                        Description=relation['Destination']['Description'],
                                        Unit=relation['Destination']['Unit'])
                r = Relation(Name=relation['Name'], Description=relation['Description'], Source=source,Destination=destination,SensitivityDirection=relation['SensitivityDirection'],Weight=relation['Weight'])
                self.Relations.append(r)


    def object2json(self):
        """
               Function to generate a json file from the Ontology model
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

class Relation():       #
    """
        Relation: Class representing the Relation

         :param string Name: Name of the Relation
         :param string Description: Description of the Relation
         :param object Source: Source object of the relation.
         :param object Destination: Destination object of the relation
         :param string SensitivityDirection: SensitivityDirection of the relation (None = No directional sensitivity information)
         :param float Weight: Sensitivity weight of the relation (None = No sensitivity weight information)
    """

    def __init__(self, JSONDescriptor=None, Name="", Description="", Source = None,Destination = None,SensitivityDirection = None,Weight = 0.0, DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.Source = Source
            self.Destination = Destination
            self.SensitivityDirection = SensitivityDirection
            self.Weight = Weight


        else:
            self.json2object(JSONDescriptor)
            x = 10

    def json2object(self, jsonDescriptor):
        """
             Function to generate a Relation object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the Relation

        """

        # --interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)


    def object2json(self):
        """
               Function to generate a json file from the Relation model
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

class DomainVariable():       #
    """
        DomainVariable: Class representing the DomainVariable

         :param string Name: Name of the DomainVariable
         :param string Description: Description of the DomainVariable
         :param string Unit: Unit of the DomainVariable
    """

    def __init__(self, JSONDescriptor=None, Name="", Description="", Unit="", DEBUG=True):
        self.DEBUG = DEBUG
        if JSONDescriptor is None:
            self.Name = Name
            self.Description = Description
            self.Unit = Unit


        else:
            self.json2object(JSONDescriptor)
            x = 10

    def json2object(self, jsonDescriptor):
        """
             Function to generate a DomainVariable object from a JSON file

             :param string jsonDescriptor: absolute path to the json file for the DomainVariable

        """

        # --interpret JSON file--
        with open(jsonDescriptor, "r") as read_file:
            jsonObject = json.load(read_file)


    def object2json(self):
        """
               Function to generate a json file from the DomainVariable model
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)