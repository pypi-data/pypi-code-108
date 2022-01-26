#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_utilities.py                                                            #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 supporting utilities                                                                  #
#                                                                                                 #
# 3.0.6 26-01-2022: removed list type decorators to remove python version dependancy (>=3.8.4)    
###################################################################################################

"""Supporting utilities"""

def ListItemByName(lst: list, name: str):
    """Retrieves an item from the list based on its name"""
    return next((x for x in lst if x.name == name), None)
