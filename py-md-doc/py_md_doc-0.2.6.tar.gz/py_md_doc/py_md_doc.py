from json import loads
from pathlib import Path
import re
from typing import List, Dict, Union
from py_md_doc.parameter import Parameter


class PyMdDoc:
    """
    Generate Markdown documentation for your Python scripts.

    ```python
    from pathlib import Path
    from py_md_doc import PyMdDoc

    if __name__ == "__main__":
        md = PyMdDoc(input_directory=Path("."),
                     files=["py_md_doc/py_md_doc.py", "py_md_doc/parameter.py"],
                     metadata_path="metadata.json")
        md.get_docs(output_directory=Path("docs"))
    ```

    """

    """:class_var
    This is a test class variable. It doesn't do anything in this code other than test that the documentation generates correctly.
    """
    CLASS_VAR: int = 0

    def __init__(self, input_directory: Union[Path, str], files: List[str],
                 metadata_path: Union[Path, str] = None):
        """
        :param input_directory: The path to the root input directory for the Python scripts. Can be a `Path` or `str`.
        :param files: A list of Python script filenames relative to `input_directory`. This script will generate documentation only for these files.
        :param metadata_path: The path to the metadata file. Can be None. See the README for how to format this file.
        """

        if isinstance(input_directory, Path):
            pass
        elif isinstance(input_directory, str):
            input_directory = Path(input_directory)
        else:
            raise Exception("Invalid type: input_directory must be of type str or Path.")

        """:field
        A list of paths to each Python script file as `Path` objects.
        """
        self.files: List[Path] = list()
        for f in files:
            filepath = input_directory.joinpath(f)
            assert filepath.exists(), f"File not found: {filepath}"
            self.files.append(filepath)

        # Load the metadata.
        if metadata_path is None:
            """:field
            The metadata dictionary loaded from the metadata file. If there is no metadata file, this is empty.
            """
            self.metadata = dict()
        if metadata_path is not None:
            if isinstance(metadata_path, Path):
                pass
            elif isinstance(metadata_path, str):
                metadata_path = Path(metadata_path)
            else:
                raise Exception("Invalid type: categories_path must be of type str or Path.")
            self.metadata = loads(metadata_path.read_text(encoding="utf-8"))
        """:field
        The expected name of the root import name, derived the input directory.
        
        ```python
        from py_md_doc import PyMdDoc
        from pathlib import Path

        # Generates the documentation for the py_md_doc module.
        md = PyMdDoc(input_directory=Path("my_module"), files=["my_file.py"])
        print(md.root_import_name) # my_module
        ```
        """
        self.root_import_name = input_directory.name

        """:field
        A list of special import statements from `__init__.py`
        """
        self.special_imports: List[str] = list()

        init_path = input_directory.joinpath("__init__.py")
        if init_path.exists():
            init_txt = init_path.read_text(encoding="utf-8")
            for line in init_txt.split("\n"):
                special_import_match = re.match(r"from \.(.*) import (.*)", line)
                if special_import_match is not None:
                    self.special_imports.append(special_import_match.group(2))

    def get_docs(self, output_directory: Union[Path, str], import_prefix: str = None) -> None:
        """
        Generate documents for all of the Python files and write them to disk.

        :param output_directory: The path to the output directory. Can be of type `Path` or `str`.
        :param import_prefix: If not None, replace the import prefix with this import prefix.
        """

        if isinstance(output_directory, Path):
            pass
        elif isinstance(output_directory, str):
            output_directory = Path(output_directory)
        else:
            raise Exception("Invalid type: output_directory must be of type str or Path.")

        if not output_directory.exists():
            output_directory.mkdir(parents=True)

        for f in self.files:
            # Create the documentation.
            doc = self.get_doc(file=f, import_prefix=import_prefix)
            # Name the document based on the name of the Python script. Write it to disk.
            output_directory.joinpath(f.name[:-3] + ".md").write_text(doc, encoding="utf-8")

    def get_doc(self, file: Path, import_prefix: str = None) -> str:
        """
        Create a document from a Python file with the API for each class. Returns the document as a string.

        :param file: The path to the Python script.
        :param import_prefix: If not None, replace the import prefix with this import prefix.
        """

        # Create the header.
        doc = ""

        file_txt = file.read_text(encoding="utf-8")
        lines: List[str] = file_txt.split("\n")

        class_name = ""
        functions_by_categories = {"": []}
        looking_for_class: bool = True
        for i in range(len(lines)):
            # Create a class description.
            if lines[i].startswith("class"):
                # Skip private classes.
                match = re.search("class _(.*):", lines[i])
                if match is not None:
                    continue
                looking_for_class = False
                # Add the name of the class
                class_name = re.search("class (.*):", lines[i]).group(1)
                class_header = re.sub(r"(.*)\((.*)\)", r"\1", class_name)

                functions_by_categories.clear()

                doc += f"# {class_header}\n\n"

                # Add an example import statement.
                if class_header in self.special_imports:
                    import_example = f"`from {self.root_import_name} import {class_header}`"
                else:
                    import_example = f"`from {self.root_import_name}.{file.name[:-3]} import {class_header}`"
                doc += import_example + "\n\n"
                doc += PyMdDoc.get_class_description(file_txt)
                # Parse an enum.
                is_enum = False
                for enum_type in ["Enum", "IntEnum", "IntFlag", "Flag"]:
                    if re.search(r"class (.*)\(" + enum_type + r"\):", lines[i]) is not None:
                        is_enum = True
                        break
                if is_enum:
                    doc += "\n\n" + PyMdDoc.get_enum_values(lines, i)
                else:
                    doc += "\n\n***\n\n"
                # Get class variables.
                class_variables = PyMdDoc.get_class_variables(lines, i)
                if class_variables != "":
                    doc += f"## Class Variables\n\n{class_variables}\n\n***\n\n"
            # Create a function description.
            elif lines[i].strip().startswith("def ") and not looking_for_class:
                # Skip private functions.
                match = re.search("def _(.*)", lines[i])
                if match is not None and "__init__" not in lines[i]:
                    continue
                if "__init__" in lines[i]:
                    field_documentation = PyMdDoc.get_fields(lines, i)
                    if field_documentation != "":
                        doc += f"## Fields\n\n{field_documentation}\n\n***\n\n## Functions\n\n"
                    else:
                        doc += "## Functions\n\n"

                # Append the function description.
                function_documentation = PyMdDoc.get_function_documentation(lines, i, class_name) + "\n\n"
                function_name = re.search("#### (.*)", function_documentation).group(1).replace("\\_", "_")

                # Categorize the functions.
                function_category = ""
                if class_name in self.metadata:
                    for category in self.metadata[class_name]:
                        if function_name in self.metadata[class_name][category]["functions"]:
                            function_category = category
                            break
                    if function_category == "":
                        print(f"Warning: Uncategorized function {class_name}.{function_name}()")
                if function_category == "":
                    doc += function_documentation
                # Add this later.
                else:
                    if function_category not in functions_by_categories:
                        functions_by_categories[function_category] = list()
                    functions_by_categories[function_category].append(function_documentation)
        if class_name in self.metadata:
            for category in self.metadata[class_name]:
                # Ignore anything in the Ignore category.
                if category == "Ignore":
                    continue
                if category != "Constructor":
                    doc += f"### {category}\n\n"
                    if self.metadata[class_name][category]["description"] != "":
                        category_desc = self.metadata[class_name][category]["description"]
                        category_desc = re.sub(r"^(.(.*))", r"\1", category_desc, flags=re.MULTILINE)
                        doc += f'{category_desc}\n\n'
                for function in functions_by_categories[category]:
                    doc += function
                doc += "***\n\n"
        # Add a table of contents.
        doc = doc.replace("[TOC]", PyMdDoc.get_toc(doc))
        # Add an import prefix.
        doc = PyMdDoc._get_doc_with_import_prefix(doc=doc, import_prefix=import_prefix)
        return doc

    def get_docs_with_inheritance(self, abstract_class_path: Union[str, Path],
                                  child_class_paths: List[Union[str, Path]],
                                  import_prefix: str = None) -> Dict[str, str]:
        """
        Generate documentation with basic (one level deep) class inheritance.

        :param abstract_class_path: The path to the abstract or base class.
        :param child_class_paths: A list of paths to the child classes.
        :param import_prefix: If not None, replace the import prefix with this import prefix.

        :return: A dictionary. Key = The name of the class. Value = The markdown documentation as a string.
        """

        docs: Dict[str, str] = dict()
        if isinstance(abstract_class_path, str):
            abstract_class_path: Path = Path(abstract_class_path)

        # Get the raw text from the abstract class Python file.
        abstract_py = abstract_class_path.read_text(encoding="utf-8")
        # Get all of the abstract functions. We'll mark them on the doc at the very end of this function.
        abstract_defs: List[str] = re.findall(r"@abstractmethod\n\s+def (.*?)\(", abstract_py, flags=re.MULTILINE)

        # Generate a doc for the abstract class.
        abstract_doc = self.get_doc(abstract_class_path)

        # Get class variables from the abstract class.
        class_variables_search = re.search(r"## Class Variables\n((.|\n)*?)\*", abstract_doc)
        if class_variables_search is not None:
            # Get a list of class variables by converting the table into a list of row strings.
            abstract_class_variables = re.findall(r"(\| `(.*)` \| (.*) \| (.*) \|$)",
                                                  class_variables_search.group(0),
                                                  flags=re.MULTILINE)
            abstract_class_variables: List[str] = [a[0] for a in abstract_class_variables]
        else:
            abstract_class_variables: List[str] = list()

        # Get fields from the abstract class.
        fields_search = re.search(r"## Fields\n((.|\n)*?)(#|\Z)", abstract_doc)
        if fields_search is not None:
            # Get a list of fields by converting the bullet-point list into a list of strings.
            abstract_fields = re.findall(r"(- `(.*?)`(.*)$)", fields_search.group(0), flags=re.MULTILINE)
            abstract_fields: List[str] = [a[0] for a in abstract_fields]
        else:
            abstract_fields: List[str] = list()

        # Get functions from the abstract class.
        functions_search = re.search(r"## Functions\n((.|\n)*?)\Z", abstract_doc, flags=re.MULTILINE)
        if functions_search is not None:
            function_names = re.findall(r"#### (.*)", functions_search.group(0), flags=re.MULTILINE)
            # Ignore the constructor.
            function_names = [f for f in function_names if f != '\\_\\_init\\_\\_']
            # Create a dictionary where the key is the function name and the value is the docstring.
            abstract_functions: Dict[str, str] = {f: re.search(f"(#### {f}" + "((.|\n)*?))(#|\\Z)",
                                                               functions_search.group(0),
                                                               flags=re.MULTILINE).group(0)
                                                  for f in function_names}
        else:
            abstract_functions: Dict[str, str] = dict()

        # Generate documentation for each child class.
        for child_class_path in child_class_paths:
            if isinstance(child_class_path, str):
                child_class_path = Path(child_class_path)
            # Get the raw text from the child class Python file.
            child_py = child_class_path.read_text(encoding="utf-8")
            # Get all of the final functions. We'll mark them on the doc at the very end of this function.
            final_defs: List[str] = re.findall(r"@final\n\s+def (.*?)\(", child_py, flags=re.MULTILINE)
            # Generate the base document.
            child_doc = self.get_doc(child_class_path)
            child_functions = re.findall("#### (.*)\n", child_doc, flags=re.MULTILINE)

            # Append class variables.
            if len(abstract_class_variables) > 0:
                class_variables_search = re.search(r"## Class Variables\n((.|\n)*?)\*", child_doc)
                # There aren't any new class variables. Create a new section.
                if class_variables_search is None:
                    child_class_variables = "## Class Variables\n\n| Variable | Type | Description |\n" \
                                            "| --- | --- | --- |\n"
                    for acv in abstract_class_variables:
                        child_class_variables += acv + "\n"
                    child_class_variables = child_class_variables.strip()
                    # Add the new section.
                    child_doc = child_doc.replace("***", f"***\n\n{child_class_variables}\n\n***", 1)
                else:
                    rows = "\n".join(abstract_class_variables)
                    child_doc = re.sub(r"(## Class Variables\n\n\| Variable \| Type \| Description \|\n"
                                       r"\| --- \| --- \| --- \|)", r"\1" + "\n" + rows, child_doc,
                                       flags=re.MULTILINE)
            # Append fields.
            if len(abstract_fields) > 0:
                fields_search = re.search(r"## Fields\n((.|\n)*?)## Functions", child_doc)
                # Create a new fields section.
                if fields_search is None:
                    child_fields = "## Fields\n\n" + "\n\n".join(abstract_fields)
                    if "## Class Variables" in child_doc:
                        child_doc = re.sub(r"(\|\n\n\*\*\*\n\n)", r"\1" + child_fields + "\n\n***\n\n",
                                           child_doc, flags=re.S)
                    else:
                        child_doc = re.sub(r"(\*\*\*\n\n)", r"\1" + child_fields + "\n\n***\n\n",
                                           child_doc, flags=re.S)
                # Append existing fields.
                else:
                    child_doc = child_doc.replace("## Fields", "## Fields\n\n" + "\n\n".join(abstract_fields))
            # Append functions.
            if len(abstract_functions) > 0:
                # Add a functions section.
                if "## Functions" not in child_doc:
                    child_doc += "## Functions\n\n"
                for f in abstract_functions:
                    # Replace existing functions.
                    if f"#### {f}" in child_doc:
                        q = abstract_functions[f]
                        if q.endswith("\n\n#"):
                            q = q[:-3]
                        if not q.endswith("\n\n"):
                            q += "\n\n"
                        child_doc = re.sub(f"(#### {f}" + r"((.|\n)*?))(#|\Z)", q, child_doc,
                                           flags=re.MULTILINE)
                    else:
                        q = abstract_functions[f]
                        if q.endswith("\n\n#"):
                            q = q[:-3]
                        if not child_doc.endswith("\n"):
                            child_doc += "\n\n"
                        child_doc += q + "\n\n"
                    child_doc = child_doc.replace(f"### {f}", f"#### {f}")
                    child_doc = child_doc.replace(f"##### {f}", f"#### {f}")

            # Append final markers.
            for final_def in final_defs:
                child_doc = re.sub(f"(#### {final_def})(.*)", r"\1\n\n_(Final)_\2", child_doc,
                                   flags=re.MULTILINE)

            # Fix headers.
            for child_function in child_functions:
                child_doc = re.sub(r"^### " + child_function, f"#### {child_function}", child_doc, flags=re.MULTILINE)
            # Store this document.
            docs[child_class_path.name[:-3]] = child_doc

        # Mark abstract functions.
        for abstract_def in abstract_defs:
            abstract_doc = re.sub(f"(#### {abstract_def})(.*)", r"\1\n\n_(Abstract)_\2", abstract_doc,
                                  flags=re.MULTILINE)
        # Store the abstract document.
        docs[abstract_class_path.name[:-3]] = abstract_doc
        if import_prefix is not None:
            docs = {k: re.sub(r"(`from (.*?)\.)(.*)$", "`" + import_prefix + ".\\3", v, flags=re.MULTILINE)
                    for (k, v) in docs.items()}
        return docs

    @staticmethod
    def get_class_variables(lines: List[str], start_index: int) -> str:
        """
        :param lines: All of the lines of the file.
        :param start_index: Start looking for fields at this line.

        :return: A table of class variables as a string.
        """

        txt = ""
        for i in range(start_index, len(lines)):
            # We assume that all class variables are declared before the constructor.
            if "def __init__" in lines[i]:
                break
            txt += lines[i] + "\n"
        # Parse all lines that have class variable documentation.
        class_var_lines = re.findall(r'""":class_var(((.*)+[\n]+)+?[\s]+)"""\n[\s]+(.*)=', txt, flags=re.MULTILINE)
        if len(class_var_lines) <= 0:
            return ""
        # Create a table.
        class_vars = "| Variable | Type | Description |\n| --- | --- | --- |\n"
        for lines in class_var_lines:
            desc = lines[0].strip()
            var_split = lines[-1].split(":")
            var = var_split[0]
            if len(var_split) > 1:
                var_type = var_split[1].split("=")[0].strip()
            else:
                var_type = ""
            class_vars += f"| `{var}` | {var_type} | {desc} |\n"
        return class_vars.strip()

    @staticmethod
    def get_fields(lines: List[str], start_index: int) -> str:
        """
        Get the field descriptions for this class.

        :param lines: All of the lines of the file.
        :param start_index: Start looking for fields at this line.

        :return: A string of field documentation.
        """

        init_txt = lines[start_index]
        match = re.search(r"def (.*)\):", init_txt, flags=re.MULTILINE)
        count = 1
        while match is None:
            init_txt += lines[start_index + count].strip()
            match = re.search(r"def (.*)\):", init_txt, flags=re.MULTILINE)
            count += 1
        init_func = ""
        for i in range(start_index + count, len(lines)):
            if "def " in lines[i]:
                break
            init_func += lines[i] + "\n"

        fields = ""
        got_fields = True
        while got_fields:
            # Find field tags for each field.
            field_match = re.search(r'""":field(((.*)+[\n]+)+?[\s]+)"""\n[\s]+self\.(.*)', init_func, flags=re.MULTILINE)
            if field_match is not None:
                # Reduce whitespace.
                field_desc = field_match.group(1).strip()
                field_desc = re.sub(r"(\A *\d+\. *|^ {0,8})", r"", field_desc, flags=re.MULTILINE)
                # Get the field name.
                field_name = field_match.group(4).split(":")[0].split("=")[0].strip()

                fields += f"- `{field_name}` " + field_desc + "\n\n"
                init_func = init_func.replace(field_match.group(0), "")
            else:
                got_fields = False
        return fields.strip()

    @staticmethod
    def get_class_description(file_txt: str) -> str:
        """
        Parses a file starting at a line defined by start_index to get the class name and description.
        This assumes that the class has a triple quote description.

        :param file_txt: All of the text of the file.
        """
        
        class_desc = re.search(r'class ([aA-Zz](.*)):\n[\s]+"""\n([\s]+((.*)+[\n]+)+?[\s]+)"""', file_txt,
                               flags=re.MULTILINE).group(3)
        class_desc = re.sub(r"(\A *\d+\. *|^ {0,4})", r"", class_desc, flags=re.MULTILINE)
        # Remove trailing new lines.
        class_desc = class_desc.strip()
        return class_desc

    @staticmethod
    def get_function_documentation(lines: List[str], start_index: int, class_name: str) -> str:
        """
        Create documentation for a function and its parameters.

        :param lines: The lines of the Python script.
        :param start_index: Start at this line to search for function documentation.
        :param class_name: The name of the class. Used for static function documentation.

        :return: The function documentation string.
        """

        began_desc = False
        function = ""

        txt = lines[start_index][:]
        # Get the definition string across multiple lines.
        if "__init__" in lines[start_index]:
            match = re.search(r"def (.*)\):", txt, flags=re.MULTILINE)
            count = 1
            while match is None:
                txt += lines[start_index + count]
                match = re.search(r"def (.*)\):", txt, flags=re.MULTILINE)
                count += 1
            def_str = match.group(1)
            def_str = " ".join(def_str.split()) + ")"
        else:
            match = re.search(r"def (.*) -> (.*):", txt, flags=re.MULTILINE)
            count = 1
            while match is None:
                txt += lines[start_index + count]
                match = re.search(r"def (.*) -> (.*):", txt, flags=re.MULTILINE)
                count += 1
            def_str = match.group(1) + " -> " + match.group(2)
            def_str = " ".join(def_str.split())
        # Used the shortened def string for the header.
        shortened_def_str = def_str.split("(")[0].replace("__", "\\_\\_")

        is_static = lines[start_index - 1].strip() == "@staticmethod"

        parameters: Dict[str, Parameter] = {}
        return_description = ""
        func_desc = ""
        for i in range(start_index + 1, len(lines)):
            line = lines[i].strip()
            if '"""' in line:
                # Found the terminating triple quote.
                if began_desc:
                    break
                # Found the beginning triple quote.
                else:
                    began_desc = True
                    continue
            elif began_desc:
                # Get a parameter.
                if line.startswith(":param"):
                    param_name = line[7:].split(":")[0]
                    param_desc = line.replace(":param " + param_name + ": ", "").strip()
                    parameters[param_name] = Parameter(name=param_name, description=param_desc, def_str=def_str)
                elif line == "":
                    func_desc += "\n"
                # Get the return description
                elif line.startswith(":return:"):
                    return_description = line[8:]
                elif line.startswith(":return"):
                    return_description = line[7:]
                # Get the overview description of the function.
                else:
                    func_desc += line + "\n"

        # Get some example code.
        if is_static:
            call = f"{class_name}.{shortened_def_str}("
        else:
            if shortened_def_str == "\\_\\_init\\_\\_":
                call = f"{class_name.split('(')[0]}("
            else:
                call = f"self.{shortened_def_str}("

        short_call = call[:]
        long_call = call[:]
        for p in parameters:
            long_call += parameters[p].name
            # Add default values to the long call example.
            if parameters[p].default_value != "":
                long_call += f"={parameters[p].default_value}"
            # If there isn't a default value, add the parameter to the short call.
            else:
                short_call += parameters[p].name + ", "
            long_call += ", "
        if short_call.endswith(", "):
            short_call = short_call[:-2]
        if long_call.endswith(", "):
            long_call = long_call[:-2]
        short_call += ")"
        long_call += ")"

        function += f"#### {shortened_def_str}\n\n"
        if short_call == long_call:
            function += f"**`{short_call}`**\n\n"
        else:
            function += f"**`{short_call}`**\n\n**`{long_call}`**\n\n"
        if is_static:
            function += "_This is a static function._\n\n"
        function += func_desc

        if function[-1] == "\n":
            function = function[:-1]
        # Add the paramter table.
        if len(parameters) > 0:
            function += "\n| Parameter | Type | Default | Description |\n| --- | --- | --- | --- |\n"
            for p in parameters:
                parameter = parameters[p]
                function += f"| {parameter.name} | {parameter.param_type} | {parameter.default_value} |" \
                            f" {parameter.description} |\n"
            function += "\n"
        # Remove trailing new lines.
        while function[-1] == "\n":
            function = function[:-1]
        # Add the return value.
        if return_description != "":
            function += "\n\n_Returns:_ " + return_description
        return function

    @staticmethod
    def get_enum_values(lines: List[str], start_index: int) -> str:
        """
        Returns a list of enum values.

        :param lines: The lines in the document.
        :param start_index: The line of the class defintion.
        """

        enum_desc = "| Value | Description |\n| --- | --- |\n"
        began_class_desc = False
        end_class_desc = False
        for i in range(start_index + 1, len(lines)):
            if "class " in lines[i]:
                break
            if lines[i] == "":
                continue
            if '"""' in lines[i]:
                if not began_class_desc:
                    began_class_desc = True
                else:
                    end_class_desc = True
                continue
            if not end_class_desc:
                continue
            line_split = lines[i].strip().split(" = ")
            val = f"`{line_split[0]}`"
            desc_split = lines[i].strip().split("#")
            if len(desc_split) > 1:
                desc = desc_split[1].strip()
            else:
                desc = ""
            enum_desc += f"| {val} | {desc} |\n"
        return enum_desc.strip()

    @staticmethod
    def get_toc(doc: str) -> str:
        """
        :param doc: The document.

        :return: The table of contents of the document.
        """

        toc = "## Overview of API\n\n"
        for header in re.findall(r"^## (.*)", doc, flags=re.MULTILINE):
            toc += f"- [{header}](#{header.lower().replace(' ', '-')})\n"
        toc = toc.strip()

        # Append functions to the table of contents.
        if "## Functions" in doc:
            # Get a table of functions.
            functions = "\n\n| Function | Description |\n| --- | --- |\n"
            for function in re.findall(r"^#### (.*)", doc.split("## Functions")[1], flags=re.MULTILINE):
                # Get the full description of the function.
                desc = re.search(r"^#### " + function + r"(.*)((.|\n)*?)^(\*\*[A-Z].*\.|[A-Z].*\.)", doc,
                                 flags=re.MULTILINE)
                if desc is None:
                    functions += f"| [{function}](#{function}) | |\n"
                else:
                    # Get the first sentence. Exclude sentences that are bolded.
                    desc = re.search(r"(^\*\*(.*?)\*\* |^)(.*?\.)($| [A-Z])", desc.group(4))
                    functions += f"| [{function}](#{function}) | {desc.group(3)} |\n"
            toc += functions
        return toc.strip()

    @staticmethod
    def _get_doc_with_import_prefix(doc: str, import_prefix: str = None) -> str:
        """
        :param doc: The document text.
        :param import_prefix: The import prefix. If None, this function returns `doc` unmodified.

        :return: The document with a custom import prefix.
        """

        if import_prefix is None:
            return doc
        else:
            return re.sub(r"(`from (.*?)\.)(.*)$", "`" + import_prefix + ".\\3", doc, flags=re.MULTILINE)
