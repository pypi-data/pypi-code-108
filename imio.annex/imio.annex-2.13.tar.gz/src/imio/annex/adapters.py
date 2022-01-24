# -*- coding: utf-8 -*-

from collective.iconifiedcategory.utils import get_category_icon_url
from collective.iconifiedcategory.utils import get_category_object
from imio.prettylink.adapters import PrettyLinkAdapter


class AnnexPrettyLinkAdapter(PrettyLinkAdapter):
    """
    """

    def _leadingIcons(self):
        """
          Manage icons to display before the annex title.
        """
        res = []
        category = get_category_object(self.context, self.context.content_category)
        category_url = get_category_icon_url(category)
        res.append((category_url,
                    category.title))
        return res
