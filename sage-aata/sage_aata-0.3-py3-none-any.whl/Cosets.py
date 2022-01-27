
def left_coset(H, g):
    H_elements = H.list()
    coset = set(())
    for element in H.list():
        coset.add(element*g)
        
    return sorted(coset)

def right_coset(H, g):
    H_elements  = H.list()
    coset = set(())
    for element in H_elements:
        coset.add(g*element)
        
    return sorted(coset)
 


def coset_generators(H, G):
    cosets  = {}
    for element in G.list():
        
        left_coset = set(())
        right_coset = set(())
        for item in H.list():
            right_coset.add(element*item)
            left_coset.add(item*element)
               
        right_coset = sorted(right_coset)
        left_coset = sorted(left_coset)
        
        
        if str(left_coset) not in cosets.keys() and str(right_coset) not in cosets.keys():
            cosets[str(left_coset)] = [str(element)+"H"]
            cosets[str(right_coset)] = ["H"+str(element)]
        if str(right_coset) in cosets.keys() and str("H"+str(element)) not in cosets[str(right_coset)]:
            cosets[str(right_coset)].append("H"+str(element))
            pass
        if str(left_coset) in cosets.keys() and str(str(element)+"H") not in cosets[str(left_coset)]:
            cosets[str(left_coset)].append(str(element)+"H")
    return cosets


