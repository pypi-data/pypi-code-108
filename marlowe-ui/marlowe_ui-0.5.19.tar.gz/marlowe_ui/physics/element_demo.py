import sys
import os

sys.path.insert(0, os.path.join(__file__, '..', '..', '..'))

import marlowe_ui.physics.element as element

if __name__ == '__main__':
    import sys
    for a in sys.argv[1:]:
        elem = None
        if a.lower() in element.table_byname:
            elem = element.table_byname[a]
        elif a in element.table_bysym:
            elem = element.table_bysym[a]
        else:
            try:
                n = int(a)
                if 0 < n < len(element.table_bynum):
                    elem = element.table_bynum[n]
            except:
                pass

        if elem:
            print('----')
            print(elem.name)
            print(elem.sym)
            print(elem.z)
            print(elem.mass)
