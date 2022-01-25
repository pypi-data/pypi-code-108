import setuptools
from distutils.core import setup
import sys

long_desc = '''\
stonemark -- a markup language similar to MarkDown
==================================================

A much less forgiving markdown implementation, which is to say: if I can't tell
what the document layout is supposed to be in text format, I don't want the
converter guessing for me.

The basic indentation is four spaces, although lists start at either zero or
two space indentation.  Indented code blocks are not allowed after a list.

Currently supported syntax:

    Element                 StoneMark Syntax

                            ==========
    Heading                 H1 Heading    H2 Heading   H3 Heading
                            ==========    ==========   ----------

    Bold                    **bold text**

    Italic                  *italicized text*

    Bold & Italic           ***bold, italicized text***

    Ordered List            1. First item
                            2. Second item
                            3. Third item

    Unordered List          - First item
                            - Second item
                            - Third item

    Code                    `code`

    Horizontal Rule         --- or ***

    Link         (in-line)  [title](https://www.example.com)

                (separate)  [title]  or [title][id]
                            ...
                            [title | id]: <https://www.example.com>

    Image                       ![alt text](image.jpg)


    Fenced Code Block       ``` or ~~~
                            {
                              "firstName": "John",
                              "lastName": "Smith",
                              "age": 25
                            }
                            ``` or ~~~

    Footnote                Here's a sentence with a footnote. [^1]
    
                            [^1]: This is the footnote.

    Strikethrough           ~~The world is flat.~~

    Underline               __Pay attention.__

    Highlight               I need to highlight these ==very important words==.

    Subscript               H~2~O
    Superscript             X^2^
'''

requirements = ['aenum', 'scription']

py2_only = ()
py3_only = ()
make = []

data = dict(
       name='stonemark',
       version='0.1.2',
       license='BSD License',
       description='a markup language similar to markdown',
       long_description=long_desc,
       long_description_content_type='text/plain',
       packages=['stonemark'],
       package_data={
           'stonemark': [
               'CHANGES',
               'LICENSE',
               ],
           },
       install_requires=requirements,
       author='Ethan Furman',
       author_email='ethan@stoneleaf.us',
       url='https://bitbucket.org/stoneleaf/stonemark',
       entry_points={
           'console_scripts': ['stonemark = stonemark.__main__:Main'],
           },
       classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Topic :: Software Development',
            'Topic :: Text Processing :: Markup',
            'Topic :: Text Processing :: Markup :: Markdown',
            ],
        )

if __name__ == '__main__':
    setup(**data)
