"""
Middleware that strips whitespace between html tags
copied from David Cramer's blog
http://www.davidcramer.net/code/369/spaceless-html-in-django.html
"""
import re

from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import keep_lazy
from django.utils.encoding import force_text

@keep_lazy(str)
def reduce_spaces_between_tags(value):
    """Returns the given HTML with all spaces between tags removed.
    ,but one. One space is left so that consecutive links and other things
    do not appear glued together
    slight mod of django.utils.html import strip_spaces_between_tags
    """
    return re.sub(r'>\s+<', '> <', force_text(value))

class SpacelessMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        """strips whitespace from all documents
        whose content type is text/html
        """
        if 'Content-Type' in response and 'text/html' in response['Content-Type']:
            response.content = reduce_spaces_between_tags(response.content)
            response['Content-Length'] = str(len(response.content))
        return response
