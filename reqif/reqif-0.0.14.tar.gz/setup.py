# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reqif',
 'reqif.cli',
 'reqif.commands',
 'reqif.commands.anonymize',
 'reqif.commands.dump',
 'reqif.commands.format',
 'reqif.commands.passthrough',
 'reqif.commands.validate',
 'reqif.commands.version',
 'reqif.helpers',
 'reqif.models',
 'reqif.parsers',
 'reqif.parsers.spec_types']

package_data = \
{'': ['*'], 'reqif.commands.dump': ['templates/*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0', 'jinja2>=2.11.2,<3.0.0', 'lxml>=4.6.2,<5.0.0']

entry_points = \
{'console_scripts': ['reqif = reqif.cli.main:main']}

setup_kwargs = {
    'name': 'reqif',
    'version': '0.0.14',
    'description': 'Python library for ReqIF format. ReqIF parsing and unparsing.',
    'long_description': '# ReqIF\n\nReqIF is a Python library for working with ReqIF format.\n\n**The project is under construction.**\n\n## Supported features\n\n- Parsing/unparsing ReqIF\n- Formatting (pretty-printing) ReqIF\n\nTo be implemented:\n\n- Validating ReqIF\n- Converting from/to Excel and other formats\n\n## Getting started\n\n```bash\npip install reqif\n```\n\n## Using ReqIF as a library\n\n### Parsing ReqIF\n\n```py\nreqif_bundle = ReqIFParser.parse(input_file_path)\nfor specification in reqif_bundle.core_content.req_if_content.specifications\n    print(specification.long_name)\n\n    for current_hierarchy in reqif_bundle.iterate_specification_hierarchy(specification):\n        print(current_hierarchy)\n```\n\n### Unparsing ReqIF\n\n```py\nreqif_bundle = ReqIFParser.parse(input_file_path)\nreqif_xml_output = ReqIFUnparser.unparse(reqif_bundle)\nwith open(output_file_path, "w", encoding="UTF-8") as output_file:\n    output_file.write(reqif_xml_output)\n```\n\nThe contents of `reqif_xml_output` should be the same as the contents of the \n`input_file`.\n\n## Using ReqIF as a command-line tool\n\n### Passthrough command\n\nBefore using the ReqIF library, it is useful to check if it fully understands a\nparticular ReqIF file format that a user has in hand. The `passthrough` command\nfirst parses the ReqIF XML into in-memory Python objects and then unparses\nthese Python objects back to an output ReqIF file.\n\nIf everything goes fine, the output of the passthrough command should be\nidentical to the contents of the input file.\n\n`tests/integration/examples` contains samples of ReqIF files found on the \ninternet. The integration tests ensure that for these samples, the passthrough\ncommand always produces outputs that are identical to inputs. \n\n### Formatting ReqIF\n\nThe `format` command is similar to `clang-format` for C/C++ files or \n`cmake-format` for CMake files. The input file is parsed and then pretty-printed\nback to an output file.\n\nThis command is useful when dealing with ReqIF files that are hand-written or\nReqIF files produced by the ReqIF tools that do not generate a well-formed XML\nwith consistent indentation.  \n\nThe `tests/integration/commands/format` contains typical examples of\nincorrectly formatted ReqIF files. The integration tests ensure that the\n`format` command fixes these issues.\n\n## Implementation details\n\nThe core of the library is a **ReqIF first-stage parser** that only transforms\nthe contents of a ReqIF XML file into a ReqIF in-memory representation. The\nin-memory representation is a tree of Python objects that map directly to the \nobjects of the ReqIF XML file structure (e.g, Spec Objects, Spec Types, Data\nTypes, Specifications, etc.).\n\n### Parsing: Converting from ReqIF to other formats\n\nThe first-stage parser (implemented by the class `ReqIFParser`) can be used by\nuser\'s second-stage parser/converter scripts that convert the ReqIF in-memory\nstructure into a desired format such as Excel, HTML or other formats. The\ntwo-stage process allows the first stage parsing to focus solely on creating an\nin-memory ReqIF object tree, while the second stage parsing can further parse\nthe ReqIF object tree according to the logical structure of user\'s documents as\nencoded in the ReqIF XML file that was produced by user\'s requirements\nmanagement tool.\n\n### Unparsing: Converting from other formats to ReqIF\n\nThe reverse process is also possible. A user\'s script converts another format\'s\ncontents into a ReqIF in-memory representation. The ReqIF un-parser\n(implemented by the class `ReqIFUnparser`) can be used to render the in-memory\nobjects to the ReqIF XML file.\n\n### Tolerance\n\nThe first-stage parser is made tolerant against possible issues in ReqIF.\nIt should be possible to parse a ReqIF file even if it is missing important\ninformation. A separate validation command shall be used to confirm the validity\nof the ReqIF contents.\n\n### A bottom-up overview of the ReqIF format\n\n- ReqIF is a standard. See reference document [RD01](#rd01-reqif-standard).\n- ReqIF has a fixed structure (see "What is common for all ReqIF documents" \nbelow)\n- ReqIF standard does not define a document structure for every documents so\na ReqIF tool implementor is free to choose between several implementation \napproaches. There is a\n[ReqIF Implementation Guide](#rd02-reqif-implementation-guide)\nthat attempts to harmonize ReqIF tool developments. See also\n"What is left open by the ReqIF standard" below.\n- ReqIF files produced by various tool often have incomplete schemas. \n\n### What is common for all ReqIF documents\n\n- All documents have ReqIF tags:\n  - Document metadata is stored inside tags of `REQ-IF-HEADER` tag.\n  - Requirements are stored as `<SPEC-OBJECT>`s\n  - Requirements types are stored as `<SPEC-TYPE>`s\n  - Supported data types are stored as `<DATATYPE>`\n  - Relationships such as \'Parent-Child\' as stored as `<SPEC-RELATIONS>`\n\n### What is left open by the ReqIF standard\n \n- How to distinguish requirements from headers/sections?\n  - One way: create separate `SPEC-TYPES`: one or more for requirements and\n    one for sections.\n  - Another way: have one spec type but have it provide a `TYPE` field that can\n  be used to distinguish between `REQUIREMENT` or `SECTION`.\n\n## Reference documents\n\n### [RD01] ReqIF standard\n\nThe latest version is 1.2:\n[Requirements Interchange Format](https://www.omg.org/spec/ReqIF)\n\n### [RD02] ReqIF Implementation Guide \n\n[ReqIF Implementation Guide v1.8](https://www.prostep.org/fileadmin/downloads/prostep-ivip_ImplementationGuide_ReqIF_V1-8.pdf)\n',
    'author': 'Stanislav Pankevich',
    'author_email': 's.pankevich@gmail.com',
    'maintainer': 'Stanislav Pankevich',
    'maintainer_email': 's.pankevich@gmail.com',
    'url': 'https://github.com/strictdoc-project/reqif',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
