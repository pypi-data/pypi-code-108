import numpy as np
from IPython.display import IFrame
from IPython.core.display import display
import streamlit.components.v1 as components 
import streamlit as st
from streamlit import cli as stcli

# - - - HIDE DEFAULT STREAMLIT - - -
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)




class simplecomponenttwo():
    
     def sliderfunction(slidetitle):
         x = st.slider(slidetitle)
         st.write(x)
                
        
    

   

         
         



 
    
   