# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jabwrapper', 'jabwrapper.parsers']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.7.6" and sys_platform == "win32" or python_version > "3.7.6" and python_version < "3.8.1" and sys_platform == "win32" or python_version > "3.8.1" and sys_platform == "win32"': ['pywin32>=300,<302']}

setup_kwargs = {
    'name': 'java-access-bridge-wrapper',
    'version': '0.9.1',
    'description': 'Python wrapper for the Windows Java Access Bridge',
    'long_description': '[![Version](https://img.shields.io/pypi/v/java-access-bridge-wrapper.svg?label=version)](https://pypi.org/project/java-access-bridge-wrapper/)\n[![License](https://img.shields.io/pypi/l/java-access-bridge-wrapper.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)\n\n# Introduction\n\nPython wrapper around the Java Access Bridge / Windows Access Bridge.\n\n# Prerequisites\n\n* 64-bit Windows\n* Java >= 8 (https://docs.aws.amazon.com/corretto/latest/corretto-8-ug/downloads-list.html)\n* Python >= 3.7 (https://www.python.org/downloads/release/python-375/)\n\nEnable the Java Access Bridge in windows\n\n    C:\\path\\to\\java\\bin\\jabswitch -enable\n\n# Install\n\n    pip install java-access-bridge-wrapper\n\n# How to use\n\nImport the Java Access Bridge (JAB) wrapper and optionally the context tree\n\n    from JABWrapper.jab_wrapper import JavaAccessBridgeWrapper\n    from JABWrapper.context_tree import ContextNode, ContextTree, SearchElement\n\nThe JAB creates an virtual GUI window when it is opened. For the JAB to operate and receive events from the GUI, the calling code needs to implement the windows\nmessage pump and call it in a loop. The JABWrapper object needs to be in the same thread.\n\nThis can be achieved for example by starting the message pump in a separate thread, where the JAB object is also initialized.\n\n    GetMessage = ctypes.windll.user32.GetMessageW\n    TranslateMessage = ctypes.windll.user32.TranslateMessage\n    DispatchMessage = ctypes.windll.user32.DispatchMessageW\n\n    def pump_background(pipe: queue.Queue):\n        try:\n            jab_wrapper = JavaAccessBridgeWrapper()\n            pipe.put(jab_wrapper)\n            message = byref(wintypes.MSG())\n            while GetMessage(message, 0, 0, 0) > 0:\n                TranslateMessage(message)\n                logging.debug("Dispatching msg={}".format(repr(message)))\n                DispatchMessage(message)\n        except Exception as err:\n            pipe.put(None)\n\n    def main():\n        pipe = queue.Queue()\n            thread = threading.Thread(target=pump_background, daemon=True, args=[pipe])\n            thread.start()\n            jab_wrapper = pipe.get()\n            if not jab_wrapper:\n                raise Exception("Failed to initialize Java Access Bridge Wrapper")\n            time.sleep(0.1) # Wait until the initial messages are parsed, before accessing frames\n\n    if __name__ == "__main__":\n        main()\n\nOnce the JABWrapper object is initialized, attach to some frame and optionally create the context tree to get the element tree of the application.\n\n    jab_wrapper.switch_window_by_title("Frame title")\n    context_tree = ContextTree(jab_wrapper)\n\n# Development\n\n## Development prerequisites\n\n* Install poetry: https://python-poetry.org/docs/\n\n## Test\n\nRun test script against simple Swing application\n\nset environment variable\n\n    set RC_JAVA_ACCESS_BRIDGE_DLL="C:\\path\\to\\Java\\bin\\WindowsAccessBridge-64.dll"\n\nRun test with poetry\n\n    poetry run python tests\\test.py\n\n## Packaging\n\n    poetry build\n    poetry publish\n\n## TODO:\n\n* Support for 32-bit Java Access Bridge version\n* Implement rest of the utility functions to the JABWrapper\n',
    'author': 'Robocorp',
    'author_email': 'support@robocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/robocorp/java-access-bridge-wrapper.git',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
