import ipywidgets as widgets
import markdown

class MyLabel(widgets.HTML):
    """ Label that allows disabling as well as markdown notation. Use 'myvalue' instead of value """

    def __init__(self,value=""):
        widgets.HTML.__init__(self)
        self._myvalue = value
        self.disabled = False
        self.paint()
        

    def paint(self):
        txt = markdown.markdown(self.myvalue)
        if not self.disabled:
            self.value = f"<p><font color='black'>{txt}</p>"
        else:
            self.value = f"<p><font color='grey'>{txt}</p>"

    @property
    def disabled(self):
        return self._disabled 

    @disabled.setter
    def disabled(self, value):
        self._disabled = value
        self.paint()
            
    @property
    def myvalue(self):
        return self._myvalue 

    @myvalue.setter
    def myvalue(self, value):
        self._myvalue = value
        self.paint()