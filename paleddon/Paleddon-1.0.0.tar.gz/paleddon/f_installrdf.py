from .libs import generate_id, data_replace
from .structures import install_rdf as template

class install_rdf(object):
    """docstring for install_rdf"""

    def __init__(self, id, version, name, secure_name, description, creator, contributors, homepage, minVersion, maxVersion):
        super(install_rdf, self).__init__()
        self.template = template
        self.id = id
        self.version = version
        self.name = name
        self.secure_name = secure_name
        self.description = description
        self.creator = creator
        self.contributors = self.__build_contributors__(contributors)

        if not self.contributors:
            self.template = self.template.replace("{contributors}", "")
        else:
            self.template = self.template.replace("{contributors}", self.contributors)

        self.homepage = homepage
        self.minVersion = minVersion
        self.maxVersion = maxVersion

    def __build_contributors__(self, contributors):
        out = []
        tag = "<em:contributor>{0}</em:contributor>"

        output = [tag.format(name) for name in contributors]

        return '\n    '.join(output) # Each contributor in new line, with identation


    def build(self):
        tags = {
            "<em:id></em:id>": f"<em:id>{self.id}</em:id>",
            "<em:version></em:version>": f"<em:version>{self.version}</em:version>",
            "<em:name></em:name>": f"<em:name>{self.name}</em:name>",
            "<em:description></em:description>": f"<em:description>{self.description}</em:description>",
            "<em:creator></em:creator>": f"<em:creator>{self.creator}</em:creator>",
            "<em:homepageURL></em:homepageURL>": f"<em:homepageURL>{self.homepage}</em:homepageURL>",
            "<em:minVersion></em:minVersion>": f"<em:minVersion>{self.creator}</em:minVersion>",
            "<em:maxVersion></em:maxVersion>": f"<em:maxVersion>{self.homepage}</maxVersion:homepageURL>",
            "<em:iconURL>chrome:///skin/": f"<em:iconURL>chrome://{self.secure_name}/skin/"
        }

        self.template = data_replace(tags, self.template)
        return self.template

