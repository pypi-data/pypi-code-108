from typing import List, Type, TypeVar

from box import Box
from requests import Response


T = TypeVar('T')


## [space, user, page, blogpost, comment, attachment]


class Foo:
    """Helping class to extract and compare static an class method types using:
    type(__dict__.get(method))"""

    @staticmethod
    def foo_static():
        pass

    @classmethod
    def foo_class(cls):
        pass


StaticMethodType = type(Foo.__dict__.get("foo_static"))
ClassMethodType = type(Foo.__dict__.get("foo_class"))


class NavigableDict(Box):
    """Base Class for Box derived entities.

    See: https://pypi.org/project/python-box/
    """
    @classmethod
    def from_response(cls: Type[T], response: Response) -> T:
        """Returns Type[T] (Box type) from response.

        Args:
            cls (Type[T]): Space, Comment, Blogpost ...
            response (Response): Requests response with json content.

        Returns:
            T: Single Box type, Space, Comment, ...
        """
        obj = cls.__new__(cls)
        obj.__init__(response.json(), default_box=True, default_box_attr=None, box_dots=True)
        return obj

    @classmethod
    def from_results(cls: Type[T], results: dict) -> List[T]:
        """Returns a list ot Type[T] (Box type) element form response.json()

        Args:
            cls (Type[T]): Space, User, Comment ...
            results (dict): reponse.json()

        Returns:
            List[T]: List of Box types elements (Space, Comment ...)
        """
        lst: List[T] = list()
        for result in results:
            obj = cls.__new__(cls)
            obj.__init__(result, default_box=True, default_box_attr=None, box_dots=True)
            lst.append(obj)
        return lst


class Page(NavigableDict):
    """Data class for containing Confluence Page responses with some property utilities for
    .id .version .title ..."""

    ## Explicit properties
    #@property
    #def id(self):
    #    return self.id
    #@property
    #def type(self):
    #    return self.type

    #@property
    #def title(self):
    #    return self.title

    @property
    def body_storage(self):
        return self.body.storage.value

    @property
    def labels(self):
        return [label.name for label in self.metadata.labels.results]

    @property
    def ancestor_ids(self):
        return [ancestor.id for ancestor in self.ancestors]

    @property
    def body_view(self):
        return self.body.export_view.value

    @property
    def parent(self):
        if self.ancestors:
            # return utils.type_wrap(self.ancestors[-1])
            # Direct parent page is always de last ancestor
            return Page(self.ancestors[-1], default_box=True, default_box_attr=None, box_dots=True)
        else:
            return None


class BlogPost(Page):
    pass


class Comment(Page):
    pass


class User(NavigableDict):
    pass


class Attachment(NavigableDict):
    pass


class Space(NavigableDict):

    @property
    def desc(self):
        return self.description.plain.value

    @property
    def labels(self):
        return [result["name"] for result in self.metadata.labels.results]


## Entities list synonims
JSONResponses = List[NavigableDict]
Pages = List[Page]
BlogPosts = List[BlogPost]
Comments = List[Comment]
Spaces = List[Space]
Users = List[User]
