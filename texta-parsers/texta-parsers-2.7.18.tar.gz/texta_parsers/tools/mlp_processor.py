import logging

from texta_parsers.settings import META_FIELD
from texta_parsers.tools.extension import Extension


logging.basicConfig(
    format='%(levelname)s %(asctime)s: %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.INFO
)


class MLPProcessor:
    """
    A wrapper class to apply MLP to DocParser documents.
    """


    def __init__(self, mlp):
        self.mlp = mlp
        self.IGNORE_FIELDS = ("texta_facts", "properties")


    def apply_mlp(self, generator, analyzers=["all"]):
        """ Applies MLP to objects in a given generator.
        """
        for item in generator:
            # check if email (it returns a tuple because of attachments)
            if isinstance(item, tuple):
                email, attachments = item
                self._apply_mlp_to_mails(email, attachments, analyzers)
            else:
                self._apply_mlp_to_item(item, analyzers)
            yield item


    def _apply_mlp(self, document: dict, field: str, analyzers: list):
        if (field not in document):
            return
        content = document.get(field, "")

        if content:
            mlp_res = self.mlp.process(content, analyzers=analyzers)
            mlp_res_path = field + "_mlp"
            # Add the MLP output dictionary.
            document[mlp_res_path] = mlp_res["text_mlp"]

            facts = []
            for f in mlp_res["texta_facts"]:
                f["doc_path"] = f"{mlp_res_path}.text"
                facts.append(f)

            if facts:
                document["texta_facts"] = facts


    def _apply_mlp_to_mails(self, email: dict, attachments: list, analyzers: list):
        self._apply_mlp(email, "body", analyzers)
        for attachment in attachments:
            self._apply_mlp(attachment, "content", analyzers)


    def _apply_mlp_to_item(self, item: dict, analyzers: list):
        """
        Apply MLP on all items exceptions those that come from a collection file
        as they might have a huge amount of fields that don't necessarily need parsing.
        """
        has_proper_fields = META_FIELD in item and 'extension' in item[META_FIELD]
        if has_proper_fields:
            extension = item[META_FIELD]['extension']
            if extension in Extension.COLLECTION_EXTENSIONS:
                pass
            else:
                item_copy = item.copy()
                for key in item_copy.keys():
                    if key not in self.IGNORE_FIELDS:
                        self._apply_mlp(item, key, analyzers)
