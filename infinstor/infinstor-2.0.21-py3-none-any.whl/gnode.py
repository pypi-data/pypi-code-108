import ast
from ast import NodeVisitor, NodeTransformer

verbose = False

class GNode:
    def __init__(self, node):
        self.node = node
        self.visited = False

    def set(self, v):
        self.visited = v

    def __str__(self):
        return self.node.__class__.__name__

    def __eq__(self, other):
        return self.node == other.node

    def __ne__(self, other):
        return self.node != other.node

    def __hash__(self):
        return self.node.__hash__()


def getAllConnectedNodes(nodeGraph, initialNodes):
    nodesToVisit = []
    connectedNodes = set()
    for n in initialNodes:
        nodesToVisit.append(n)
        connectedNodes.add(n)

    while (len(nodesToVisit) > 0):
        gn = nodesToVisit[0]
        nodesToVisit.remove(gn)
        gn.visited = True
        for next in nodeGraph.get(gn, []):
            connectedNodes.add(next)
            if (not next.visited):
                nodesToVisit.append(next)
    return connectedNodes


class DFTransformer(NodeTransformer):
    hotParent = False
    hotNodes = None

    def generic_visit(self, node):
        if (node.__class__.__name__ == "Module"):
            return super().generic_visit(node)
        if (node in self.hotNodes):
            self.hotParent = True
            ret = super().generic_visit(node)
            self.hotParent = False
            return ret
        elif (self.hotParent == True):
            return super().generic_visit(node)
        else:
            return None

    def visitWithContext(self, tree, hotNodes):
        self.hotNodes = hotNodes
        return self.visit(tree)


class PrintTypesTransformer(NodeTransformer):

    def visit_Assign(self, node):
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        retNodes = [node]
        for t in node.targets:
            if hasattr(t, "id"):
                typePrintNode = ast.Expr(value=ast.Call(func=ast.Name(id="print"), args=[
                    ast.BinOp(left=ast.Str(s=t.id + " : "), op=ast.Add(), right=ast.Call(func=ast.Name(id='str'), args=[
                        ast.Call(func=ast.Name(id='type'), args=[ast.Name(id=t.id)], keywords=[])], keywords=[]))],
                                                  keywords=[]))
                retNodes.append(typePrintNode)
        return retNodes

    """
        'ret_nodes' must be appended with the new nodes being injected in the AST
        Returns ast.Name with tmpId
    """
    def create_new_var(self, node, tmpId, ret_nodes):
        if (verbose == True):
            print("Modify Return Expression")
        newAssign = \
            ast.Assign(targets=[ast.Name(id=tmpId, ctx=ast.Store(),
                                         lineno=0, col_offset=0)], value=node)
        ret_nodes.append(newAssign)
        typePrintNode = ast.Expr(value=ast.Call(func=ast.Name(id="print"), args=[
            ast.BinOp(left=ast.Str(s=tmpId + " : "), op=ast.Add(), right=ast.Call(func=ast.Name(id='str'), args=[
                ast.Call(func=ast.Name(id='type'), args=[ast.Name(id=tmpId)], keywords=[])], keywords=[]))],
                                                keywords=[]))
        ret_nodes.append(typePrintNode)
        return ast.Name(id=tmpId, ctx=ast.Load(), lineno=0, col_offset=0)


    def create_new_return(self, return_vars):
        if len(return_vars) > 1:
            tuple = ast.Tuple(elts=return_vars, ctx=ast.Load(), lineno=0, col_offset=0)
            return ast.Return(value=tuple, lineno=0, col_offset=0)
        else:
            return ast.Return(value=return_vars[0], lineno=0, col_offset=0)


    def visit_Return(self, node):
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        retNodes = []
        return_vars = []
        if isinstance(node.value, ast.Name):
            # Nothing needs to be done
            pass
        elif isinstance(node.value, ast.Tuple):
            index = 0
            for childNode in node.value.elts:
                if isinstance(childNode, ast.Name):
                    return_vars.append(childNode)
                else:
                    tmpId = 'tmp_ret_val_' + str(index)
                    index = index+1
                    var_name_node = self.create_new_var(childNode, tmpId, retNodes)
                    return_vars.append(var_name_node)
        else:
            tmpId = 'tmp_ret_val'
            var_name_node = self.create_new_var(node.value, tmpId, retNodes)
            return_vars.append(var_name_node)

        if not retNodes:
            # No code change needed
            return node
        else:
            newReturn = self.create_new_return(return_vars)
            retNodes.append(newReturn)
            return retNodes

def printNodeGraph(graph):
    for n in graph.keys():
        print(str(n) + " : ", end="")
        for d in graph[n]:
            print(str(d), end=", ")
        print("\n")
