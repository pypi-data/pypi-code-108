from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name             = 'TracChecklist',
    version          = '0.1.1',
    author           = 'Ralph Ewig',
    author_email     = 'ralph.ewig@sydereal.com',
    description      = "Include checklists in ticket, sourced from wiki pages",
    
    long_description=long_description,
    long_description_content_type="text/markdown",    

    url="https://sydereal.space",
    project_urls={
        "Bug Tracker": "https://sydereal.space",
    },

    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Framework :: Trac',        
    ],

    packages= ['checklist', 'checklist.upgrades'],
    package_data={ 'checklist': [
        'htdocs/*.html', 
        'htdocs/*.css', 
        'htdocs/*.js',
        'htdocs/*.png',
        'htdocs/*.jpg',
        'htdocs/*.svg'        
    ]},
    
    entry_points = {
        'trac.plugins': [
                'checklist.plugin = checklist.plugin',
                'checklist.macros = checklist.macros',                
                ],
    }
)   
