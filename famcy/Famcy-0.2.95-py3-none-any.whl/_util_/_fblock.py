# -*- coding: UTF-8 -*-
import abc
import copy
import base64
import random
import Famcy
from Famcy._util_._fwidget import FamcyWidget

class FBlock(FamcyWidget):
    """
    Represents the base class of the fblock 
    function that displays and handles
    submissions. 

    Interface:
        render_inner: render the html content
            for the block
        handle_submission: handle form submit
            action
    """
    def __init__(self):
        # self.value = FBlock.generate_template_content()
        super(FBlock, self).__init__()

    def __getitem__(self, k):
        return self.value.get(k, None)

    def __setitem__(self, k, v):
        self.value[k] = v

    def update(self, updated_dict):
        self.value.update(updated_dict)

    def preload(self):
        """
        This is the preload function
        that should be executed before 
        the inner render function. 
        """
        pass

    def postload(self):
        """
        After the page is rendered, 
        apply async post load function. 
        """
        pass

    # Interface methods
    # ------------------------------------
    @classmethod
    @abc.abstractmethod
    def generate_template_content(cls):
        """
        This is the function that
        returns the template content 
        for the given fblock. 
        - Return a content dictionary - values
        """
        return NotImplemented


class FInputBlock(FBlock):
    """
    This block represents the input
    fblock and possess save/dump feature
    to cookie. 
    
    * Allow:
    mandatory
    action_after_post
    """
    REQUIRED_KEYS = ["action_after_post", "mandatory"]

    def __init__(self):
        super(FInputBlock, self).__init__()
        self.parent_form = self.find_parent(self, 'input_form')

        for k in self.REQUIRED_KEYS:
            assert k in self.value.keys(), k + " is needed for FInputBlock.."


class FUploadBlock(FBlock):
    def __init__(self):
        super(FUploadBlock, self).__init__()
        self.parent_form = self.find_parent(self, 'upload_form')
        self.upload = True
        