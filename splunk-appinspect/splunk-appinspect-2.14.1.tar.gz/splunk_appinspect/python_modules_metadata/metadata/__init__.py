# to avoid any possible python module clash (relative module clashes with the built-in modules),
# we put everything into the metadata_importer
from splunk_appinspect.python_modules_metadata.metadata_importer import load_metadata

load_metadata()
