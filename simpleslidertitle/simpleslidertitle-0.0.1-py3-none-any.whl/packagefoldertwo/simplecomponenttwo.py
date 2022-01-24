import numpy as np
import sys
#sys.path.append('/usr/local/bin/ipython')
#import IPython
#from IPython import IFrame
#import pkg_resources
#pkg_resources.require("ipyhton==7.30.1")
from IPython.display import IFrame
from IPython.core.display import display
import streamlit.components.v1 as components 
import streamlit as st
from streamlit import cli as stcli


class renderslider():
     def sliderfunction(slidetitle):
         x = st.slider(slidetitle)
         st.write(x)
 
    
   