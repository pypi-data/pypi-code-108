""" Deep-first search (DFS) functionality """

def get_DFS_path(G,v,seen=None,path=None):
    """
        Get DFS path
        ------------
        Get connected nodes, i.e, path, in molecular graph
        using deep first search (DFS) starting from v.

        Input
        -----
        G: dct(), molecular graph

    """
    if seen is None: seen = []
    if path is None: path = [v]

    seen.append(v)

    paths = []
    for t in G[v]:
        if t not in seen:
            t_path = path + [t]
            paths.append(t_path)
            paths.extend(get_DFS_path(G, t, seen[:], t_path))
    return paths


def get_DFS_longest_paths(G,keys=None):
    """
        Get DFS longest paths
        ---------------------
        Using get_DFS_path for every k starting point 
        in molecular graph to get all longest paths 
        for per k starting point. 

        Input
        -----
        G: dct(), molecular graph 

    """
    if keys is None:
        keys = G.keys()
    all_paths = []
    k_all_paths = []
    k_max_paths = []
    max_paths = []
    for k in list(keys):
        k_paths = get_DFS_path(G, k)
        print(k_paths)
        k_max_len   = max(len(p) for p in k_paths)
        k_max_paths = [p for p in k_paths if len(p) == k_max_len]
        all_paths += k_paths
        max_len = max(len(p) for p in all_paths)
        max_paths += k_max_paths
    return all_paths, max_len, max_paths

def get_DFS_cycles(graph, start, end):
    """
        
        Depth-first search (DFS)
        ------------------------
        Find cycles [A,A] in molecular graph. 
        Note: This is a generator, yielding one cycle at time. 

        Reference 
            - [1] https://stackoverflow.com/questions/40833612/find-all-cycles-in-a-graph-implementation
    """
    fringe = [(start, [])]
    while fringe:
        state, path = fringe.pop()
        if path and state == end:
            yield path
            continue
        for next_state in graph[state]:
            if next_state in path:
                continue
            fringe.append((next_state, path+[next_state]))

