"""
* Resolve state references to IDs.
*
* This is part of the bifrost-common suite for module developers.
*
* @module idOfRef
* @author Ralf Mosshammer <bifrost.at@siemens.com>
* @copyright Siemens AG Austria, 2019, 2020
* Python implementation
* @author Manuel Matzinger <manuel.matzinger@siemens.com>
 """

from bifrost_common_py.tokens import tkId
from bifrost_common_py.safepointer import safepointer


"""
* This function will resolve a fully-qualified BIFROST state reference to and ID
* by trying to resolve the reference and accessing the ID field of the resolved
* object. If this fails, it defaults to the last part of state reference.
* 
* @param {object} state The BIFROST state object, including the directory
* @param {string} ref The reference to resolve
* 
* @throws Error if the reference is null, undefined, or empty
"""
def idOfRef(state, ref):
    if (not ref) or (ref == '') or ('/' not in ref):
        raise ValueError('Attempt to resolve empty or invalid reference '+str(ref)+' to ID.')
    sr = ref.split('/')
    defo = sr[len(sr)-1]
    return get(safepointer.get(state, ref, {}), tkId, str(defo))

def get(objectp, path, default = None):
        try:
            return objectp[path]
        except Exception as e:
            print(e)
            return default