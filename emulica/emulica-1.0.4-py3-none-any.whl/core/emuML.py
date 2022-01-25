# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Rémi Pannequin, Centre de Recherche en Automatique de Nancy remi.pannequin@univ-lorraine.fr
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

"""
This module contains utilities to load and save emulica models in XML format.
Only module *configuration* is written : the state of a particular module 
is ignored.
"""
import os.path
from xml.etree.ElementTree import ElementTree, Element, SubElement
#ElementTree._namespace_map["http://www.w3.org/2001/XMLSchema"] = 'xs'
from emulica.core import emulation, properties
import logging, zipfile, pickle

logger = logging.getLogger('emulica.emuML')

class EmuFile(object):
    """This class enable to read or write Emulica files."""
    def __init__(self, filename, mode='r', parent_model=None, name='main'):
        """Create a new instance of a EmuFile file.

        Arguments:
            filename -- the name of the .emu file to open
            mode -- the open mode 'r' for reading, 'w' for writing
            parent_model -- the parent Emulation model, if current model is a 
                            submodel
            name -- the name of the model to load, if it is a submodel

        Raises:
            IOError if a file is absent or not readeable/writable
            FileNotFoundError if a submodel is absent
            EmuMLError if mode is not r or w, or if file in not a valid emu file.
        """
        self.filename = filename
        self.name = name
        self.mode = mode
        if mode == 'r' or mode == 'w':
            self.zfile = zipfile.ZipFile(filename, mode)
            if mode == 'r':
                namelist = self.zfile.namelist()
                if 'emulation.xml' in namelist:
                    model_xml = self.zfile.read('emulation.xml')
                    self.efile = EmulationParser(model_xml,
                                                 name = name,
                                                 path = self.filename,
                                                 parent = parent_model)
                else:
                    raise EmuMLError(_("unable to find emulation.xml"))
                if 'control.py' in namelist:
                    self.control = self.zfile.read('control.py')
                else:
                    raise EmuMLError(_("unable to find control.py"))
                if 'props.db' in namelist:
                    self.__props = pickle.loads(self.zfile.read('props.db'))
                else:
                    raise EmuMLError(_("unable to find props.db"))
        else:
            raise EmuMLError(_("Invalid opening mode, only 'r' (for reading) and 'w' (for writing) are valid modes."))

    def read(self, parent=None, name='main'):
        """Read the content of a model. This class parse the emulation.xml file
        contained in the emu file, and also parse and loads submodels. NB:
        model and submodels properties can be retrieved using get_properties()
        
        Returns:
            a tuple containing the emulation model and the control file
        Raises:
            EmuMLError -- if file was not open in read mode or if the emu
                           file is not correct
            IOError -- if a submodel could not be read
        """
        if self.mode != 'r':
            raise EmuMLError(_("File opened in write mode, cannot read."))
        self.efile.parse()
        return (self.efile.model, self.control)

    def get_properties(self):
        """Return a dictionary of the model and submodels properties. Models are
        identified by their names (the top-model name is 'main')"""
        props = dict()
        props[self.name] = self.__props
        for (name, gsf) in self.efile.submodels.items(): 
            for (name, prop) in gsf.get_properties().items():
                props[name] = prop
        return props

    def write(self, model, control, properties):
        """Write the emu file element into a emu file.

        Arguments:
            model -- the emulation model
            control -- the control system
            properties -- the model properties

        """
        if self.mode != 'w':
            raise EmuMLError(_("File opened in read mode, cannot write."))
        self.write_model(model)
        self.write_control(control)
        self.write_properties(properties)

    def write_model(self, model):
        """Write the emmulation model in the emu file.

        Arguments:
            model -- the model to write

        """
        efile = EmulationWriter(model)
        self.zfile.writestr('emulation.xml', efile.write())

    def write_control(self, control):
        """Write the control string in the emu file.

        Arguments:
            control -- the code (as text) of the control system

        """
        self.zfile.writestr('control.py', control)

    def write_properties(self, props):
        """Write the props dictionary in the emu file (using pickle).

        Arguments:
            props -- a dictionary of model properties

        """
        props_str = pickle.dumps(props) #get emulica config (using pickle)
        self.zfile.writestr('props.db', props_str)

    def close(self):
        """Close the emu file. Any operation is invalid after."""
        try:
            for zinfo in self.zfile.infolist():
                zinfo.external_attr = 600 << 16
        finally:
            self.zfile.close()


class EmulationWriter(object):
    """This class write an emulation model as an xml string"""
    def __init__(self, model):
        """Create a new instance of a emuML.EmulationFile.

        Arguments:
            model -- the model from which extract modules

        """
        self.model = model

    def write(self):
        """Return an XML string that correspond to model. NB: submodels are not
        outputed."""
        from xml.etree.ElementTree import tostring
        root = Element("emulationModel")
        input_root = SubElement(root, "interface")
        for (name, (module_name, property_name)) in self.model.inputs.items():
            input_elt = SubElement(input_root, "input")
            input_elt.attrib['name'] = name
            input_elt.attrib['module'] = module_name
            input_elt.attrib['property'] = property_name
        mod_root = SubElement(root, "modules")
        #model structure
        for (name, mod) in self.model.modules.items():
            if mod.is_model():
                mod_root.append(self.marshall_submodel(mod))
            else:
                mod_root.append(self.marshall_module(mod))
        tree = ElementTree(root)
        return tostring(root)

    def marshall_submodel(self, module):
        """Return a XML element that represent a submodel inclusion (and its properties)"""
        #create a 
        submodel_elt = Element("submodel")
        submodel_elt.attrib['name'] = module.name
        submodel_elt.attrib['path'] = module.path#TODO: modify mod.path to a relative path ?
        for (name, prop) in module.properties.items():
            prop_elt = SubElement(submodel_elt, "property")
            prop_elt.attrib["name"] = name
            self.marshall_value(prop_elt, prop)
            logger.debug("marshaling attribute {0} with value {1} for module {2}".format(name, prop, module.name))
        return submodel_elt

    def marshall_module(self, module):
        """Return a XML element that represents the module.

        Arguments:
            module -- the module to marshall

        """
        mod_elt = Element("module")
        mod_elt.attrib["name"] = module.name
        mod_elt.attrib["type"] = module.__class__.__name__
        for (name, prop) in module.properties.items():
            prop_elt = SubElement(mod_elt, "property")
            prop_elt.attrib["name"] = name
            self.marshall_value(prop_elt, prop)
            logger.debug("marshaling attribute {0} with value {1} for module {2}".format(name, prop, module.name))
        return mod_elt


    def marshall_value(self, root, value):
        """Append one or several elements to root. If value is None, nothing is
        appended, if value is a list, an element is append for each object of
        the list, else one element is appended.

        Arguments:
            root -- the element to which append the created element
            value -- the property to marshall

        """
        if value is None:
            logger.warning("marshalling a null value")
        elif type(value) == list:
            list_root = SubElement(root, 'value-list')
            for v in value:
                self.marshall_value(list_root, v)
        else:
            if value.__class__.__name__ == 'ProgramTable':
                #program-table element
                self.marshall_prog(root, value)
            elif value.__class__.__name__ == 'SetupMatrix':
                #setup-table element
                self.marshall_setup(root, value)
            elif value.__class__.__name__ == 'ChangeTable':
                #change-table element
                self.marshall_change(root, value)
            elif 'fullname' in dir(value):
                #reference element
                elt = SubElement(root, 'reference')
                elt.text = value.fullname()
            else:
                #value element
                elt = SubElement(root, 'value')
                elt.text = str(value)
                #TODO: manage type ?
                #elt.attrib["type"] = str(type(value))

    def marshall_prog(self, root, table):
        """Append an Element that represents a program table to element 
        prog_root.

        Arguments:
            root -- the program table to marshall
            table -- the element to which append the created element

        """
        prog_root = SubElement(root, 'program-table')
        #get program structure, write as attribute
        schema = [name for (name, display) in table.program_keyword]
        schema_str = '['+','.join(schema)+']'
        prog_root.attrib["schema"] = schema_str
        for (name, p) in table.items():
            prog = SubElement(prog_root, "program")
            prog.attrib["name"] = name
            prog.attrib["delay"] = str(p.time_law)
            if p.transform and 'items' in dir(p.transform):
                for (n, e) in p.transform.items():
                    elt = SubElement(prog, 'transform')
                    elt.attrib['name'] = n
                    self.marshall_value(elt, e)

    def marshall_setup(self, root, table):
        """Append a setup-table Element that represents a setup table to element 
        root.

        Arguments:
            root -- the element to which append the created element
            table -- the setup table to marshall

        """
        setup_root = SubElement(root, 'setup-table')
        setup_root.attrib["default_delay"] = str(table.default_time)
        for (initial, final, delay) in table.items():
            setup = SubElement(setup_root, 'setup')
            setup.attrib['initial'] = initial
            setup.attrib['final']  = final
            setup.attrib['delay'] = str(delay)


    def marshall_change(self, root, table):
        """Append a change-table Element that represents a change table to element 
        root.

        Arguments:
            root -- the element to which append the created element
            table -- the setup table to marshall
           """
        change_root = SubElement(root, 'change-table')
        for (name, value) in table.items():
            change = SubElement(change_root, 'change')
            change.attrib["property"] = name
            self.marshall_value(change, value)


class EmulationParser(object):
    """This class can be used to get an Emulation Model from an xml file."""
    def __init__(self, string, model = None, parent = None, name = 'main', path = None):
        """Create a new instance of a emuML.EmulationParser. When the object is 
        created, the string is parsed, and submodels list is built. Beware: the
        submodels files are opened at this stage ! If the model argument is 
        specified, it is used to load modules into, else a new model is created 
        using the kwargs.
        
        Arguments:
            string -- the model into which load modules or from which extract modules
            model -- the model to load modules into
            *kwargs -- keywords argumenst to be passed to the Model constructor
        Raises:
            ???Error -- if string is not well formed   
         
        """
        from xml.etree.ElementTree import fromstring
        self.tree = fromstring(string)
        self.model = model or emulation.Model(model = parent, name = name, path = path)
        self.submodels = dict()
        mod_root = self.tree.find("modules")
        for submodel_elt in mod_root.findall("submodel"):
            #try loading emu file for every submodels
            sub_path = submodel_elt.get('path')
            #TODO If sub_path is a relative pathname, interpret it where the current model is
            if not os.path.isabs(sub_path):
                base = os.path.dirname(path)
                sub_path = os.path.join(base, sub_path)
            sub_name = submodel_elt.get('name')
            gsf = EmuFile(sub_path, 'r', parent_model = self.model, name = sub_name)
            #TODO: if opening fails, add name to a list of broken submodels
            self.submodels[sub_name] = gsf
        self.renaming = dict()
    
    def load_submodels(self):
        """Load submodels in the model"""
        for (name, gsf) in self.submodels.items():
            (submodel, subcontrol) = gsf.read()
            #compile and register control in model
            compile_control(submodel, subcontrol)    
    
    def parse(self):
        """Load a set of modules from an XML string or treeset into the model, 
        and Return the list of created modules.
        
        Arguments:
            string -- an XML string that represent the model.
            
        Return 
            the list of created modules
        
        """
        
        mod_root = self.tree.find("modules")
        mod_list = []
        properties_elt = dict()
        #loads submodels first (if any)
        self.load_submodels()
        #loads modules
        for mod_elt in mod_root.findall("module"):
            mod_type = mod_elt.get("type")
            name = mod_elt.get("name")
            if name in self.model.modules:
                new_name = mod_type+str(len(self.model.modules))
                self.renaming[name] = new_name
                logger.warning("renaming module: " + name + " to: "+new_name)
                name = new_name
            logger.info("creating module: " + name + " of type: "+mod_type)
            mod_class = getattr(emulation, mod_type)
            mod = mod_class(self.model, name)
            mod_list.append(mod)
            properties_elt[mod] = mod_elt.findall('property')
            
        #build model structure
        for mod, prop_list in properties_elt.items():
            for prop_elt in prop_list:
                name = prop_elt.get('name')
                value = self.parse_child_as_value(mod.properties, name, prop_elt)
                #print "property {0} = {1}".format(name, value)
                mod.properties[name] = value
        #get inputs
        interface_root = self.tree.find('interface')
        if not interface_root is None:
            for input_elt in interface_root.findall('input'):
                name = input_elt.get('name')
                module = input_elt.get('module')
                prop = input_elt.get('property')
                self.model.inputs[name] = (module, prop)
            #if model has parent, call apply_inputs
            if not self.model.is_main:
                self.model.apply_inputs()
        #load submodel properties
        for submodel_elt in mod_root.findall('submodel'):
            submodel = self.model.get_module(submodel_elt.get('name'))
            for prop_elt in submodel_elt.findall('property'):
                name = prop_elt.get('name')
                value = self.parse_child_as_value(submodel.properties, name, prop_elt)
                #print "property {0} = {1}".format(name, value)
                submodel.properties[name] = value
        return mod_list

    def parse_child_as_value(self, props, root_prop_name, element):
        """Parse the children of element as values (or list of values)"""
        children = element.getchildren()
        if len(children) == 0:
            logger.warning("returning None when parsing element")
            return None
        elif len(children) == 1:
            return self.parse_value(props, root_prop_name, children[0])
        else:
            logger.warning("wrong number of values")

    def parse_value(self, props, root_prop_name, element):
        """Parse a module property and return the resulting object
        
        Arguments:
            module -- the module which the property belongs
            element -- the Element to parse
        
        Returns:
            the parsed value
            
        """
        if element.tag == 'value':
            elt_type = element.get("type")
            #TODO: get type and cast to type
            try:
                return eval(element.text)
            except (NameError, AttributeError):
                return element.text
                
        elif element.tag == 'value-list':
            children = element.getchildren()
            value = list()
            for child in children:
                value.append(self.parse_value(props, root_prop_name, child))
            return value
        elif element.tag == 'reference':
            name = element.text
            if name in self.renaming:
                name = self.renaming[name]
            return self.model.get_module(name)
        elif element.tag == 'program-table':
            return self.parse_prog(props, root_prop_name, element)
        elif element.tag == 'setup-table':
            return self.parse_setup(props, root_prop_name, element)
        elif element.tag == 'change-table':
            return self.parse_change(props, root_prop_name, element)
        else:
            #error case
            logger.warning("errror: unknow tag {0}".format(element.tag))

    def parse_prog(self, props, root_prop_name, element):
        """Parse a program table and return the resulting object.

        Arguments:
            element -- the Element to parse

        Returns:
            the parsed program table (type dictionary)

        """
        #get the program table schema
        schema_str = element.get("schema")
        context = {'source': ('source', properties.Display(properties.Display.REFERENCE, _("Source"))),
                   'destination': ('destination',properties.Display( properties.Display.REFERENCE, _("Destination"))),
                   'change': ('change', properties.Display(properties.Display.PHYSICAL_PROPERTIES_LIST, _("Physical changes")))}
        if schema_str is None:
            if 'program_keyword' in dir(props.owner):
                schema = props.owner.program_keyword
            else:
                logger.warning(_("unable to determine program schema"))
                schema = []
        else:
            schema = eval(schema_str, globals(), context)
        table = properties.ProgramTable(props, root_prop_name, schema)
        for program in element.findall('program'):
            delay = program.get("delay")
            #get transform
            transform = dict()
            for elt in program.findall('transform'):
                value = self.parse_child_as_value(props, root_prop_name, elt)
                transform[elt.get("name")] = value      
            name = program.get("name")
            assert(not name is None)
            table.add_program(name, delay, transform)
        return table

    def parse_setup(self, props, root_prop_name, element):
        """Parse a setup table and return the resulting object.

        Arguments:
            element -- the Element to parse

        Returns:
            the parsed SetupTable

        """
        default_delay = element.get("default_delay")
        setup = properties.SetupMatrix(props, default_delay, root_prop_name)
        for s in element.findall('setup'):
            delay = eval(s.get("delay"))
            init = s.get("initial")
            final = s.get("final")
            assert(not init is None)
            assert(not final is None)
            setup.add(init, final, delay)
        return setup

    def parse_change(self, props, root_prop_name, element):
        """Parse a change table and return the resulting object"""
        table = properties.ChangeTable(props, root_prop_name)
        for child in element.findall('change'):
            name = child.get("property")
            assert(not name is None)
            value = self.parse_child_as_value(props, root_prop_name, child)
            table[name] = value
        return table

def compile_control(model, source, **kwargs):
    """compile code in the control buffer. The global environment that is available
    in the control code is the package emulation, and classes Request and Report.
    The control code must provide a function initialize_control that registers the
    control modules in the model.
    
    Arguments:
        model -- the model into which load the control
        source -- the source code of the control system

    Any other keyword argument can be added : these kw arguments will be passed
    to the initialize_control method of the source. 

    Returns: 
        True if no error are found.

    Raises:
        SyntaxError -- if there is syntax error in the source
        EmuMLError -- if init function has not been declared

    """
    code = compile(source,'<control buffer>', 'exec')
    g = globals()
    env = dict()
    env['emulation'] = emulation
    env['Request'] = emulation.Request
    env['Report'] = emulation.Report
    l = dict()
    exec(code, env, l)
    logger.info(_("control code compilation sucessfull"))
    if not 'initialize_control' in l:
        raise EmuMLError(_("initialization function have not been implemented"))
    model.control_classes = []
    #This function come from the code we just compiled and executed
    init_function = l['initialize_control']
    init_function(l, model, **kwargs)

def save_modules(model, modules):
    """Return an XML string that represent these modules. Used to cut or copy 
    modules.
    
    Arguments:
        model -- the model (context, useful for references)
        modules -- the list of module to marshall
        
    """
    from xml.etree.ElementTree import tostring
    writer = EmulationWriter(model)
    top = Element("emulationClip")
    mod_root = SubElement(top, "modules")
    #model structure
    for mod in modules:
        mod_root.append(writer.marshall_module(mod))
    return tostring(top)

def load_modules(model, elt):
    """Convenience function to load a set of modules from an XML string in the 
    model. Used to paste modules.
    
    Arguments:
        model -- the model where the module are loaded
        elt -- the XML string that describes the modules
    """
    parser = EmulationParser(elt, model = model)
    parser.parse()

def save(model, filename=None):
    """Convenience function to save a model to a file. If filename is not set, 
    the resulting xml string is returned."""
    writer = EmulationWriter(model)
    if filename is None:
        return writer.write()
    else:
        try:
            efile = open(filename, 'w')
            content = writer.write()
            efile.write(content)
        finally:
            efile.close()

def load(filename):
    """Convenience function that returns a new Model from a file"""
    f = open(filename, 'r')
    content = f.read()
    f.close()
    efile = EmulationParser(content, path = filename)
    efile.parse()
    return efile.model

def parse_request(message):
    """Parse a XML message and return a Request instance
    
    Returns:
        a emulation.Request instance
        
    Raises:
        EmuMLError -- if the request doesn't respects schema
        
    """
    from xml.etree.ElementTree import fromstring
    try:
        root = fromstring(message)
    except Exception as message:
        raise EmuMLError(message)
    attributes = dict()
    elt = root.find('who')
    if elt == None: 
        raise EmuMLError("request message does not specify who must execute it")
    who = elt.text
    elt = root.find('what')
    if elt == None: 
        raise EmuMLError("request message does not specify what to execute")
    what = elt.text
    rq = emulation.Request(who, what)
    elt = root.find("how")
    if not elt == None:
        for e in elt.findall("element"):
            try:
                value = e.text
            except (SyntaxError, NameError):
                value = e.text
            rq.how[e.attrib["name"]] = value
    elt = root.find("where")
    if not elt == None:
        rq.where = elt.text
    elt = root.find("when")
    if not elt == None:
        try:
            rq.when = float(elt.text)
        except ValueError:
            raise EmuMLError("""'{0}' could not be recognized as a date (float)""".format(elt.text))
    elt = root.find("why")
    if not elt == None:
        rq.why = elt.text
    return rq

def parse_report(message):
    """Parse a XML message and return a Report instance
    
    Returns:
        a emulation.Report instance
        
    Raises:
        EmuMLError -- if the request doesn't respects schema
        
    """
    from xml.etree.ElementTree import fromstring
    try:
        root = fromstring(message)
    except Exception as message:
        raise EmuMLError(message)
    attributes = dict()
    elt = root.find('who')
    if elt == None: 
        raise EmuMLError("request message does not specify who must execute it")
    who = elt.text
    elt = root.find('what')
    if elt == None: 
        raise EmuMLError("request message does not specify what to execute")
    what = elt.text
    rp = emulation.Report(who, what)
    elt = root.find("how")
    if not elt == None:
        for e in elt.findall("element"):
            try:
                value = eval(e.text)
            except (SyntaxError, NameError):
                value = e.text
            rp.how[e.attrib["name"]] = value
    elt = root.find("where")
    if not elt == None:
        rp.where = elt.text
    elt = root.find("when")
    if not elt == None:
        try:
            rp.when = float(elt.text)
        except ValueError:
            raise EmuMLError("""'{0}' could not be recognized as a date (float)""".format(elt.text))
    elt = root.find("why")
    if not elt == None:
        rp.why = elt.text
    return rp

def write_report(report):
    """Return an XML message from a report object"""
    from xml.etree.ElementTree import tostring
    root = Element("report")
    for attr in ['who', 'what', 'where', 'why', 'when']:
        value = getattr(report, attr)
        if value:
            elt = SubElement(root, attr)
            elt.text = str(value)
    how_elt = SubElement(root, 'how')
    for (name, value) in report.how.items():
        elt = SubElement(how_elt, 'element')
        elt.attrib['name'] = name
        elt.text = str(value)
    return tostring(root)

def write_request(request):
    """Return an XML message from a request object"""
    from xml.etree.ElementTree import tostring
    root = Element("request")
    for attr in ['who', 'what', 'when', 'where', 'why']:
        value = getattr(request, attr)
        if value:
            elt = SubElement(root, attr)
            elt.text = str(value)
    how_elt = SubElement(root, 'how')
    for (name, value) in request.how.items():
        elt = SubElement(how_elt, 'element')
        elt.attrib['name'] = name
        elt.text = str(value)
    return tostring(root)


class EmuMLError(Exception):
    """This class is used to deal with exception ancountrered when reading or 
    writing a file."""
