import os
import re
from pyecore.ecore import EClass
from pyecore.resources import ResourceSet, URI
from pyecore.resources.xmi import XMIResource
from pyecore.utils import DynamicEPackage
#----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                 HELPER FUNCTIONS
#----------------------------------------------------------------------------------------------------------------------------------------------------
def updateKB(model):
    """
      For internal use only!
    """
    #TODO: update the current MM instead of the new one
    export_metamodel('C:/Users/B.MKR/Documents/06_PhD/03_Projects/03_PaCo/paco-workspace/PythonProjects/Master2/UA/API/unit-tests/output/OldGearBox.xmi',model)

def updateKBv6(KB_path,model):
    """
      For internal use only!
    """
    #TODO: update the current MM instead of the new one
    export_metamodel(KB_path,model)
    #necessary post-processing functions due to prefix error
    postProcess_prefix(KB_path)
    postProcess_DFARule(KB_path)
    postProcess_OptimizationProblem(KB_path)
    postProcess_AssemblySystem(KB_path)
    postProcess_platformRoot(KB_path)

def resolvePath(relativePath):
    """
      For internal use only!
    """
    return os.path.abspath(relativePath)

def importInstanceModel(path_ecore, path_instance, VERBOSE=False):
    """
      For internal use only!
    """
    rset = ResourceSet()
    # add external mm resources
    rset = addXMLResource(rset)

    resource = rset.get_resource(URI(path_ecore))
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root
    # At this point, the .ecore is loaded in the 'rset' as a metamodel
    resource = rset.get_resource(URI(path_instance))
    model_root = resource.contents[0]
    model = model_root

    #instantiate MM
    initialize(path_ecore)

    return model

def addXMLResource(rset):
    """
      For internal use only!
    """
    import pyecore.ecore as Ecore
    int_conversion = lambda x: int(x)  # translating str to int durint load()
    String = Ecore.EDataType('String', str)
    Double = Ecore.EDataType('Double', int, 0, from_string=int_conversion)
    Int = Ecore.EDataType('Int', int, from_string=int_conversion)
    IntObject = Ecore.EDataType('IntObject', int, None,
                                from_string=int_conversion)
    Boolean = Ecore.EDataType('Boolean', bool, False,
                              from_string=lambda x: x in ['True', 'true'],
                              to_string=lambda x: str(x).lower())
    Long = Ecore.EDataType('Long', int, 0, from_string=int_conversion)
    EJavaObject = Ecore.EDataType('EJavaObject', object)
    #TODO:add the enum translations

    xmltype = Ecore.EPackage()
    xmltype.eClassifiers.extend([String,
                                 Double,
                                 Int,
                                 EJavaObject,
                                 Long,
                                 Boolean,
                                 IntObject])
    xmltype.nsURI = 'http://www.eclipse.org/emf/2003/XMLType'
    xmltype.nsPrefix = 'xmltype'
    xmltype.name = 'xmltype'
    rset.metamodel_registry[xmltype.nsURI] = xmltype

    return rset

def initialize( model_uri):
    """
    Initialization function to read in the MetaModel  from the ecore resource file.
        :param model_uri: URI to the ecore model file, either in URI or in string format.
        :return: A dynamic instantiation of the MetaModel, able create instances of its EClasses.
    """

    # Check if the provided URI contains a valid value
    if isinstance(model_uri, str):
        model_uri = URI(model_uri)
    if not isinstance(model_uri, URI):
        raise TypeError(f"model_uri expected to be of type f{URI}, but received {type(model_uri)}")

    # Create and initialize the resource set
    rset = ResourceSet()
    resource = rset.get_resource(model_uri)
    root_package = resource.contents[0]

    # Create a dynamic metamodel able to create instances of EClasses
    MM = DynamicEPackage(root_package)

    # Instantiate the root object -> this is hard coded for PACo
    root_object = MM.PlatformRoot()

    MM = MM
    model_instance = root_object

    return MM,model_instance


def serialize( xmi_uri,model):
    """
    Serializes the model instance to an EMF-readable XMI-file.
        :param xmi_uri: URI for the xmi-file to be created, either in URI or in string format.
    """

    # Check if the provided URI contains a valid value
    if isinstance(xmi_uri, str):
        xmi_uri = URI(xmi_uri)
    if not isinstance(xmi_uri, URI):
        raise TypeError(f"xmi_uri expected to be of type f{URI}, but received {type(xmi_uri)}")

    resource = XMIResource(xmi_uri)
    resource.append(model)
    resource.save()

def create( e_class,MM,model_instance):
    """
        Generic create function to create instances of a specific EClass as defined by the MetaModel

       :param e_class class: The EClass to create an instance of, specified either as a string or as an EClass
       :return object createdObject: The created EObject
    """

    # Check if e_class contains a valid value
    if isinstance(e_class, str):
        e_class = getattr(MM, e_class)
    if e_class not in list(vars(MM).values()):
        raise TypeError(f"e_class of type {type(e_class)} not recognized.")

    # Create the object
    e_object = e_class()

    # Attach the created object to the root object
    root_reference = getattr(model_instance, 'includes' + e_class.name)
    #root_reference.append(e_object)            #original
    # updated - to support lists of elements
    try:
        root_reference.items.append(e_object)
    except:
        root_reference.append(e_object)

    return e_object

def create_custom( object,e_class,MM):
    """
        Generic create function to create instances of a specific EClass as defined by the MetaModel

        :param e_class class: The EClass to create an instance of, specified either as a string or as an EClass
        :return object createdObject: The created EObject
    """

    # Check if e_class contains a valid value
    if isinstance(e_class, str):
        e_class = getattr(MM, e_class)
    if e_class not in list(vars(MM).values()):
        raise TypeError(f"e_class of type {type(e_class)} not recognized.")

    # Create the object
    e_object = e_class()

    # Attach the created object to the root object
    root_reference = getattr(object, 'has' + e_class.name)
    # updated - to support lists of elements
    try:
        root_reference.items.append(e_object)
    except:
        root_reference.append(e_object)

    return e_object


def create_noPlatformRoot( e_class,MM,model_instance):
    """
        Generic create function to create instances of a specific EClass as defined by the MetaModel but don't link to the platformRoot

       :param e_class class: The EClass to create an instance of, specified either as a string or as an EClass
       :return object createdObject: The created EObject
    """

    # Check if e_class contains a valid value
    if isinstance(e_class, str):
        e_class = getattr(MM, e_class)
    if e_class not in list(vars(MM).values()):
        raise TypeError(f"e_class of type {type(e_class)} not recognized.")

    # Create the object
    e_object = e_class()

    # Attach the created object to the root object
    #root_reference = getattr(model_instance, 'includes' + e_class.name)
    #root_reference.append(e_object)            #original
    #root_reference.items.append(e_object)      #updated

    return e_object



def export_metamodel( output_file,model):
    """
        Exports the python data into an xmi file defined by an Ecore model

        :param object model: instantiation of the meta-model
        :param string path: path of the output xmi file
    """
    # Save to xmi file
    serialize(output_file,model)

    # open file to manually add missing attribute in root element (@ToDo clean this up)
    with open(output_file, "r") as file:
        data = file.read()

    target = 'xmi:version="2.0">'
    replacement = 'xmi:version="2.0" xsi:schemaLocation="http://www.ua.be/cosys/paco/PACoMM PACoMM.ecore">'

    with open(output_file, "w") as file:
        data.replace(target, replacement)
        file.write(data)

    file.close()

def postProcess_prefix( output_file):
    """
        Custom postprocessing function to clean the xmi file defined by an Ecore model

        :param string path: path of the output xmi file
    """
    # open file to manually add missing attribute in root element (@ToDo clean this up)
    with open(output_file, "r") as file:
        data = file.read()

    # Prefix replacement
    target = '<paco:'
    replacement = '<includes'

    with open(output_file, "w") as file:
        data_new = data.replace(target, replacement)
        file.write(data_new)

    file.close()

def postProcess_platformRoot( output_file):
    """
        Custom postprocessing function to clean the xmi file defined by an Ecore model

        :param string path: path of the output xmi file
    """
    # open file to manually add missing attribute in root element (@ToDo clean this up)
    with open(output_file, "r") as file:
        data = file.read()

    # Prefix replacement
    target = 'includesPlatformRoot'
    replacement = 'paco:PlatformRoot'

    with open(output_file, "w") as file:
        data_new = data.replace(target, replacement)
        file.write(data_new)

    file.close()

def postProcess_DFARule( output_file):
    """
        Custom postprocessing function to clean the xmi file defined by an Ecore model

        :param string path: path of the output xmi file
    """
    # open file to manually add missing attribute in root element (@ToDo clean this up)
    with open(output_file, "r") as file:
        data = file.read()

    # Prefix replacement
    target = '<includesDFA_Rule'
    replacement = '<hasDFARule'

    with open(output_file, "w") as file:
        data_new = data.replace(target, replacement)
        file.write(data_new)

    file.close()

def postProcess_OptimizationProblem( output_file):
    """
        Custom postprocessing function to clean the xmi file defined by an Ecore model

        :param string path: path of the output xmi file
    """
    # open file to manually add missing attribute in root element (@ToDo clean this up)
    with open(output_file, "r") as file:
        data = file.read()

    # Prefix replacement
    target = '</paco:OptimizationProblem'
    replacement = '</includesOptimizationProblem'

    with open(output_file, "w") as file:
        data_new = data.replace(target, replacement)
        file.write(data_new)

    file.close()

def postProcess_AssemblySystem( output_file):
    """
        Custom postprocessing function to clean the xmi file defined by an Ecore model

        :param string path: path of the output xmi file
    """
    # open file to manually add missing attribute in root element (@ToDo clean this up)
    with open(output_file, "r") as file:
        data = file.read()

    # Prefix replacement
    target = '</paco:AssemblySystem'
    replacement = '</includesAssemblySystem'

    with open(output_file, "w") as file:
        data_new = data.replace(target, replacement)
        file.write(data_new)

    file.close()
