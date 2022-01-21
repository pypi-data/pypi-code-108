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
 
    def sliderfunction(x,y):
       a = x + y
       print(a)

       
       # x = st.slider(slidetitle)
   # st.markdown(f'`{x}` squared is `{x * x}`')
      #  components.html("<html><body><h1>Test, Slide</h1></body></html>", width=200, height=200)
      #   st.write('component title')

#    def sliderfunction(varOne, varTwo):
#        st.write(varOne)
#        st.write(varTwo)

#if __name__ == '__main__':
 #   sys.argv = ["streamlit", "run", "simplecomponent.py"]
  #  sys.exit(stcli.main()) 