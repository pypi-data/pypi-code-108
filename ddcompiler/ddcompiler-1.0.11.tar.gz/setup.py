# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ddcompiler']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ddcompiler',
    'version': '1.0.11',
    'description': 'Interpreter for evaluating expressions used in AutomationEdge AIStudio dialog designer',
    'long_description': '## ddcompiler\n\nddcompiler is the parser used by AutomationEdge AI Studio dialog designer. In dialog designer, conditions can be used either in an action dialog element or a branch dialog element. A condition is an expression which evaluates either to True or False. ddcompiler has a lexer and a parser which respectively tokenizes and parses the given expression.\n\n### Installation\n\n**pip install ddcompiler** will install the library. It has been tested with Python 3.9.6, but should work with any Python 3.\\* version.\n\n### Basic Usage\n\n```python\nimport ddcompiler as ddc\nvar_dict = {\n    \'conv.lang\': \'fr\',\n}\n\n# Variables used in the expression of the form ${var_name} should be present in the var_dict.\nexpression = \'${conv.lang} == "fr" or ${conv.lang} == "de" and contains("aistudio", "studio")\'\n\n# Instantiate parser and lexer, pass expression to the lexer.\nddparser = ddc.DDParser(ddc.DDLexer(expression))\ntree = ddparser.parse()\n# Prints parse tree\ntree.traverse()\n# Get list of variables used in the expression in form of a set\nprint(f"VARIABLES in the expression: {ddparser.get_variables()}")\n\nprint(f"INPUT: {expression}")\nprint(f"EVALUATION: {tree.evaluate(var_dict)}")\n```\n\n### Expression Language\n\nVisit [AI Studio](https://docs.automationedge.ai/docs/getting-started/manual-configuration/conditions/) documentation to get list of supported constructs.\n\n### More Examples\n\nGo through [parser test file](https://bitbucket.org/yovyom/ddcompiler/src/master/tests/test_parser.py) to see different examples of expressions.\n',
    'author': 'Yogesh Ketkar',
    'author_email': 'yogesh.ketkar@automationedge.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://automationedge.com',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.0,<4.0',
}


setup(**setup_kwargs)
