""" Indicator depcition
"""
import logging
import six
from six.moves import urllib
from zope.interface import implementer
from zope.component import queryMultiAdapter
from eea.depiction.browser.interfaces import IImageView
from eea.depiction.browser.dexterity import DexterityContainerImageView
logger = logging.getLogger("eea.dexterity.indicators")


def getDataFigureBlock(blocks):
    """ Get block by type
    """
    for uid in blocks:
        block = blocks[uid]
        if block.get('@type') == 'dataFigure':
            if block.get('figureUrl', '') or block.get('url', ''):
                return block

        data = block.get('data', {})
        sub_blocks = data.get('blocks', block.get('blocks', {}))
        if sub_blocks:
            block = getDataFigureBlock(sub_blocks)
            if block:
                return block
    return {}


@implementer(IImageView)
class IndicatorImageView(DexterityContainerImageView):
    """ Custom Image View for IMS Indicator
    """
    _imgview = False

    @property
    def imgview(self):
        """ Img
        """
        if self._imgview is False:
            self._imgview = None
            blocks = getattr(self.context, 'blocks', {})
            if not blocks:
                return self._imgview

            block = getDataFigureBlock(blocks)
            if not block:
                return self._imgview

            figureUrl = block.get('figureUrl', '')
            url = block.get('url', '')
            if not figureUrl:
                if url:
                    if six.PY2 and isinstance(url, six.text_type):
                        url = url.encode('utf-8')
                    url = urllib.parse.unquote(url).split('/')[-1]
                    if url in self.context.keys():
                        obj = self.context[url]
                        self._imgview = queryMultiAdapter(
                            (obj, self.request),
                            name='imgview'
                        )
                return self._imgview

            if six.PY2 and isinstance(figureUrl, six.text_type):
                figureUrl = figureUrl.encode('utf-8')

            figureUrl = urllib.parse.unquote(figureUrl).strip('/')
            try:
                obj = self.context.unrestrictedTraverse(figureUrl)
            except Exception as err:
                logger.exception(err)
                return self._imgview

            chart = None
            if url:
                if 'embed-chart.svg?chart=' in url:
                    chart = url.split('embed-chart.svg?chart=')[-1]
                elif 'embed-chart.png?chart=' in url:
                    chart = url.split('embed-chart.png?chart=')[-1]
            if chart:
                chart = '%s.png' % chart

            imgview = None
            if chart and chart in obj.keys():
                imgview = queryMultiAdapter((
                    obj[chart], self.request), name='imgview')

            if not imgview:
                imgview = queryMultiAdapter(
                    (obj, self.request), name='imgview')

            if imgview:
                self._imgview = imgview

        return self._imgview

    def display(self, scalename='thumb'):
        """ Return a bool if the scale should be displayed
        """
        if not self.imgview:
            return super(IndicatorImageView, self).display(scalename)
        return self.imgview.display(scalename)

    def __call__(self, scalename='thumb'):
        imgview = self.imgview
        if not imgview:
            return super(IndicatorImageView, self).__call__(scalename)
        return imgview(scalename)
