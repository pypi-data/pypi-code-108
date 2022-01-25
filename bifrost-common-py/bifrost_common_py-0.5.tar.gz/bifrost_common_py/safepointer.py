"""
* A wrapper around json pointer with default fallbacks.
* 
* This is part of the bifrost-common suite for module developers.
* @module safepointer
* @author Ralf Mosshammer <bifrost.at@siemens.com>
* @copyright Siemens AG Austria, 2019, 2020
* Python implementation
* @author Manuel Matzinger <manuel.matzinger@siemens.com>
"""
class safepointer:
    def has(obj,path):
        return pointerclass.hasp(obj,path)

    def get(obj,path, defn = None):
        if (pointerclass.hasp(obj,path)): # anderes has
            return pointerclass.getp(obj,path)
        return defn

class pointerclass:
    # Converts a json pointer into a array of reference tokens
    def parse(pointer):
        if (pointer == ''):
            return []
        if (pointer[0] != '/'):
            raise Exception('Invalid JSON pointer: ' + pointer)
        # removes first char which should be / and then splits the rest
        return pointer[1:].split("/")

    def getp(obj, pointer):
        if (isinstance(pointer,list)):
            refTokens = pointer
        else:
            refTokens = pointerclass.parse(pointer)
        for i in range(len(refTokens)):
            tok = refTokens[i]
            if not ((type(obj) is dict and tok in obj)):
                raise Exception('Invalid reference token: ' + tok)
            obj = obj[tok]
        return obj

    def hasp(obj, pointer):
        try:
            pointerclass.getp(obj, pointer)
        except Exception as e:
            print(e)
            return False
        return True
