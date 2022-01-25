class CompareUtil(object):

    @staticmethod
    def compareTo(l, r):
        if not l and not r:
            return 0
        elif not l:
            return -1
        elif not r:
            return 1

        l_ln = len(l)
        r_ln = len(r)
        for i in range(l_ln):
            if l[i] > r[i]:
                return 1
            if l[i] < r[i]:
                return -1
        return l_ln - r_ln
