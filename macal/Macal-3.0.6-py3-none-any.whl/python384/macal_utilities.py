#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_utilities.py                                                            #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 supporting utilities                                                                  #
#                                                                                                 #
###################################################################################################

"""Supporting utilities"""

def ListItemByName(lst: list, name: str):
    """Retrieves an item from the list based on its name"""
    return next((x for x in lst if x.name == name), None)
