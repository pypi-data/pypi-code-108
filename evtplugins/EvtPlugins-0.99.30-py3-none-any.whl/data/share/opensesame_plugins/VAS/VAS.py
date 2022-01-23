#-*- coding:utf-8 -*-

"""
No rights reserved. All files in this repository are released into the public
domain.
"""

from libopensesame.py3compat import *
from libopensesame.item import item
from libqtopensesame.items.qtautoplugin import qtautoplugin
from openexp.canvas import Canvas, canvas
from libopensesame.oslogging import oslogger

from openexp.keyboard import Keyboard
from openexp.mouse import Mouse
from libopensesame.exceptions import osexception
import os
import sys
import numpy as np


from pyEVT import EvtExchanger


class VAS(item):

    """
    This class (the class with the same name as the module) handles the basic
    functionality of the item. It does not deal with GUI stuff.
    """

    # Provide an informative description for your plug-in.
    description = u'A VAS modifier for a canvas'

    def reset(self):

        """
        desc:
            Resets plug-in to initial values.
        """

        # Here we provide default values for the variables that are specified
        # in info.json. If you do not provide default values, the plug-in will
        # work, but the variables will be undefined when they are not explicitly
        # set in the GUI.
        self.var.VAS_ENCODER_ID                = u"MOUSE"
        self.var.VAS_EXIT_METHOD             = u'MOUSE'
        self.var.VAS_EXIT_KEY                 = u' '
        self.var.VAS_DURATION                = 10000
        self.var.VAS_CANVAS_NAME             = u'VASSCREEN'
        self.var.VAS_BODY_NAME                 = u'VASBODY'
        self.var.VAS_CURSOR_NAME             = u'VASCURSOR'
        self.var.VAS_TIMER_NAME                 = u'VASTIMER'
        self.var.VAS_CURSOR_STARTPOSITION     = 0
        
    def prepare(self):

        """The preparation phase of the plug-in goes here."""
        item.prepare(self)
        self.EE = EvtExchanger()
        Devices = self.EE.Select(self.var.VAS_ENCODER_ID)

        try:
            self.EE.RENC_SetUp(1024, 0, int(1024*(self.var.VAS_CURSOR_STARTPOSITION/100.0)), 1, 1)
            if Devices[0] is None:
                raise

        except:
            self.var.VAS_ENCODER_ID = u"MOUSE"
            oslogger.info("Cannot find encoder input device: Using mouse")

                        
        
        # Checking the excistence of the VAS elements is only possible in the runphase
        # as only then the full canvas is availeable
        
        self.c = Canvas(self.experiment)
        
        self._Keyboard = Keyboard(self.experiment, timeout = 0);
        
        self._Mouse = Mouse(self.experiment)
        my_canvas = self.experiment.items[self.var.VAS_CANVAS_NAME].canvas
        
        try:
            if my_canvas[self.var.VAS_CURSOR_NAME] == None or my_canvas[self.var.VAS_BODY_NAME] == None:
                oslogger.info("Should not occur")
        except Exception as e:
            raise osexception(u"Prepare: READ the VAS manual:\n\rNo VAS elements found on the named canvas")
        
        self.c = self.experiment.items[self.var.VAS_CANVAS_NAME].canvas
        self.c[self.var.VAS_CURSOR_NAME].sx = (self.c[self.var.VAS_BODY_NAME].sx+self.c[self.var.VAS_BODY_NAME].ex) / 2.0
        self.c[self.var.VAS_CURSOR_NAME].ex = self.c[self.var.VAS_CURSOR_NAME].sx
        
        self.VASLENGTH = self.c[self.var.VAS_BODY_NAME].ex - self.c[self.var.VAS_BODY_NAME].sx
        self.SHOWTIMER = False
        if self.var.VAS_EXIT_METHOD == 'TIME':
            if my_canvas[self.var.VAS_CURSOR_NAME] != None:
                self.SHOWTIMER = True
                self.w = self.c[self.var.VAS_TIMER_NAME].ex - self.c[self.var.VAS_TIMER_NAME].sx
                self.h = self.c[self.var.VAS_TIMER_NAME].ey - self.c[self.var.VAS_TIMER_NAME].sy
                self.TIMER_DIR = 'vert'
                self.TIMERSIZE = self.h
                if (abs(self.w) > abs(self.h)): 
                    self.TIMER_DIR = 'horiz'
                    self.TIMERSIZE = self.w
            
        
    def run(self):
        self.set_item_onset(self.c.show())
        st = self.experiment.time()
        val = int(1024*(self.var.VAS_CURSOR_STARTPOSITION/100.0))
        
        while(True):
            if self.var.VAS_EXIT_METHOD == 'TIME': 
                if self.SHOWTIMER:
                    tperc = (self.experiment.time()-st)/self.var.VAS_DURATION
                    if self.TIMER_DIR == 'horiz':
                        self.c[self.var.VAS_TIMER_NAME].ex = self.c[self.var.VAS_TIMER_NAME].sx + ((1-tperc) * self.w)
                    else:
                        self.c[self.var.VAS_TIMER_NAME].ey = self.c[self.var.VAS_TIMER_NAME].sy + ((1-tperc) * self.h)
                        
                if ((self.experiment.time()-st) > self.var.VAS_DURATION):
                    break
            if self.var.VAS_EXIT_METHOD == 'MOUSE':
                button, position, timestamp = self._Mouse.get_click(timeout=2)
                if button is not None:
                    break
            if self.var.VAS_EXIT_METHOD == 'KEY':
                key, time = self._Keyboard.get_key(timeout=5)
                if key is not None:
                    if key == self.var.VAS_EXITKEY:
                        break

            self._Keyboard.flush()
            
            
            if self.var.VAS_ENCODER_ID != u"MOUSE":
                val = self.EE.GetAxis()
            else:
                (val,y), time = self._Mouse.get_pos()
                val = (val + 512) 
            
            if val is not None:
                val = (val)/1024.0
                val = np.clip(val, 0, 1)
                try:
                    self.c["VASVALUE"].text = str(round(val,2))
                except Exception as e:
                    e.Message = ""

                for i in self.c[self.var.VAS_CURSOR_NAME]:
                    i.sx = self.c[self.var.VAS_BODY_NAME].sx + (val*self.VASLENGTH)
                    i.ex = i.sx
            
            self.c.show()
            

        # Add all response related data to the Opensesame responses instance.
        self.experiment.responses.add(response_time=self.experiment.time()-st, \
                                correct=None, \
                                response=str(round(val,2)), \
                                item=self.name)


class qtVAS(VAS, qtautoplugin):

    """
    This class handles the GUI aspect of the plug-in. By using qtautoplugin, we
    usually need to do hardly anything, because the GUI is defined in info.json.
    """

    def __init__(self, name, experiment, script=None):

        """
        Constructor.

        Arguments:
        name        --    The name of the plug-in.
        experiment    --    The experiment object.

        Keyword arguments:
        script        --    A definition script. (default=None)
        """

        # We don't need to do anything here, except call the parent
        # constructors.
        VAS.__init__(self, name, experiment, script)
        qtautoplugin.__init__(self, __file__)

    def c(self):
        self.VAS_TIMERNAME_widget.setEnabled(self.VAS_EXIT_METHOD_widget.currentText() == u'TIME')
        self.VAS_DURATION_widget.setEnabled(self.VAS_EXIT_METHOD_widget.currentText() == u'TIME')
        self.VAS_EXITKEY_widget.setEnabled(self.VAS_EXIT_METHOD_widget.currentText() == u'KEY')
            
    def init_edit_widget(self):

        """
        Constructs the GUI controls. Usually, you can omit this function
        altogether, but if you want to implement more advanced functionality,
        such as controls that are grayed out under certain conditions, you need
        to implement this here.
        """

        # First, call the parent constructor, which constructs the GUI controls
        # based on info.json.
        qtautoplugin.init_edit_widget(self)
        # If you specify a 'name' for a control in info.json, this control will
        # be available self.[name]. The type of the object depends on the
        # control. A checkbox will be a QCheckBox, a line_edit will be a
        # QLineEdit. Here we connect the stateChanged signal of the QCheckBox,
        # to the setEnabled() slot of the QLineEdit. This has the effect of
        # disabling the QLineEdit when the QCheckBox is uncheckhed. We also
        # explictly set the starting state.
        #self.line_edit_widget.setEnabled(self.checkbox_widget.isChecked())
        #self.checkbox_widget.stateChanged.connect(
        #    self.line_edit_widget.setEnabled)
        ELister = EvtExchanger()
        listofdevices = ELister.Attached()
        for i in listofdevices:
            self.VAS_ENCODERID_widget.addItem(i)
        self.VAS_TIMERNAME_widget.setEnabled(self.VAS_EXIT_METHOD_widget.currentText() == u'TIME')
        self.VAS_DURATION_widget.setEnabled(self.VAS_EXIT_METHOD_widget.currentText() == u'TIME')
        self.VAS_EXITKEY_widget.setEnabled(self.VAS_EXIT_METHOD_widget.currentText() == u'KEY')
        self.VAS_EXIT_METHOD_widget.currentTextChanged.connect(self.c)
    
    
