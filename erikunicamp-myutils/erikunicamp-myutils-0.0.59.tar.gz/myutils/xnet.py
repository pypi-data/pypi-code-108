from igraph import *;
import io;
import numpy as np;
import re;

def __textSplit2(text):
	entries = text.split()
	if(len(entries)<2):
		raise ValueError();
	return (float(entries[0]),float(entries[1]));

def __textSplit3(text):
	entries = text.split()
	if(len(entries)<3):
		raise ValueError();
	return (float(entries[0]),float(entries[1]),float(entries[2]));

__propertyHeaderRegular = re.compile("#([ve]) \"(.+)\" ([sn]|v2|v3)");
__propertyFunctions = {
	"s": str,
	"n": float,
	"v2": __textSplit2,
	"v3": __textSplit3
}

def __readXnetVerticesHeader(fp,currentLineIndex,lastLine=""):
	headerLine = lastLine;
	if(len(headerLine)==0):
		for lineData in fp:
			headerLine = lineData.decode("utf-8").rstrip();
			currentLineIndex+=1;
			if(len(headerLine)>0):
				break;

	headerEntries = headerLine.split();
	nodeCount = 0;

	if(len(headerEntries)==0 or headerEntries[0].lower() != "#vertices"):
		raise ValueError("Malformed xnet file [%s:%d]\n\t>%s"%(fp.name,currentLineIndex,headerLine));

	try:
		nodeCount = int(headerEntries[1]);
	except ValueError:
		raise ValueError("Malformed xnet file [%s:%d]\n\t>%s"%(fp.name,currentLineIndex,headerLine));

	return (nodeCount,currentLineIndex,"");

def __readXnetNames(fp,currentLineIndex,lastLine=""):
	names = [];
	fileEnded = True;
	for lineData in fp:
		lineString = lineData.decode("utf-8").rstrip();
		currentLineIndex+=1;
		
		if(len(lineString)==0):
			continue;
		
		lastLine = lineString;
		
		if(len(lineString)>0 and lineString[0]=="#"):
			fileEnded = False;
			break;
		
		if(len(lineString)>1 and lineString[0]=="\"" and lineString[-1]=="\""):
			lineString = lineString[1:-1];
		
		names.append(lineString);

	if(fileEnded):
		lastLine = "";
	return (names,currentLineIndex,lastLine);


def __readXnetEdgesHeader(fp,currentLineIndex,lastLine=""):
	headerLine = lastLine;
	if(len(headerLine)==0):
		for lineData in fp:
			headerLine = lineData.decode("utf-8").rstrip();
			currentLineIndex+=1;
			if(len(headerLine)>0):
				break;
	
	headerEntries = headerLine.split();
	
	weighted = False;
	directed = False;

	if(len(headerEntries)==0 or headerEntries[0].lower() != "#edges"):
		raise ValueError("Malformed xnet file [%s:%d]\n\t>%s"%(fp.name,currentLineIndex,headerLine));

	for headerEntry in headerEntries:
		if(headerEntry == "weighted"):
			weighted = True;
		if(headerEntry == "nonweighted"):
			weighted = False;
		if(headerEntry == "directed"):
			directed = True;
		if(headerEntry == "undirected"):
			directed = False;

	return ((weighted,directed),currentLineIndex,"");

def __readXnetEdges(fp,currentLineIndex,lastLine=""):
	edges = [];
	weights = [];
	fileEnded = True;
	for lineData in fp:
		lineString = lineData.decode("utf-8").rstrip();
		currentLineIndex+=1;
		
		if(len(lineString)==0):
			continue;
		
		lastLine = lineString;
		
		if(len(lineString)>0 and lineString[0]=="#"):
			fileEnded=False;
			break;
		
		entries = lineString.split();

		if(len(entries)<2):
			raise ValueError("Malformed xnet file [%s:%d]\n\t>%s"%(fp.name,currentLineIndex,headerLine));
		try:
			edge = (int(entries[0]),int(entries[1]));
			weight = 1.0;
			if(len(entries)>2):
				weight = float(entries[2]);
			edges.append(edge);
			weights.append(weight);
		except ValueError:
			raise ValueError("Malformed xnet file [%s:%d]\n\t>%s"%(fp.name,currentLineIndex,headerLine));

	if(fileEnded):
		lastLine = "";
	return ((edges,weights),currentLineIndex,lastLine);

def __readXnetPropertyHeader(fp,currentLineIndex,lastLine=""):
	global __propertyHeaderRegular;
	headerLine = lastLine;
	if(len(headerLine)==0):
		for lineData in fp:
			headerLine = lineData.decode("utf-8").rstrip();
			currentLineIndex+=1;
			if(len(headerLine)>0):
				break;

	headerEntries = __propertyHeaderRegular.findall(headerLine);

	if(len(headerEntries)==0 or (len(headerEntries)==1 and len(headerEntries[0])!=3)):
		raise ValueError("Malformed xnet file [%s:%d]\n\t>%s"%(fp.name,currentLineIndex,headerLine));
	
	(propertyType,propertyName,propertyFormat) = headerEntries[0];
	return ((propertyType,propertyName,propertyFormat),currentLineIndex,"");

def __readXnetProperty(fp,propertyFormat,currentLineIndex,lastLine=""):
	global __propertyFunctions;
	properties = [];
	propertyFunction = __propertyFunctions[propertyFormat];
	fileEnded = True;
	for lineData in fp:
		lineString = lineData.decode("utf-8").rstrip();
		currentLineIndex+=1;
		
		if(len(lineString)==0):
			continue;
		
		lastLine = lineString;
		
		if(len(lineString)>0 and lineString[0]=="#"):
			fileEnded = False;
			break;
		
		if(len(lineString)>1 and lineString[0]=="\"" and lineString[-1]=="\""):
			lineString = lineString[1:-1];

		try:
			properties.append(propertyFunction(lineString));
		except ValueError:
			raise ValueError("Malformed xnet file [%s:%d]\n\t>%s"%(fp.name,currentLineIndex,headerLine));

	if(fileEnded):
		lastLine = "";

	return (properties,currentLineIndex,lastLine);

def xnet2igraph(fileName='test.xnet'):
	"""
	Read a Graph from a xnet formatted file.
	
	Parameters
	----------
	fileName : string
	    Input file path.
	"""
	network = None;
	with open(fileName, 'rb') as fp:
		currentLineIndex = 0;
		lastLine = "";
		(nodeCount,currentLineIndex,lastLine) = __readXnetVerticesHeader(fp,currentLineIndex,lastLine);
		(names,currentLineIndex,lastLine) = __readXnetNames(fp,currentLineIndex,lastLine);
		if(len(names)>0 and len(names)<nodeCount):
			raise ValueError("Malformed xnet file [%s:%d]\n\t>%s [%d entries expected but only %d found]"%(fp.name,currentLineIndex,headerLine,nodeCount,len(names)));
		((weighted,directed),currentLineIndex,lastLine) = __readXnetEdgesHeader(fp,currentLineIndex,lastLine);
		((edges,weights),currentLineIndex,lastLine) = __readXnetEdges(fp,currentLineIndex,lastLine);
		network = Graph(nodeCount,edges=edges,directed=directed);
		if(len(names)>0):
			network.vs["name"] = names;
		if(weighted):
			network.es["weight"] = weights;
		while(lastLine!=""):
			((propertyType,propertyName,propertyFormat),currentLineIndex,lastLine) = __readXnetPropertyHeader(fp,currentLineIndex,lastLine);
			(properties,currentLineIndex,lastLine) = __readXnetProperty(fp,propertyFormat,currentLineIndex,lastLine);
			if(propertyType=="e"):
				if(len(properties)>0 and len(properties)<len(edges)):
					raise ValueError("Malformed xnet file [%s:%d]\n\t>%s [%d entries expected but only %d found]"%(fp.name,currentLineIndex,headerLine,len(edges),len(properties)));
				network.es[propertyName] = properties;
			elif(propertyType=="v"):
				if(len(properties)>0 and len(properties)<nodeCount):
					raise ValueError("Malformed xnet file [%s:%d]\n\t>%s [%d entries expected but only %d found]"%(fp.name,currentLineIndex,headerLine,nodeCount,len(properties)));
				network.vs[propertyName] = properties;
	return network;



def igraph2xnet(g,fileName='test.xnet',ignoredNodeAtts=[],ignoredEdgeAtts=[]):
	"""
	Write igraph object to .xnet format.
	
	Vertex attributes 'name' and 'weight' are treated in special manner. They
	correspond to attributes assigned inside the #vertices tag.
	
	Edge attribute 'weight' is assigned to edges inside the #edges tag.
	
	Parameters
	----------
	g : igraph.Graph
	    Input graph.
	fileName : string
	    Output file.
	ignoredNodeAtts : list
	    List of node attributes to ignore when writing graph.
	ignoredEdgeAtts : list
	    List of edge attributes to ignore when writing graph.
	"""

	N = g.vcount()
	E = g.ecount()
	
	nodesAtt = g.vs.attributes()
	edgesAtt = g.es.attributes()

	if (('weight' in nodesAtt) & ('weight' not in ignoredNodeAtts)):
		isNodeWeighted = True
		isNodeWeightedString = 'weighted'
	else:
		isNodeWeighted = False
		isNodeWeightedString = 'nonweighted'
		
	if (('name' in nodesAtt) & ('name' not in ignoredNodeAtts)):
		isNodeNamed = True
	else:
		isNodeNamed = False		

	fd = open(fileName,'w')
	fd.write('#vertices '+str(N)+' '+isNodeWeightedString+'\n')

	if (isNodeNamed & isNodeWeighted):
		for i in range(N):
			fd.write('\"'+g.vs[i]['name']+'\" '+str(g.vs[i]['weight'])+'\n')
	elif (isNodeNamed & (not isNodeWeighted)):
		for i in range(N):
			fd.write('\"'+g.vs[i]['name']+'\"'+'\n')
	elif ((not isNodeNamed) & isNodeWeighted):
		for i in range(N):
			fd.write(str(g.vs[i]['weight'])+'\n')
			

	if (('weight' in edgesAtt) & ('weight' not in ignoredEdgeAtts)):
		isEdgeWeighted = True
		isEdgeWeightedString = 'weighted'
	else:
		isEdgeWeighted = False		
		isEdgeWeightedString = 'nonweighted'

	if (g.is_directed()==True):
		isEdgeDirected = True
		isEdgeDirectedString = 'directed'
	else:
		isEdgeDirected = False			
		isEdgeDirectedString = 'undirected'
	
	fd.write('#edges '+isEdgeWeightedString+' '+isEdgeDirectedString+'\n')
	
	for i in range(E):
			
		edge = g.es[i].tuple
		if (isEdgeWeighted):
			fd.write(str(edge[0])+' '+str(edge[1])+' '+str(g.es[i]['weight'])+'\n')
		else:			
			fd.write(str(edge[0])+' '+str(edge[1])+'\n')
		
	if (isNodeWeighted):	
		nodesAtt.remove('weight')
	if (isNodeNamed):
		nodesAtt.remove('name')
	if (isEdgeWeighted):
		edgesAtt.remove('weight')
		
	nodesAtt.sort()
	edgesAtt.sort()
	
	for att in nodesAtt:
		if (att not in ignoredNodeAtts):
			sample = g.vs[0][att]
						
			typeSample = type(sample)
			if (typeSample==str):
				typeSampleString = 's'			
			elif (np.isscalar(sample)==True):
				typeSampleString = 'n'
			elif ((typeSample==list)|(typeSample==tuple)):
				if (len(sample)==2):
					typeSampleString = 'v2'
				elif (len(sample)==3):
					typeSampleString = 'v3'
				
			fd.write('#v \"'+att+'\" '+typeSampleString+'\n')
			for i in range(N):
				if (typeSampleString == 'n'):
					fd.write(str(g.vs[i][att])+'\n')
				elif (typeSampleString == 'v2'):
					fd.write(str(g.vs[i][att][0])+' '+str(g.vs[i][att][1])+'\n')
				elif (typeSampleString == 'v3'):
					fd.write(str(g.vs[i][att][0])+' '+str(g.vs[i][att][1])+' '+str(g.vs[i][att][2])+'\n')
				elif (typeSampleString == 's'):
					fd.write('\"'+g.vs[i][att]+'\"'+'\n')
				

	for att in edgesAtt:
		if (att not in ignoredEdgeAtts):
			sample = g.es[0][att]
			
			typeSample = type(sample)
			if (typeSample==str):
				typeSampleString = 's'			
			elif (np.isscalar(sample)==True):
				typeSampleString = 'n'
			elif ((typeSample==list)|(typeSample==tuple)):
				if (len(sample)==2):
					typeSampleString = 'v2'
				elif (len(sample)==3):
					typeSampleString = 'v3'
				
			fd.write('#e \"'+att+'\" '+typeSampleString+'\n')
			for i in range(E):
				if (typeSampleString == 'n'):
					fd.write(str(g.es[i][att])+'\n')
				elif (typeSampleString == 'v2'):
					fd.write(str(g.es[i][att][0])+' '+str(g.es[i][att][1])+'\n')
				elif (typeSampleString == 'v3'):
					fd.write(str(g.es[i][att][0])+' '+str(g.es[i][att][1])+' '+str(g.es[i][att][2])+'\n')
				elif (typeSampleString == 's'):
					fd.write('\"'+g.es[i][att]+'\"'+'\n')				
				
	fd.close()	
	
def igraph2xnet_fast(g):
	"""
	Convert igraph object to a .xnet format string. This string 
	can then be written to a file or used in a pipe. The purpose 
	of this function is to have a fast means to convert a graph
	without any attributes to the .xnet format.
	
	Parameters
	----------
	g : igraph.Graph
	    Input graph.
	
	Returns
	-------
	strOut : string
	    String that can be written to a .xnet file.
	"""

	N = g.vcount()
	strOut = "#vertices "+str(N)+" nonweighted\n#edges nonweighted undirected"
	
	edList = np.array(g.get_edgelist())
	
	s = io.StringIO()
	np.savetxt(s, edList, fmt='%d', header=strOut, comments='')
	
	strOut = s.getvalue()
	s.close()
	
	return strOut	

def xnet2graphml(filename, outfilename='/tmp/mygraph.graphml'):
	"""
	Convert xnet object to a .graphml format
	
	Parameters
	----------
	g : xnet graph
	
	Returns
	-------
	strOut : string
	    String that can be written to a .xnet file.
	"""
	g = xnet2igraph(filename)

	if not 'x' in g.vertex_attributes() and 'posx' in g.vertex_attributes():
		g.vs['x'] = g.vs['posx']; del g.vs['posx']
	if not 'y' in g.vertex_attributes() and 'posy' in g.vertex_attributes():
		g.vs['y'] = g.vs['posy']; del g.vs['posy']

	for attr in g.vertex_attributes():
		if type(g.vs[0][attr]) != float: continue
		g.vs[attr] = np.array(g.vs[attr]).astype(str).tolist()
    
	import igraph
	igraph.write(g, outfilename)
