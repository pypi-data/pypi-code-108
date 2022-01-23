from itertools import product 

# Use this label dictionary when site compostion is 
# not considered. Useful for monometallic clusters.
def get_monometallic_cluster_labels():
    return {'ontop|vertex': 1,
            'ontop|edge': 2,
            'ontop|fcc111': 3,
            'ontop|fcc100': 4,
            'bridge|edge': 5,
            'bridge|fcc111': 6,
            'bridge|fcc100': 7,
            'fcc|fcc111': 8,
            'hcp|fcc111': 9,
            '4fold|fcc100': 10,
            '6fold|subsurf': 11}


# Use this label dictionary when site compostion is 
# considered. Useful for bimetallic clusters.
def get_bimetallic_cluster_labels(metals): 
    ma, mb = metals[0], metals[1]

    return {'ontop|vertex|{}'.format(ma): 1, 
            'ontop|vertex|{}'.format(mb): 2,
            'ontop|edge|{}'.format(ma): 3,
            'ontop|edge|{}'.format(mb): 4,
            'ontop|fcc111|{}'.format(ma): 5,
            'ontop|fcc111|{}'.format(mb): 6,
            'ontop|fcc100|{}'.format(ma): 7,
            'ontop|fcc100|{}'.format(mb): 8,
            'bridge|edge|{}{}'.format(ma,ma): 9, 
            'bridge|edge|{}{}'.format(ma,mb): 10,
            'bridge|edge|{}{}'.format(mb,mb): 11,
            'bridge|fcc111|{}{}'.format(ma,ma): 12,
            'bridge|fcc111|{}{}'.format(ma,mb): 13,
            'bridge|fcc111|{}{}'.format(mb,mb): 14,
            'bridge|fcc100|{}{}'.format(ma,ma): 15,
            'bridge|fcc100|{}{}'.format(ma,mb): 16,
            'bridge|fcc100|{}{}'.format(mb,mb): 17,
            'fcc|fcc111|{}{}{}'.format(ma,ma,ma): 18,
            'fcc|fcc111|{}{}{}'.format(ma,ma,mb): 19, 
            'fcc|fcc111|{}{}{}'.format(ma,mb,mb): 20,
            'fcc|fcc111|{}{}{}'.format(mb,mb,mb): 21,
            'hcp|fcc111|{}{}{}'.format(ma,ma,ma): 22,
            'hcp|fcc111|{}{}{}'.format(ma,ma,mb): 23,
            'hcp|fcc111|{}{}{}'.format(ma,mb,mb): 24,
            'hcp|fcc111|{}{}{}'.format(mb,mb,mb): 25,
            '4fold|fcc100|{}{}{}{}'.format(ma,ma,ma,ma): 26,
            '4fold|fcc100|{}{}{}{}'.format(ma,ma,ma,mb): 27, 
            '4fold|fcc100|{}{}{}{}'.format(ma,ma,mb,mb): 28,
            '4fold|fcc100|{}{}{}{}'.format(ma,mb,ma,mb): 29, 
            '4fold|fcc100|{}{}{}{}'.format(ma,mb,mb,mb): 30,
            '4fold|fcc100|{}{}{}{}'.format(mb,mb,mb,mb): 31,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,ma): 32,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,mb): 33,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,ma,ma): 34,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,mb,mb): 35,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,ma): 36,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,mb): 37,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,ma): 38,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,mb): 39,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,ma,ma): 40,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,mb,mb): 41,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,ma): 42,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,mb): 43,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,ma): 44,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,mb): 45,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,ma,ma): 46,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,mb,mb): 47,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,ma): 48,
            '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,mb): 49,
            '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,ma): 50,
            '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,mb): 51,
            '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,ma,ma): 52,
            '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,mb,mb): 53,
            '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,ma): 54,
            '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,mb): 55}


# Use this label dictionary when site compostion is 
# considered. Useful for clusters with arbitrary number
# of components.
def get_multimetallic_cluster_labels(metals): 
    relations = {'ontop': ['vertex','edge','fcc111','fcc100'],
                 'bridge': ['edge','fcc111','fcc100'],
                 'fcc': ['fcc111'],
                 'hcp': ['fcc111'],
                 '4fold': ['fcc100'],
                 '6fold': ['subsurf']}
    d = {}
    count = 0 
    for k, vs in relations.items():
        if k == 'ontop':
            n = 1
        elif k == 'bridge':
            n = 2
        elif k in ['fcc','hcp']:
            n = 3
        elif k == '4fold':
            n = 4
        elif k == '6fold':
            n = 6
        for v in vs:
            for p in product(metals, repeat=n):
                comp = ''.join(p)
                count += 1
                d['{0}|{1}|{2}'.format(k, v, comp)] = count    
                
    return d


# Use this label dictionary when site compostion is 
# not considered. Useful for monometallic slabs.
def get_monometallic_slab_labels(surface): 
    if surface in ['fcc111','hcp0001']:
        return {'ontop|terrace': 1,
                'bridge|terrace': 2,
                'fcc|terrace': 3,
                'hcp|terrace': 4,
                '6fold|subsurf': 5}

    elif surface in ['fcc100','bcc100']:
        return {'ontop|terrace': 1,
                'bridge|terrace': 2,
                '4fold|terrace': 3}

    elif surface in ['fcc110','hcp10m10h']:
        return {'ontop|step': 1,
                'bridge|step': 2, 
                'bridge|sc-tc-h': 3,
                'fcc|sc-tc-h': 4,
                'hcp|sc-tc-h': 5,
                '4fold|terrace': 6,
                '5fold|terrace': 7,
                '6fold|subsurf': 8}

    elif surface == 'fcc211':
        return {'ontop|step': 1,      
                'ontop|terrace': 2,
                'ontop|corner': 3, 
                'bridge|step': 4,
                'bridge|corner': 5,
                'bridge|sc-tc-h': 6,
                'bridge|tc-cc-h': 7,
                'bridge|sc-cc-t': 8,
                'fcc|sc-tc-h': 9,
                'fcc|tc-cc-h': 10,
                'hcp|sc-tc-h': 11,
                'hcp|tc-cc-h': 12,
                '4fold|sc-cc-t': 13,
                '6fold|subsurf': 14}

    elif surface in ['fcc311','fcc331']:
        return {'ontop|step': 1,
                'ontop|terrace': 2,
                'bridge|step': 3,
                'bridge|terrace': 4,
                'bridge|sc-tc-h': 5,
                'bridge|sc-tc-t': 6,
                'fcc|sc-tc-h': 7,
                'hcp|sc-tc-h': 8,
                '4fold|sc-tc-t': 9,
                '6fold|subsurf': 10}

    elif surface == 'fcc322':
        return {'ontop|step': 1,
                'ontop|terrace': 2,
                'ontop|corner': 3,
                'bridge|step': 4,
                'bridge|terrace': 5,
                'bridge|corner': 6,
                'bridge|sc-tc-h': 7,
                'bridge|tc-cc-h': 8,
                'bridge|sc-cc-t': 9,
                'fcc|terrace': 10,
                'fcc|sc-tc-h': 11,
                'fcc|tc-cc-h': 12,
                'hcp|terrace': 13,
                'hcp|sc-tc-h': 14,                    
                'hcp|tc-cc-h': 15,
                '4fold|sc-cc-t': 16,
                '6fold|subsurf': 17}

    elif surface in ['fcc221','fcc332']:
        return {'ontop|step': 1,
                'ontop|terrace': 2,
                'ontop|corner': 3,
                'bridge|step': 4,
                'bridge|terrace': 5,
                'bridge|corner': 6,
                'bridge|sc-tc-h': 7,
                'bridge|tc-cc-h': 8,
                'bridge|sc-cc-h': 9,
                'fcc|terrace': 10,
                'fcc|sc-tc-h': 11,
                'fcc|tc-cc-h': 12,
                'fcc|sc-cc-h': 13,
                'hcp|terrace': 14,
                'hcp|sc-tc-h': 15, 
                'hcp|tc-cc-h': 16,
                'hcp|sc-cc-h': 17,
                '6fold|subsurf': 18}

    elif surface == 'bcc110':
        return {'ontop|terrace': 1,
                'shortbridge|terrace': 2,
                'longbridge|terrace': 3,
                '3fold|terrace': 4}
              
    elif surface == 'bcc111':           
        return {'ontop|step': 1,                       
                'ontop|terrace': 2,        
                'ontop|corner': 3,
                'shortbridge|sc-tc-o': 4,
                'shortbridge|tc-cc-o': 5,
                'longbridge|sc-cc-o': 6,
                '3fold|sc-tc-cc-o': 7}

    elif surface == 'bcc210':
        return {'ontop|step': 1,     
                'ontop|terrace': 2,
                'ontop|corner': 3, 
                'bridge|step': 4,
                'bridge|terrace': 5,
                'bridge|corner': 6,
                'bridge|sc-tc-o': 7,
                'bridge|tc-cc-o': 8,
                'bridge|sc-cc-t': 9,
                '3fold|sc-tc-o': 10,
                '3fold|tc-cc-o': 11,
                '4fold|sc-cc-t': 12}

    elif surface == 'bcc211':
        return {'ontop|step': 1,
                'bridge|step': 2, 
                'bridge|sc-tc-o': 3,
                '3fold|sc-tc-o': 4,
                '4fold|terrace': 5,
                '5fold|terrace': 6}

    elif surface == 'bcc310':
        return {'ontop|step': 1,
                'ontop|terrace': 2,
                'bridge|step': 3,
                'bridge|terrace': 4,
                'bridge|sc-tc-o': 5,
                'bridge|sc-tc-t': 6,
                '3fold|sc-tc-o': 7,
                '4fold|sc-tc-t': 8}

    elif surface == 'hcp10m10t':
        return {'ontop|step': 1,
                'ontop|terrace': 2,
                'bridge|step': 3,
                'bridge|terrace': 4,
                'bridge|sc-tc-t': 5,
                '5fold|subsurf': 6,}

    elif surface == 'hcp10m11':
        return {'ontop|step': 1,
                'ontop|terrace': 2,
                'bridge|step': 3,
                'bridge|terrace': 4,
                'bridge|sc-tc-h': 5,
                'fcc|sc-tc-h': 6,
                'hcp|sc-tc-h': 7,
                '4fold|subsurf': 8,
                '5fold|subsurf': 9,
                '6fold|subsurf': 10}

    elif surface == 'hcp10m12':       
        return {'ontop|step': 1,
                'ontop|terrace': 2,
                'ontop|corner': 3,
                'bridge|step': 4,
                'bridge|terrace': 5,
                'bridge|corner': 6,
                'bridge|sc-tc-h': 7,
                'bridge|tc-cc-t': 8,
                'bridge|sc-cc-h': 9,
                'fcc|sc-tc-h': 10,
                'fcc|sc-cc-h': 11,
                'hcp|sc-tc-h': 12,
                'hcp|sc-cc-h': 13,
                '4fold|tc-cc-t': 14,
                '6fold|subsurf': 15}


# Use this label dictionary when site compostion is 
# considered. Useful for bimetallic slabs.
def get_bimetallic_slab_labels(surface, metals): 
    ma, mb = metals[0], metals[1]

    if surface in ['fcc111','hcp0001']:
        return {'ontop|terrace|{}'.format(ma): 1, 
                'ontop|terrace|{}'.format(mb): 2,
                'bridge|terrace|{}{}'.format(ma,ma): 3, 
                'bridge|terrace|{}{}'.format(ma,mb): 4,
                'bridge|terrace|{}{}'.format(mb,mb): 5, 
                'fcc|terrace|{}{}{}'.format(ma,ma,ma): 6,
                'fcc|terrace|{}{}{}'.format(ma,ma,mb): 7, 
                'fcc|terrace|{}{}{}'.format(ma,mb,mb): 8,
                'fcc|terrace|{}{}{}'.format(mb,mb,mb): 9,
                'hcp|terrace|{}{}{}'.format(ma,ma,ma): 10,
                'hcp|terrace|{}{}{}'.format(ma,ma,mb): 11,
                'hcp|terrace|{}{}{}'.format(ma,mb,mb): 12,
                'hcp|terrace|{}{}{}'.format(mb,mb,mb): 13,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,ma): 14,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,mb): 15,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,ma,ma): 16,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,mb,mb): 17,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,ma): 18,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,mb): 19,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,ma): 20,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,mb): 21,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,ma,ma): 22,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,mb,mb): 23,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,ma): 24,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,mb): 25,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,ma): 26,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,mb): 27,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,ma,ma): 28,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,mb,mb): 29,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,ma): 30,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,mb): 31,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,ma): 32,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,mb): 33,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,ma,ma): 34,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,mb,mb): 35,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,ma): 36,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,mb): 37}

    elif surface in ['fcc100','bcc100']:
        return {'ontop|terrace|{}'.format(ma): 1, 
                'ontop|terrace|{}'.format(mb): 2,
                'bridge|terrace|{}{}'.format(ma,ma): 3, 
                'bridge|terrace|{}{}'.format(ma,mb): 4,
                'bridge|terrace|{}{}'.format(mb,mb): 5, 
                '4fold|terrace|{}{}{}{}'.format(ma,ma,ma,ma): 6,
                '4fold|terrace|{}{}{}{}'.format(ma,ma,ma,mb): 7, 
                '4fold|terrace|{}{}{}{}'.format(ma,ma,mb,mb): 8,
                '4fold|terrace|{}{}{}{}'.format(ma,mb,ma,mb): 9, 
                '4fold|terrace|{}{}{}{}'.format(ma,mb,mb,mb): 10,
                '4fold|terrace|{}{}{}{}'.format(mb,mb,mb,mb): 11}

    elif surface in ['fcc110','hcp10m10h']:
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'bridge|step|{}{}'.format(ma,ma): 3,
                'bridge|step|{}{}'.format(ma,mb): 4,
                'bridge|step|{}{}'.format(mb,mb): 5,
                'bridge|sc-tc-h|{}{}'.format(ma,ma): 6,
                'bridge|sc-tc-h|{}{}'.format(ma,mb): 7,
                'bridge|sc-tc-h|{}{}'.format(mb,mb): 8,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,ma): 9,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,mb): 10, 
                'fcc|sc-tc-h|{}{}{}'.format(ma,mb,mb): 11,
                'fcc|sc-tc-h|{}{}{}'.format(mb,mb,mb): 12,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,ma): 13,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,mb): 14,
                'hcp|sc-tc-h|{}{}{}'.format(ma,mb,mb): 15,
                'hcp|sc-tc-h|{}{}{}'.format(mb,mb,mb): 16,
                '4fold|terrace|{}{}-{}{}'.format(ma,ma,ma,ma): 17,
                '4fold|terrace|{}{}-{}{}'.format(ma,ma,ma,mb): 18,
                '4fold|terrace|{}{}-{}{}'.format(ma,ma,mb,mb): 19,
                '4fold|terrace|{}{}-{}{}'.format(ma,mb,ma,ma): 20,
                '4fold|terrace|{}{}-{}{}'.format(ma,mb,ma,mb): 21,
                '4fold|terrace|{}{}-{}{}'.format(ma,mb,mb,mb): 22,
                '4fold|terrace|{}{}-{}{}'.format(mb,mb,ma,ma): 23,
                '4fold|terrace|{}{}-{}{}'.format(mb,mb,ma,mb): 24,
                '4fold|terrace|{}{}-{}{}'.format(mb,mb,mb,mb): 25,
                # neighbor elements count clockwise from shorter bond ma
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,ma,ma,ma): 26,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,ma,ma,mb): 27,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,ma,mb,mb): 28,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,mb,ma,mb): 29,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,mb,mb,ma): 30,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,mb,mb,mb): 31,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,mb,mb,mb,mb): 32,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,ma,ma,ma): 33,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,ma,ma,mb): 34,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,ma,mb,mb): 35,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,mb,ma,mb): 36,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,mb,mb,ma): 37,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,mb,mb,mb): 38,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,mb,mb,mb,mb): 39,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,ma): 40,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,mb): 41,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,ma,ma): 42,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,mb,mb): 43,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,ma): 44,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,mb): 45,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,ma): 46,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,mb): 47,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,ma,ma): 48,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,mb,mb): 49,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,ma): 50,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,mb): 51,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,ma): 52,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,mb): 53,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,ma,ma): 54,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,mb,mb): 55,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,ma): 56,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,mb): 57,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,ma): 58,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,mb): 59,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,ma,ma): 60,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,mb,mb): 61,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,ma): 62,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,mb): 63}

    elif surface == 'fcc211':
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3,
                'ontop|terrace|{}'.format(mb): 4,
                'ontop|corner|{}'.format(ma): 5,
                'ontop|corner|{}'.format(mb): 6,
                'bridge|step|{}{}'.format(ma,ma): 7, 
                'bridge|step|{}{}'.format(ma,mb): 8,
                'bridge|step|{}{}'.format(mb,mb): 9,
                'bridge|corner|{}{}'.format(ma,ma): 10,
                'bridge|corner|{}{}'.format(ma,mb): 11,
                'bridge|corner|{}{}'.format(mb,mb): 12,
                'bridge|sc-tc-h|{}{}'.format(ma,ma): 13,
                'bridge|sc-tc-h|{}{}'.format(ma,mb): 14,
                'bridge|sc-tc-h|{}{}'.format(mb,mb): 15,
                # terrace bridge is equivalent to tc-cc-h bridge
                'bridge|tc-cc-h|{}{}'.format(ma,ma): 16,
                'bridge|tc-cc-h|{}{}'.format(ma,mb): 17,
                'bridge|tc-cc-h|{}{}'.format(mb,mb): 18,
                'bridge|sc-cc-t|{}{}'.format(ma,ma): 19,
                'bridge|sc-cc-t|{}{}'.format(ma,mb): 20,
                'bridge|sc-cc-t|{}{}'.format(mb,mb): 21,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,ma): 22,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,mb): 23, 
                'fcc|sc-tc-h|{}{}{}'.format(ma,mb,mb): 24,
                'fcc|sc-tc-h|{}{}{}'.format(mb,mb,mb): 25,
                'fcc|tc-cc-h|{}{}{}'.format(ma,ma,ma): 26,
                'fcc|tc-cc-h|{}{}{}'.format(ma,ma,mb): 27,
                'fcc|tc-cc-h|{}{}{}'.format(ma,mb,mb): 28,
                'fcc|tc-cc-h|{}{}{}'.format(mb,mb,mb): 29,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,ma): 30,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,mb): 31,
                'hcp|sc-tc-h|{}{}{}'.format(ma,mb,mb): 32,
                'hcp|sc-tc-h|{}{}{}'.format(mb,mb,mb): 33,
                'hcp|tc-cc-h|{}{}{}'.format(ma,ma,ma): 34,
                'hcp|tc-cc-h|{}{}{}'.format(ma,ma,mb): 35,
                'hcp|tc-cc-h|{}{}{}'.format(ma,mb,mb): 36,
                'hcp|tc-cc-h|{}{}{}'.format(mb,mb,mb): 37,
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,ma,ma,ma): 38,
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,ma,ma,mb): 39, 
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,ma,mb,mb): 40,
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,mb,ma,mb): 41, 
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,mb,mb,mb): 42,
                '4fold|sc-cc-t|{}{}{}{}'.format(mb,mb,mb,mb): 43,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,ma): 44,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,mb): 45,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,ma,ma): 46,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,mb,mb): 47,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,ma): 48,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,mb): 49,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,ma): 50,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,mb): 51,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,ma,ma): 52,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,mb,mb): 53,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,ma): 54,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,mb): 55,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,ma): 56,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,mb): 57,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,ma,ma): 58,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,mb,mb): 59,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,ma): 60,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,mb): 61,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,ma): 62,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,mb): 63,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,ma,ma): 64,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,mb,mb): 65,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,ma): 66,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,mb): 67}
                 
    elif surface in ['fcc311','fcc331']:
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3,
                'ontop|terrace|{}'.format(mb): 4,
                'bridge|step|{}{}'.format(ma,ma): 5,
                'bridge|step|{}{}'.format(ma,mb): 6,
                'bridge|step|{}{}'.format(mb,mb): 7,
                'bridge|terrace|{}{}'.format(ma,ma): 8,
                'bridge|terrace|{}{}'.format(ma,mb): 9,
                'bridge|terrace|{}{}'.format(mb,mb): 10,
                'bridge|sc-tc-h|{}{}'.format(ma,ma): 11,
                'bridge|sc-tc-h|{}{}'.format(ma,mb): 12,
                'bridge|sc-tc-h|{}{}'.format(mb,mb): 13,
                'bridge|sc-tc-t|{}{}'.format(ma,ma): 14,
                'bridge|sc-tc-t|{}{}'.format(ma,mb): 15,
                'bridge|sc-tc-t|{}{}'.format(mb,mb): 16,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,ma): 17,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,mb): 18,
                'fcc|sc-tc-h|{}{}{}'.format(ma,mb,mb): 19,
                'fcc|sc-tc-h|{}{}{}'.format(mb,mb,mb): 20,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,ma): 21,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,mb): 22,
                'hcp|sc-tc-h|{}{}{}'.format(ma,mb,mb): 23,
                'hcp|sc-tc-h|{}{}{}'.format(mb,mb,mb): 24,
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,ma,ma,ma): 25,
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,ma,ma,mb): 26, 
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,ma,mb,mb): 27,
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,mb,ma,mb): 28, 
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,mb,mb,mb): 29,
                '4fold|sc-tc-t|{}{}{}{}'.format(mb,mb,mb,mb): 30,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,ma): 31,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,mb): 32,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,ma,ma): 33,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,mb,mb): 34,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,ma): 35,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,mb): 36,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,ma): 37,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,mb): 38,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,ma,ma): 39,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,mb,mb): 40,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,ma): 41,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,mb): 42,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,ma): 43,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,mb): 44,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,ma,ma): 45,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,mb,mb): 46,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,ma): 47,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,mb): 48,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,ma): 49,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,mb): 50,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,ma,ma): 51,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,mb,mb): 52,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,ma): 53,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,mb): 54}

    elif surface == 'fcc322':                                                      
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3,
                'ontop|terrace|{}'.format(mb): 4,
                'ontop|corner|{}'.format(ma): 5,
                'ontop|corner|{}'.format(mb): 6,
                'bridge|step|{}{}'.format(ma,ma): 7, 
                'bridge|step|{}{}'.format(ma,mb): 8,
                'bridge|step|{}{}'.format(mb,mb): 9,
                'bridge|terrace|{}{}'.format(ma,ma): 10,
                'bridge|terrace|{}{}'.format(ma,mb): 11,
                'bridge|terrace|{}{}'.format(mb,mb): 12,
                'bridge|corner|{}{}'.format(ma,ma): 13,
                'bridge|corner|{}{}'.format(ma,mb): 14,
                'bridge|corner|{}{}'.format(mb,mb): 15,
                'bridge|sc-tc-h|{}{}'.format(ma,ma): 16,
                'bridge|sc-tc-h|{}{}'.format(ma,mb): 17,
                'bridge|sc-tc-h|{}{}'.format(mb,mb): 18,                    
                'bridge|tc-cc-h|{}{}'.format(ma,ma): 19,
                'bridge|tc-cc-h|{}{}'.format(ma,mb): 20,
                'bridge|tc-cc-h|{}{}'.format(mb,mb): 21,
                'bridge|sc-cc-t|{}{}'.format(ma,ma): 22,
                'bridge|sc-cc-t|{}{}'.format(ma,mb): 23,
                'bridge|sc-cc-t|{}{}'.format(mb,mb): 24,
                'fcc|terrace|{}{}{}'.format(ma,ma,ma): 25,
                'fcc|terrace|{}{}{}'.format(ma,ma,mb): 26,
                'fcc|terrace|{}{}{}'.format(ma,mb,mb): 27,
                'fcc|terrace|{}{}{}'.format(mb,mb,mb): 28,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,ma): 29,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,mb): 30, 
                'fcc|sc-tc-h|{}{}{}'.format(ma,mb,mb): 31,
                'fcc|sc-tc-h|{}{}{}'.format(mb,mb,mb): 32,
                'fcc|tc-cc-h|{}{}{}'.format(ma,ma,ma): 33,
                'fcc|tc-cc-h|{}{}{}'.format(ma,ma,mb): 34,
                'fcc|tc-cc-h|{}{}{}'.format(ma,mb,mb): 35,
                'fcc|tc-cc-h|{}{}{}'.format(mb,mb,mb): 36,
                'hcp|terrace|{}{}{}'.format(ma,ma,ma): 37,
                'hcp|terrace|{}{}{}'.format(ma,ma,mb): 38,
                'hcp|terrace|{}{}{}'.format(ma,mb,mb): 39,
                'hcp|terrace|{}{}{}'.format(mb,mb,mb): 40,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,ma): 41,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,mb): 42,
                'hcp|sc-tc-h|{}{}{}'.format(ma,mb,mb): 43,
                'hcp|sc-tc-h|{}{}{}'.format(mb,mb,mb): 44,
                'hcp|tc-cc-h|{}{}{}'.format(ma,ma,ma): 45,
                'hcp|tc-cc-h|{}{}{}'.format(ma,ma,mb): 46,
                'hcp|tc-cc-h|{}{}{}'.format(ma,mb,mb): 47,
                'hcp|tc-cc-h|{}{}{}'.format(mb,mb,mb): 48,
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,ma,ma,ma): 49,
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,ma,ma,mb): 50, 
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,ma,mb,mb): 51,
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,mb,ma,mb): 52, 
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,mb,mb,mb): 53,
                '4fold|sc-cc-t|{}{}{}{}'.format(mb,mb,mb,mb): 54,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,ma): 55,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,mb): 56,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,ma,ma): 57,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,mb,mb): 58,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,ma): 59,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,mb): 60,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,ma): 61,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,mb): 62,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,ma,ma): 63,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,mb,mb): 64,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,ma): 65,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,mb): 66,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,ma): 67,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,mb): 68,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,ma,ma): 69,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,mb,mb): 70,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,ma): 71,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,mb): 72,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,ma): 73,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,mb): 74,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,ma,ma): 75,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,mb,mb): 76,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,ma): 77,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,mb): 78}

    elif surface in ['fcc221','fcc332']:                                          
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3,
                'ontop|terrace|{}'.format(mb): 4,
                'ontop|corner|{}'.format(ma): 5,
                'ontop|corner|{}'.format(mb): 6,
                'bridge|step|{}{}'.format(ma,ma): 7, 
                'bridge|step|{}{}'.format(ma,mb): 8,
                'bridge|step|{}{}'.format(mb,mb): 9,
                'bridge|terrace|{}{}'.format(ma,ma): 10,
                'bridge|terrace|{}{}'.format(ma,mb): 11,
                'bridge|terrace|{}{}'.format(mb,mb): 12,
                'bridge|corner|{}{}'.format(ma,ma): 13,
                'bridge|corner|{}{}'.format(ma,mb): 14,
                'bridge|corner|{}{}'.format(mb,mb): 15,
                'bridge|sc-tc-h|{}{}'.format(ma,ma): 16,
                'bridge|sc-tc-h|{}{}'.format(ma,mb): 17,
                'bridge|sc-tc-h|{}{}'.format(mb,mb): 18, 
                'bridge|tc-cc-h|{}{}'.format(ma,ma): 19,
                'bridge|tc-cc-h|{}{}'.format(ma,mb): 20,
                'bridge|tc-cc-h|{}{}'.format(mb,mb): 21,
                'bridge|sc-cc-h|{}{}'.format(ma,ma): 22,
                'bridge|sc-cc-h|{}{}'.format(ma,mb): 23,
                'bridge|sc-cc-h|{}{}'.format(mb,mb): 24,
                'fcc|terrace|{}{}{}'.format(ma,ma,ma): 25,
                'fcc|terrace|{}{}{}'.format(ma,ma,mb): 26,
                'fcc|terrace|{}{}{}'.format(ma,mb,mb): 27,
                'fcc|terrace|{}{}{}'.format(mb,mb,mb): 28,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,ma): 29,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,mb): 30, 
                'fcc|sc-tc-h|{}{}{}'.format(ma,mb,mb): 31,
                'fcc|sc-tc-h|{}{}{}'.format(mb,mb,mb): 32,
                'fcc|tc-cc-h|{}{}{}'.format(ma,ma,ma): 33,
                'fcc|tc-cc-h|{}{}{}'.format(ma,ma,mb): 34,
                'fcc|tc-cc-h|{}{}{}'.format(ma,mb,mb): 35,
                'fcc|tc-cc-h|{}{}{}'.format(mb,mb,mb): 36,
                'fcc|sc-cc-h|{}{}{}'.format(ma,ma,ma): 37,
                'fcc|sc-cc-h|{}{}{}'.format(ma,ma,mb): 38,
                'fcc|sc-cc-h|{}{}{}'.format(ma,mb,mb): 39,
                'fcc|sc-cc-h|{}{}{}'.format(mb,mb,mb): 40,
                'hcp|terrace|{}{}{}'.format(ma,ma,ma): 41,
                'hcp|terrace|{}{}{}'.format(ma,ma,mb): 42,
                'hcp|terrace|{}{}{}'.format(ma,mb,mb): 43,
                'hcp|terrace|{}{}{}'.format(mb,mb,mb): 44,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,ma): 45,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,mb): 46,
                'hcp|sc-tc-h|{}{}{}'.format(ma,mb,mb): 47,
                'hcp|sc-tc-h|{}{}{}'.format(mb,mb,mb): 48,
                'hcp|tc-cc-h|{}{}{}'.format(ma,ma,ma): 49,
                'hcp|tc-cc-h|{}{}{}'.format(ma,ma,mb): 50,
                'hcp|tc-cc-h|{}{}{}'.format(ma,mb,mb): 51,
                'hcp|tc-cc-h|{}{}{}'.format(mb,mb,mb): 52,
                'hcp|sc-cc-h|{}{}{}'.format(ma,ma,ma): 53,
                'hcp|sc-cc-h|{}{}{}'.format(ma,ma,mb): 54,
                'hcp|sc-cc-h|{}{}{}'.format(ma,mb,mb): 55,
                'hcp|sc-cc-h|{}{}{}'.format(mb,mb,mb): 56,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,ma): 57,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,mb): 58,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,ma,ma): 59,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,mb,mb): 60,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,ma): 61,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,mb): 62,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,ma): 63,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,mb): 64,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,ma,ma): 65,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,mb,mb): 66,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,ma): 67,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,mb): 68,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,ma): 69,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,mb): 70,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,ma,ma): 71,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,mb,mb): 72,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,ma): 73,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,mb): 74,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,ma): 75,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,mb): 76,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,ma,ma): 77,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,mb,mb): 78,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,ma): 79,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,mb): 80}

    elif surface == 'bcc110':
        return {'ontop|terrace|{}'.format(ma): 1, 
                'ontop|terrace|{}'.format(mb): 2,
                'shortbridge|terrace|{}{}'.format(ma,ma): 3,
                'shortbridge|terrace|{}{}'.format(ma,mb): 4,
                'shortbridge|terrace|{}{}'.format(mb,mb): 5,
                'longbridge|terrace|{}{}'.format(ma,ma): 6, 
                'longbridge|terrace|{}{}'.format(ma,mb): 7,
                'longbridge|terrace|{}{}'.format(mb,mb): 8, 
                '3fold|terrace|{}{}{}'.format(ma,ma,ma): 9,
                '3fold|terrace|{}{}{}'.format(ma,ma,mb): 10, 
                '3fold|terrace|{}{}{}'.format(ma,mb,mb): 11,
                '3fold|terrace|{}{}{}'.format(mb,mb,mb): 12}

    elif surface == 'bcc111':                         
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3,
                'ontop|terrace|{}'.format(mb): 4,
                'ontop|corner|{}'.format(ma): 5,
                'ontop|corner|{}'.format(mb): 6,
                'shortbridge|sc-tc-o|{}{}'.format(ma,ma): 7, 
                'shortbridge|sc-tc-o|{}{}'.format(ma,mb): 8,
                'shortbridge|sc-tc-o|{}{}'.format(mb,mb): 9,
                'shortbridge|tc-cc-o|{}{}'.format(ma,ma): 10,
                'shortbridge|tc-cc-o|{}{}'.format(ma,mb): 11,
                'shortbridge|tc-cc-o|{}{}'.format(mb,mb): 12,
                'longbridge|sc-cc-o|{}{}'.format(ma,ma): 13,
                'longbridge|sc-cc-o|{}{}'.format(ma,mb): 14,
                'longbridge|sc-cc-o|{}{}'.format(mb,mb): 15,
                '3fold|sc-tc-cc-o|{}{}{}'.format(ma,ma,ma): 16,
                '3fold|sc-tc-cc-o|{}{}{}'.format(ma,ma,mb): 17, 
                '3fold|sc-tc-cc-o|{}{}{}'.format(ma,mb,mb): 18,
                '3fold|sc-tc-cc-o|{}{}{}'.format(mb,mb,mb): 19}

    elif surface == 'bcc210':
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3,
                'ontop|terrace|{}'.format(mb): 4,
                'ontop|corner|{}'.format(ma): 5,
                'ontop|corner|{}'.format(mb): 6,
                'bridge|step|{}{}'.format(ma,ma): 7, 
                'bridge|step|{}{}'.format(ma,mb): 8,
                'bridge|step|{}{}'.format(mb,mb): 9,
                'bridge|terrace|{}{}'.format(ma,ma): 10,
                'bridge|terrace|{}{}'.format(ma,mb): 11,
                'bridge|terrace|{}{}'.format(mb,mb): 12,
                'bridge|corner|{}{}'.format(ma,ma): 13,
                'bridge|corner|{}{}'.format(ma,mb): 14,
                'bridge|corner|{}{}'.format(mb,mb): 15,
                'bridge|sc-tc-o|{}{}'.format(ma,ma): 16,
                'bridge|sc-tc-o|{}{}'.format(ma,mb): 17,
                'bridge|sc-tc-o|{}{}'.format(mb,mb): 18,
                'bridge|tc-cc-o|{}{}'.format(ma,ma): 19,
                'bridge|tc-cc-o|{}{}'.format(ma,mb): 20,
                'bridge|tc-cc-o|{}{}'.format(mb,mb): 21,
                'bridge|sc-cc-t|{}{}'.format(ma,ma): 22,
                'bridge|sc-cc-t|{}{}'.format(ma,mb): 23,
                'bridge|sc-cc-t|{}{}'.format(mb,mb): 24,
                '3fold|sc-tc-o|{}{}{}'.format(ma,ma,ma): 25,
                '3fold|sc-tc-o|{}{}{}'.format(ma,ma,mb): 26, 
                '3fold|sc-tc-o|{}{}{}'.format(ma,mb,mb): 27,
                '3fold|sc-tc-o|{}{}{}'.format(mb,mb,mb): 28,
                '3fold|tc-cc-o|{}{}{}'.format(ma,ma,ma): 29,
                '3fold|tc-cc-o|{}{}{}'.format(ma,ma,mb): 30,
                '3fold|tc-cc-o|{}{}{}'.format(ma,mb,mb): 31,
                '3fold|tc-cc-o|{}{}{}'.format(mb,mb,mb): 32,
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,ma,ma,ma): 33,
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,ma,ma,mb): 34, 
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,ma,mb,mb): 35,
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,mb,ma,mb): 36, 
                '4fold|sc-cc-t|{}{}{}{}'.format(ma,mb,mb,mb): 37,
                '4fold|sc-cc-t|{}{}{}{}'.format(mb,mb,mb,mb): 38}

    elif surface == 'bcc211':
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'bridge|step|{}{}'.format(ma,ma): 3,
                'bridge|step|{}{}'.format(ma,mb): 4,
                'bridge|step|{}{}'.format(mb,mb): 5,
                'bridge|sc-tc-o|{}{}'.format(ma,ma): 6,
                'bridge|sc-tc-o|{}{}'.format(ma,mb): 7,
                'bridge|sc-tc-o|{}{}'.format(mb,mb): 8,
                '3fold|sc-tc-o|{}{}{}'.format(ma,ma,ma): 9,
                '3fold|sc-tc-o|{}{}{}'.format(ma,ma,mb): 10, 
                '3fold|sc-tc-o|{}{}{}'.format(ma,mb,mb): 11,
                '3fold|sc-tc-o|{}{}{}'.format(mb,mb,mb): 12,
                '4fold|terrace|{}{}-{}{}'.format(ma,ma,ma,ma): 13,
                '4fold|terrace|{}{}-{}{}'.format(ma,ma,ma,mb): 14,
                '4fold|terrace|{}{}-{}{}'.format(ma,ma,mb,mb): 15,
                '4fold|terrace|{}{}-{}{}'.format(ma,mb,ma,ma): 16,
                '4fold|terrace|{}{}-{}{}'.format(ma,mb,ma,mb): 17,
                '4fold|terrace|{}{}-{}{}'.format(ma,mb,mb,mb): 18,
                '4fold|terrace|{}{}-{}{}'.format(mb,mb,ma,ma): 19,
                '4fold|terrace|{}{}-{}{}'.format(mb,mb,ma,mb): 20,
                '4fold|terrace|{}{}-{}{}'.format(mb,mb,mb,mb): 21,
                # neighbor elements count clockwise from shorter bond ma
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,ma,ma,ma): 22,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,ma,ma,mb): 23,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,ma,mb,mb): 24,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,mb,ma,mb): 25,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,mb,mb,ma): 26,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,ma,mb,mb,mb): 27,
                '5fold|terrace|{}-{}{}{}{}'.format(ma,mb,mb,mb,mb): 28,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,ma,ma,ma): 29,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,ma,ma,mb): 30,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,ma,mb,mb): 31,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,mb,ma,mb): 32,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,mb,mb,ma): 33,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,ma,mb,mb,mb): 34,
                '5fold|terrace|{}-{}{}{}{}'.format(mb,mb,mb,mb,mb): 35}

    elif surface == 'bcc310':
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3,
                'ontop|terrace|{}'.format(mb): 4,
                'bridge|step|{}{}'.format(ma,ma): 5,
                'bridge|step|{}{}'.format(ma,mb): 6,
                'bridge|step|{}{}'.format(mb,mb): 7,
                'bridge|terrace|{}{}'.format(ma,ma): 8,
                'bridge|terrace|{}{}'.format(ma,mb): 9,
                'bridge|terrace|{}{}'.format(mb,mb): 10,
                'bridge|sc-tc-o|{}{}'.format(ma,ma): 11,
                'bridge|sc-tc-o|{}{}'.format(ma,mb): 12,
                'bridge|sc-tc-o|{}{}'.format(mb,mb): 13,
                'bridge|sc-tc-t|{}{}'.format(ma,ma): 14,
                'bridge|sc-tc-t|{}{}'.format(ma,mb): 15,
                'bridge|sc-tc-t|{}{}'.format(mb,mb): 16,
                '3fold|sc-tc-o|{}{}{}'.format(ma,ma,ma): 17,
                '3fold|sc-tc-o|{}{}{}'.format(ma,ma,mb): 18,
                '3fold|sc-tc-o|{}{}{}'.format(ma,mb,mb): 19,
                '3fold|sc-tc-o|{}{}{}'.format(mb,mb,mb): 20,                    
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,ma,ma,ma): 21,
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,ma,ma,mb): 22, 
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,ma,mb,mb): 23,
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,mb,ma,mb): 24, 
                '4fold|sc-tc-t|{}{}{}{}'.format(ma,mb,mb,mb): 25,
                '4fold|sc-tc-t|{}{}{}{}'.format(mb,mb,mb,mb): 26}

    elif surface == 'hcp10m10t':
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3,
                'ontop|terrace|{}'.format(mb): 4,                     
                'bridge|step|{}{}'.format(ma,ma): 5,    
                'bridge|step|{}{}'.format(ma,mb): 6,
                'bridge|step|{}{}'.format(mb,mb): 7,
                'bridge|terrace|{}{}'.format(ma,ma): 8,
                'bridge|terrace|{}{}'.format(ma,mb): 9,
                'bridge|terrace|{}{}'.format(mb,mb): 10,
                'bridge|sc-tc-t|{}{}'.format(ma,ma): 11,
                'bridge|sc-tc-t|{}{}'.format(ma,mb): 12,
                'bridge|sc-tc-t|{}{}'.format(mb,mb): 13,
                # neighbor elements count clockwise from shorter bond ma
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,ma,ma,ma): 14,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,ma,ma,mb): 15,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,ma,mb,mb): 16,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,mb,ma,mb): 17,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,mb,mb,ma): 18, 
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,mb,mb,mb): 19,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,mb,mb,mb,mb): 20,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,ma,ma,ma): 21,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,ma,ma,mb): 22,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,ma,mb,mb): 23,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,mb,ma,mb): 24,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,mb,mb,ma): 25,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,mb,mb,mb): 26,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,mb,mb,mb,mb): 27}

    elif surface == 'hcp10m11':
        return {'ontop|step|{}'.format(ma): 1, 
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3, 
                'ontop|terrace|{}'.format(mb): 4,                    
                'bridge|step|{}{}'.format(ma,ma): 5, 
                'bridge|step|{}{}'.format(ma,mb): 6,
                'bridge|step|{}{}'.format(mb,mb): 7, 
                'bridge|terrace|{}{}'.format(ma,ma): 8, 
                'bridge|terrace|{}{}'.format(ma,mb): 9,
                'bridge|terrace|{}{}'.format(mb,mb): 10, 
                'bridge|sc-tc-h|{}{}'.format(ma,ma): 11, 
                'bridge|sc-tc-h|{}{}'.format(ma,mb): 12,
                'bridge|sc-tc-h|{}{}'.format(mb,mb): 13, 
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,ma): 14,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,mb): 15, 
                'fcc|sc-tc-h|{}{}{}'.format(ma,mb,mb): 16,
                'fcc|sc-tc-h|{}{}{}'.format(mb,mb,mb): 17,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,ma): 18,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,mb): 19, 
                'hcp|sc-tc-h|{}{}{}'.format(ma,mb,mb): 20,
                'hcp|sc-tc-h|{}{}{}'.format(mb,mb,mb): 21,
                '4fold|subsurf|{}{}-{}{}'.format(ma,ma,ma,ma): 22,
                '4fold|subsurf|{}{}-{}{}'.format(ma,ma,ma,mb): 23,
                '4fold|subsurf|{}{}-{}{}'.format(ma,ma,mb,mb): 24,
                '4fold|subsurf|{}{}-{}{}'.format(ma,mb,ma,ma): 25,
                '4fold|subsurf|{}{}-{}{}'.format(ma,mb,ma,mb): 26,
                '4fold|subsurf|{}{}-{}{}'.format(ma,mb,mb,mb): 27,
                '4fold|subsurf|{}{}-{}{}'.format(mb,mb,ma,ma): 28,
                '4fold|subsurf|{}{}-{}{}'.format(mb,mb,ma,mb): 29,
                '4fold|subsurf|{}{}-{}{}'.format(mb,mb,mb,mb): 30,
                # neighbor elements count clockwise from shorter bond ma
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,ma,ma,ma): 31,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,ma,ma,mb): 32,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,ma,mb,mb): 33,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,mb,ma,mb): 34,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,mb,mb,ma): 35, 
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,ma,mb,mb,mb): 36,
                '5fold|subsurf|{}-{}{}{}{}'.format(ma,mb,mb,mb,mb): 37,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,ma,ma,ma): 38,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,ma,ma,mb): 39,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,ma,mb,mb): 40,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,mb,ma,mb): 41,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,mb,mb,ma): 42,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,ma,mb,mb,mb): 43,
                '5fold|subsurf|{}-{}{}{}{}'.format(mb,mb,mb,mb,mb): 44,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,ma): 45,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,mb): 46,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,ma,ma): 47,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,mb,mb): 48,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,ma): 49,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,mb): 50,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,ma): 51,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,mb): 52,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,ma,ma): 53,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,mb,mb): 54,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,ma): 55,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,mb): 56,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,ma): 57,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,mb): 58,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,ma,ma): 59,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,mb,mb): 60,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,ma): 61,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,mb): 62,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,ma): 63,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,mb): 64,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,ma,ma): 65,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,mb,mb): 66,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,ma): 67,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,mb): 68}

    elif surface == 'hcp10m12':
        return {'ontop|step|{}'.format(ma): 1,
                'ontop|step|{}'.format(mb): 2,
                'ontop|terrace|{}'.format(ma): 3,
                'ontop|terrace|{}'.format(mb): 4,
                'ontop|corner|{}'.format(ma): 5,
                'ontop|corner|{}'.format(mb): 6,
                'bridge|step|{}{}'.format(ma,ma): 7, 
                'bridge|step|{}{}'.format(ma,mb): 8,
                'bridge|step|{}{}'.format(mb,mb): 9,
                'bridge|terrace|{}{}'.format(ma,ma): 10,
                'bridge|terrace|{}{}'.format(ma,mb): 11,
                'bridge|terrace|{}{}'.format(mb,mb): 12,
                'bridge|corner|{}{}'.format(ma,ma): 13,
                'bridge|corner|{}{}'.format(ma,mb): 14,
                'bridge|corner|{}{}'.format(mb,mb): 15,
                'bridge|sc-tc-h|{}{}'.format(ma,ma): 16,
                'bridge|sc-tc-h|{}{}'.format(ma,mb): 17,
                'bridge|sc-tc-h|{}{}'.format(mb,mb): 18,
                'bridge|tc-cc-t|{}{}'.format(ma,ma): 19,
                'bridge|tc-cc-t|{}{}'.format(ma,mb): 20,
                'bridge|tc-cc-t|{}{}'.format(mb,mb): 21,
                'bridge|sc-cc-h|{}{}'.format(ma,ma): 22,
                'bridge|sc-cc-h|{}{}'.format(ma,mb): 23,
                'bridge|sc-cc-h|{}{}'.format(mb,mb): 24,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,ma): 25,
                'fcc|sc-tc-h|{}{}{}'.format(ma,ma,mb): 26, 
                'fcc|sc-tc-h|{}{}{}'.format(ma,mb,mb): 27,
                'fcc|sc-tc-h|{}{}{}'.format(mb,mb,mb): 28,
                'fcc|sc-cc-h|{}{}{}'.format(ma,ma,ma): 29,
                'fcc|sc-cc-h|{}{}{}'.format(ma,ma,mb): 30,
                'fcc|sc-cc-h|{}{}{}'.format(ma,mb,mb): 31,
                'fcc|sc-cc-h|{}{}{}'.format(mb,mb,mb): 32,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,ma): 33,
                'hcp|sc-tc-h|{}{}{}'.format(ma,ma,mb): 34,
                'hcp|sc-tc-h|{}{}{}'.format(ma,mb,mb): 35,
                'hcp|sc-tc-h|{}{}{}'.format(mb,mb,mb): 36,
                'hcp|sc-cc-h|{}{}{}'.format(ma,ma,ma): 37,
                'hcp|sc-cc-h|{}{}{}'.format(ma,ma,mb): 38,
                'hcp|sc-cc-h|{}{}{}'.format(ma,mb,mb): 39,
                'hcp|sc-cc-h|{}{}{}'.format(mb,mb,mb): 40,
                '4fold|tc-cc-t|{}{}{}{}'.format(ma,ma,ma,ma): 41,
                '4fold|tc-cc-t|{}{}{}{}'.format(ma,ma,ma,mb): 42, 
                '4fold|tc-cc-t|{}{}{}{}'.format(ma,ma,mb,mb): 43,
                '4fold|tc-cc-t|{}{}{}{}'.format(ma,mb,ma,mb): 44, 
                '4fold|tc-cc-t|{}{}{}{}'.format(ma,mb,mb,mb): 45,
                '4fold|tc-cc-t|{}{}{}{}'.format(mb,mb,mb,mb): 46,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,ma): 47,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,ma,mb): 48,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,ma,ma): 49,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,ma,mb,mb): 50,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,ma): 51,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,ma,mb,mb,mb): 52,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,ma): 53,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,ma,mb): 54,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,ma,ma): 55,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,ma,mb,mb): 56,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,ma): 57,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,ma,mb,mb,mb,mb): 58,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,ma): 59,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,ma,mb): 60,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,ma,ma): 61,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,ma,mb,mb): 62,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,ma): 63,
                '6fold|subsurf|{}{}{}{}{}{}'.format(ma,mb,mb,mb,mb,mb): 64,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,ma): 65,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,ma,mb): 66,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,ma,ma): 67,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,ma,mb,mb): 68,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,ma): 69,
                '6fold|subsurf|{}{}{}{}{}{}'.format(mb,mb,mb,mb,mb,mb): 70}


# Use this label dictionary when site compostion is 
# considered. Useful for slabs with arbitrary number
# of components.
def get_multimetallic_slab_labels(surface, metals): 
    if surface in ['fcc111','hcp0001']:
        relations = {'ontop': ['terrace'],
                     'bridge': ['terrace'],
                     'fcc': ['terrace'],
                     'hcp': ['terrace'],
                     '6fold': ['subsurf']}

    elif surface in ['fcc100','bcc100']:
        relations = {'ontop': ['terrace'],
                     'bridge': ['terrace'],
                     '4fold': ['terrace']}

    elif surface in ['fcc110','hcp10m10h']:
        relations = {'ontop': ['step'], 
                     'bridge': ['step','sc-tc-h'],
                     'fcc': ['sc-tc-h'],
                     'hcp': ['sc-tc-h'],
                     '4fold': ['terrace'],
                     '5fold': ['terrace'],
                     '6fold': ['subsurf']}

    elif surface == 'fcc211':
        relations = {'ontop': ['step','terrace','corner'],
                     'bridge': ['step','terrace','corner','sc-tc-h','tc-cc-h','sc-cc-t'],
                     'fcc': ['sc-tc-h','tc-cc-h'],
                     'hcp': ['sc-tc-h','tc-cc-h'],
                     '4fold': ['sc-cc-t'],
                     '6fold': ['subsurf']}

    elif surface in ['fcc311','fcc331']:
        relations = {'ontop': ['step','terrace'],
                     'bridge': ['step','terrace','sc-tc-h','sc-tc-t'],
                     'fcc': ['sc-tc-h'],
                     'hcp': ['sc-tc-h'],
                     '4fold': ['sc-tc-t'],
                     '6fold': ['subsurf']}

    elif surface == 'fcc322':
        relations = {'ontop': ['step','terrace','corner'],
                     'bridge': ['step','terrace','corner','sc-tc-h','tc-cc-h','sc-cc-t'],
                     'fcc': ['terrace','sc-tc-h','tc-cc-h'],
                     'hcp': ['terrace','sc-tc-h','tc-cc-h'],
                     '4fold': ['sc-cc-t'],
                     '6fold': ['subsurf']}

    elif surface in ['fcc221','fcc332']:
        relations = {'ontop': ['step','terrace','corner'],
                     'bridge': ['step','terrace','corner','sc-tc-h','tc-cc-h','sc-cc-h'],
                     'fcc': ['terrace','sc-tc-h','tc-cc-h'],
                     'hcp': ['terrace','sc-tc-h','tc-cc-h'],
                     '6fold': ['subsurf']}

    elif surface == 'bcc110':
        relations = {'ontop': ['terrace'],
                     'shortbridge': ['terrace'],
                     'longbridge': ['terrace'],
                     '3fold': ['terrace']}

    elif surface == 'bcc111':
        relations = {'ontop': ['step','terrace','corner'],
                     'shortbridge': ['sc-tc-o','tc-cc-o'],
                     'longbridge': ['sc-cc-o'],
                     '3fold': ['sc-tc-cc-o']}

    elif surface == 'bcc210':
        relations = {'ontop': ['step','terrace','corner'],
                     'bridge': ['step','terrace','corner','sc-tc-o','tc-cc-o','sc-cc-t'],
                     '3fold': ['sc-tc-o','tc-cc-o'],
                     '4fold': ['sc-cc-t']}

    elif surface == 'bcc211':
        relations = {'ontop': ['step'], 
                     'bridge': ['step','sc-tc-o'],
                     '3fold': ['sc-tc-o'],
                     '4fold': ['terrace'],
                     '5fold': ['terrace']}

    elif surface == 'bcc310':
        relations = {'ontop': ['step','terrace'],
                     'bridge': ['step','terrace','sc-tc-o','sc-tc-t'],
                     '3fold': ['sc-tc-o'],
                     '4fold': ['sc-tc-t']}

    elif surface == 'hcp10m10t':
        relations = {'ontop': ['step','terrace'],
                     'bridge': ['step','terrace','sc-tc-t'],
                     '5fold': ['subsurf']}

    elif surface == 'hcp10m11':
        relations = {'ontop': ['step','terrace'],
                     'bridge': ['step','terrace','sc-tc-h'],
                     'fcc': ['sc-tc-h'],
                     'hcp': ['sc-tc-h'],
                     '4fold': ['subsurf'],
                     '5fold': ['subsurf'],
                     '6fold': ['subsurf']}

    elif surface == 'hcp10m12':
        relations = {'ontop': ['step','terrace','corner'],
                     'bridge': ['step','terrace','corner','sc-tc-h','tc-cc-t','sc-cc-h'],
                     'fcc': ['sc-tc-h','sc-cc-h'],
                     'hcp': ['sc-tc-h','sc-cc-h'],
                     '4fold': ['tc-cc-t'],
                     '6fold': ['subsurf']}

    d = {}
    count = 0 
    for k, vs in relations.items():
        if k == 'ontop':
            n = 1
        elif k in ['bridge','shortbridge','longbridge']:
            n = 2
        elif k in ['fcc','hcp','3fold']:
            n = 3
        elif k == '4fold':
            n = 4
        elif k == '5fold':
            n = 5
        elif k == '6fold':
            n = 6
        for v in vs:
            for p in product(metals, repeat=n):
                if k == '5fold':
                    comp = str(p[0]) + '-' + ''.join(p[1:])
                elif k == '4fold' and surface in ['fcc110','hcp10m10h','bcc211','hcp10m11']:
                    comp = ''.join(p[:2]) + '-' + ''.join(p[2:])
                else: 
                    comp = ''.join(p)
                count += 1
                d['{0}|{1}|{2}'.format(k, v, comp)] = count 
                
    return d


def get_cluster_signature_from_label(label, composition_effect=False, metals=[]):
    if not composition_effect:
        label_dict = get_monometallic_cluster_labels()
    else:
        if len(metals) <= 2:
            label_dict = get_bimetallic_cluster_labels(metals)
        else:
            label_dict = get_multimetallic_cluser_labels(metals)

    return list(label_dict.keys())[list(label_dict.values()).index(int(label))]


def get_slab_signature_from_label(label, surface, composition_effect=False, metals=[]):
    if not composition_effect:
        label_dict = get_monometallic_slab_labels(surface)
    else:
        if len(metals) <= 2:
            label_dict = get_bimetallic_slab_labels(surface, metals)
        else:
            label_dict = get_multimetallic_slab_labels(surface, metals)

    return list(label_dict.keys())[list(label_dict.values()).index(int(label))]
