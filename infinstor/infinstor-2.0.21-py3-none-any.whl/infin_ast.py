import ast
import astor
from ast import NodeVisitor
from . import gnode
import os

verbose = False

def writeAst(astTree, outfile):
    with open(outfile, "w") as f:
        f.write(ast.dump(astTree, include_attributes=True))
    f.close()

def get_source(tree):
    return astor.code_gen.to_source(tree)

def write_to_file(filename, src):
    with open(filename, "w") as f:
        f.write(src)
    f.close()


class ASTBuilder():
    srcfile = None
    srcString = None
    tree = None

    def setSourceFile(self, srcfile):
        self.srcfile = srcfile
        return self

    def setSourceString(self, srcString):
        self.srcString = srcString
        return self

    def build(self):
        if self.srcString is not None:
            self.tree = ast.parse(self.srcString)
        elif self.srcfile is not None:
            fh = open(self.srcfile)
            self.tree = ast.parse(fh.read())
            fh.close()
        else:
            raise Exception("No source found")
        return self

    def dumpAst(self, outfile):
        writeAst(self.tree, outfile)

    def getAst(self):
        return self.tree


class DataFrameVisitor(NodeVisitor):
    hotSymbol = None
    lastNode = None

    def __init__(self, transform_symbol):
        self.transform_symbol = transform_symbol

    def visit_FunctionDef(self, node):
        if node.name == self.transform_symbol:
            self.hotSymbol = node.name
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Module(self, node):
        for child in ast.iter_child_nodes(node):
            self.visit(child)
            if self.hotSymbol is not None and self.lastNode is None:
                self.lastNode = child

    def getLastNode(self):
        return self.lastNode

    def getDfSymbolId(self):
        return self.hotSymbol



class DependencyBuilder(NodeVisitor):
    lastNode = None
    currentTopNode = None
    idTopNodeMap = {}
    idDependencies = {}
    tmpIdList = set()
    tmpIdMutated = set()
    importNodes = set()

    def __init__(self, lastNode):
        self.lastNode = lastNode

    def visit_Module(self, node):
        for child in ast.iter_child_nodes(node):
            self.currentTopNode = child
            self.tmpIdList = set()
            self.tmpIdMutated = set()
            self.visit(child)
            for id in self.tmpIdMutated:
                if self.idTopNodeMap.get(id) is None:
                    self.idTopNodeMap[id] = set()
                self.idTopNodeMap[id].add(child)
            self.idDependencies[child] = set()
            for id in self.tmpIdList:
                self.idDependencies[child].add(id)
            if child == self.lastNode:
                break

    def visit_Assign(self, node):
        self.extractIdFromAssign(node)
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_FunctionDef(self, node):
        self.extractId(node, True)
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_ClassDef(self, node):
        self.extractId(node, True)
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Name(self, node):
        self.extractId(node, False)
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Call(self, node):
        self.extractIdFromCall(node)
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def generic_visit(self, node):
        self.extractId(node, False)
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Import(self, node):
        self.handle_ImportNode(node)

    def visit_ImportFrom(self, node):
        self.handle_ImportNode(node)

    def handle_ImportNode(self, node):
        self.importNodes.add(self.currentTopNode)
        for child in ast.iter_child_nodes(node):
            self.visit(child)


    def extractIdFromAssign(self, node):
        targets = node.targets
        for t in targets:
            if hasattr(t, "id"):
                self.tmpIdList.add(t.id)
                self.tmpIdMutated.add(t.id)
            elif hasattr(t, "value") and hasattr(t.value, "id"):
                self.tmpIdList.add(t.value.id)
                self.tmpIdMutated.add(t.value.id)

    def extractId(self, node, mutated):
        id = None
        try:
            if node.id:
                self.tmpIdList.add(node.id)
                if mutated:
                    self.tmpIdMutated.add(node.id)
                id = node.id
        except AttributeError:
            # ignore
            pass

        try:
            if node.name:
                self.tmpIdList.add(node.name)
                if mutated:
                    self.tmpIdMutated.add(node.name)
                id = node.name
        except AttributeError:
            # ignore
            pass
        return id

    def extractIdFromCall(self, node):
        if isinstance(node.func, ast.Name):
            self.tmpIdList.add(node.func.id)

        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if hasattr(node.func.value, "id"):
                self.tmpIdList.add(node.func.value.id)
                if (func_name in ("append")):
                    self.tmpIdMutated.add(node.func.value.id)


    def getDependencyMap(self):
        return self.idDependencies

    def getIdNodeMap(self):
        return self.idTopNodeMap

    def getImportNodes(self):
        return self.importNodes


def noErrorPop(collection):
    try:
        return collection.pop()
    except IndexError:
        return None

"""
   One of src_file or src_str must be set.
   If both set, src_str is given preference and src_file is ignored
"""
def extract_transform(transform_symbol, src_file=None, src_str=None, workspace_dir="/tmp"):
    astbuilder = None
    if src_str is not None:
        astbuilder = ASTBuilder().setSourceString(src_str).build()
    elif src_file is not None:
        astbuilder = ASTBuilder().setSourceFile(src_file).build()
    else:
        raise Exception("No source specified")

    astbuilder.dumpAst( workspace_dir + "/ast-for-src-input.txt")
    tree = astbuilder.getAst()

    dfv = DataFrameVisitor(transform_symbol)
    dfv.visit(tree)

    dependencyBuilder = DependencyBuilder(dfv.getLastNode())
    dependencyBuilder.visit(tree)

    nodeIdDependencyMap = dependencyBuilder.getDependencyMap()
    idToMutatingNodeMap = dependencyBuilder.getIdNodeMap()

    allImportNodes = dependencyBuilder.getImportNodes()

    if (verbose == True):
        print("NODE ID DEPENDENCY MAP")
        gnode.printNodeGraph(nodeIdDependencyMap)
        print("ID to Mutating node map")
        gnode.printNodeGraph(idToMutatingNodeMap)


    startIds = []
    currNode = dfv.getLastNode()
    if nodeIdDependencyMap.get(currNode) is not None:
        for i in nodeIdDependencyMap.get(currNode):
            startIds.append(i)
    currId = noErrorPop(startIds)
    nodeGraph = {}
    idVisited = set()
    while currId is not None:
        if idToMutatingNodeMap.get(currId) is None:
            currId = noErrorPop(startIds)
            continue
        mutatingNodeList = idToMutatingNodeMap[currId]
        for mn in mutatingNodeList:
            if nodeGraph.get(gnode.GNode(currNode)) is None:
                nodeGraph[gnode.GNode(currNode)] = set()
            nodeGraph[gnode.GNode(currNode)].add(gnode.GNode(mn))
            if nodeIdDependencyMap.get(mn) is not None:
                for i in nodeIdDependencyMap.get(mn):
                    if i not in idVisited:
                        startIds.append(i)
        idVisited.add(currId)
        currId = noErrorPop(startIds)

    if (verbose == True):
        gnode.printNodeGraph(nodeGraph)

    hotGNodes = gnode.getAllConnectedNodes(nodeGraph, [gnode.GNode(dfv.getLastNode())])

    hotNodes = set()
    for hgn in hotGNodes:
        hotNodes.add(hgn.node)

    for impn in allImportNodes:
        hotNodes.add(impn)

    if (verbose == True):
        for n in hotNodes:
            print("Hot Node -- " + str(n))

    transformedTree = gnode.DFTransformer().visitWithContext(tree, hotNodes)

    return transformedTree

## Modifies the treee in place
def add_type_statements(astTree):
    gnode.PrintTypesTransformer().visit(astTree)


if __name__ == "__main__":
    targetDir = "../../target"
    if not os.path.isdir(targetDir):
        os.mkdir(targetDir)
    ##transformAst = extract_transform(src_file="../test/infin-transform-example.py", workspace_dir=targetDir)
    fh = open("../test/infin-transform-example.py")
    srcString = fh.read()
    fh.close()
    transformAst = extract_transform(src_str=srcString, workspace_dir=targetDir)
    add_type_statements(transformAst)
    transformSrc = get_source(transformAst)
    write_to_file(targetDir + "/infin-transform-modified.py", transformSrc)
