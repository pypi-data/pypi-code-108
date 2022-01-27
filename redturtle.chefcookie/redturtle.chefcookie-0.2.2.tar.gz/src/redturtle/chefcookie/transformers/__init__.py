from zope.interface import Interface


class INodePlaceholder(Interface):
    """
    Provide correct placeholder for a node we need to hide due to GDPR
    """

    def transform_anchor(self, anchor):
        """
        @param anchor: the lxml node / anchor we need to transform
        @return: the modified anchor and the reative placeholder
        """
