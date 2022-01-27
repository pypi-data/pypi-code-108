import matplotlib.pyplot as plt
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
import PyEFVLib
import numpy as np

def navierStokes(problemData):
	propertyData 	 = problemData.propertyData
	timeStep 		 = problemData.timeStep
	grid 			 = problemData.grid
	numberOfVertices = grid.numberOfVertices
	dimension 		 = grid.dimension

	csvSaver = PyEFVLib.CsvSaver(grid, problemData.outputFilePath, problemData.libraryPath)
	meshioSaver = PyEFVLib.MeshioSaver(grid, problemData.outputFilePath, problemData.libraryPath, extension="xdmf")

	vField    = np.repeat(0.0, dimension*numberOfVertices)
	prevVField = np.concatenate((problemData.initialValues["v_x"], problemData.initialValues["v_y"], problemData.initialValues["v_z"])) if dimension==3 else np.concatenate((problemData.initialValues["v_x"], problemData.initialValues["v_y"]))

	pField    = np.repeat(0.0, numberOfVertices)
	prevPField = problemData.initialValues["p"].copy()

	prevResults = np.concatenate((prevVField,prevPField))
	results = prevResults.copy()

	def assembleMatrix():
		matrix 		= np.zeros(((1+dimension)*numberOfVertices, (1+dimension)*numberOfVertices))
		for region in grid.regions:
			mu         = propertyData.get(region.handle, "mu")
			rho       = propertyData.get(region.handle, "rho")
			g = np.array([0.0, propertyData.get(region.handle, "g"), 0.0])[:dimension]

			for element in region.elements:
				# ∇·V      - Conservação da Massa
				for innerFace in element.innerFaces:
					area = innerFace.area.getCoordinates()[:dimension]
					shapeFunctions = innerFace.getShapeFunctions()

					backwardsHandle, forwardHandle = innerFace.getNeighborVerticesHandles()
					for coord in range(dimension):
						for local, vertex in enumerate(element.vertices):
							# estava coord nos dois
							matrix[backwardsHandle+(dimension)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += shapeFunctions[local] * area[coord]
							matrix[forwardHandle+(dimension)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] -= shapeFunctions[local] * area[coord]

				# ∇·P    - Termo da pressão
				for face in element.innerFaces:
					area = face.area.getCoordinates()[:dimension]
					shapeFunctions = face.getShapeFunctions()

					backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
					for coord in range(dimension):
						for local, vertex in enumerate(element.vertices):
							# estava dimension nos dois
							matrix[backwardsHandle+(coord)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] += shapeFunctions[local] * area[coord]
							matrix[forwardHandle+(coord)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] -= shapeFunctions[local] * area[coord]

				# ∇·(ρVV) - Fluxo de massa no VC
				# Começa tudo zero na primeira iteração pois V=0
				prevVElementField = np.array([[prevResults[vertex.handle + coord * numberOfVertices] for vertex in element.vertices] for coord in range(dimension)])
				for face in element.innerFaces:
					area = face.area.getCoordinates()[:dimension]
					shapeFunctions = face.getShapeFunctions()

					matrixCoefficients = rho * np.dot( np.dot(prevVElementField, shapeFunctions), area ) * shapeFunctions

					backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
					for local, vertex in enumerate(element.vertices):
						for coord in range(dimension):
							matrix[backwardsHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += matrixCoefficients[local]
							matrix[forwardHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] -= matrixCoefficients[local]

				# -∇·(μ∇V) - Termo viscoso
				for face in element.innerFaces:
					area = face.area.getCoordinates()[:dimension]
					backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
					for local, vertex in enumerate(element.vertices):
						for c1 in range(dimension):
							for c2 in range(dimension):
								matrix[backwardsHandle+(c1)*numberOfVertices][vertex.handle+(c2)*numberOfVertices] -= face.globalDerivatives[c1][local] * area[c2]
								matrix[forwardHandle+(c1)*numberOfVertices][vertex.handle+(c2)*numberOfVertices] += face.globalDerivatives[c1][local] * area[c2]

		# plt.spy(matrix)
		# plt.show()
		# exit()

		# Dirichlet Boundary Conditions
		for bCondition in problemData.dirichletBoundaries["v_x"]:
			for vertex in bCondition.boundary.vertices:
				matrix[vertex.handle+(0)*numberOfVertices] = np.zeros((1+dimension)*numberOfVertices)
				matrix[vertex.handle+(0)*numberOfVertices][vertex.handle+(0)*numberOfVertices] = 1.0

		for bCondition in problemData.dirichletBoundaries["v_y"]:
			for vertex in bCondition.boundary.vertices:
				matrix[vertex.handle+(1)*numberOfVertices] = np.zeros((1+dimension)*numberOfVertices)
				matrix[vertex.handle+(1)*numberOfVertices][vertex.handle+(1)*numberOfVertices] = 1.0

		if dimension == 3:
			for bCondition in problemData.dirichletBoundaries["v_z"]:
				for vertex in bCondition.boundary.vertices:
					matrix[vertex.handle+(2)*numberOfVertices] = np.zeros((1+dimension)*numberOfVertices)
					matrix[vertex.handle+(2)*numberOfVertices][vertex.handle+(2)*numberOfVertices] = 1.0

		for bCondition in problemData.dirichletBoundaries["p"]:
			for vertex in bCondition.boundary.vertices:
				matrix[vertex.handle+(dimension)*numberOfVertices] = np.zeros((1+dimension)*numberOfVertices)
				matrix[vertex.handle+(dimension)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] = 1.0

		# Inverse Matrix
		# inverseMatrix = np.linalg.inv(matrix)
		return matrix

	def assembleIndependent():
		independent = np.zeros((1+dimension)*numberOfVertices)

		for region in grid.regions:
			mu         = propertyData.get(region.handle, "mu")
			rho       = propertyData.get(region.handle, "rho")
			g = np.array([0.0, propertyData.get(region.handle, "g"), 0.0])[:dimension]

		# Neumann Boundary Condition
		for bCondition in problemData.neumannBoundaries["v_x"]:
			for facet in bCondition.boundary.facets:
				for outerFace in facet.outerFaces:
					independent[outerFace.vertex.handle+(0)*numberOfVertices] += bCondition.getValue(outerFace.handle) * np.linalg.norm(outerFace.area.getCoordinates())

		for bCondition in problemData.neumannBoundaries["v_y"]:
			for facet in bCondition.boundary.facets:
				for outerFace in facet.outerFaces:
					independent[outerFace.vertex.handle+(1)*numberOfVertices] += bCondition.getValue(outerFace.handle) * np.linalg.norm(outerFace.area.getCoordinates())

		if dimension == 3:
			for bCondition in problemData.neumannBoundaries["v_z"]:
				for facet in bCondition.boundary.facets:
					for outerFace in facet.outerFaces:
						independent[outerFace.vertex.handle+(2)*numberOfVertices] += bCondition.getValue(outerFace.handle) * np.linalg.norm(outerFace.area.getCoordinates())

		for bCondition in problemData.neumannBoundaries["p"]:
			for facet in bCondition.boundary.facets:
				for outerFace in facet.outerFaces:
					independent[outerFace.vertex.handle+(dimension)*numberOfVertices] += bCondition.getValue(outerFace.handle) * np.linalg.norm(outerFace.area.getCoordinates())

		# Dirichlet Boundary Condition
		for bCondition in problemData.dirichletBoundaries["v_x"]:
			for vertex in bCondition.boundary.vertices:
				independent[vertex.handle+(0)*numberOfVertices] = bCondition.getValue(vertex.handle)

		for bCondition in problemData.dirichletBoundaries["v_y"]:
			for vertex in bCondition.boundary.vertices:
				independent[vertex.handle+(1)*numberOfVertices] = bCondition.getValue(vertex.handle)

		if dimension == 3:
			for bCondition in problemData.dirichletBoundaries["v_z"]:
				for vertex in bCondition.boundary.vertices:
					independent[vertex.handle+(2)*numberOfVertices] = bCondition.getValue(vertex.handle)

		for bCondition in problemData.dirichletBoundaries["p"]:
			for vertex in bCondition.boundary.vertices:
				independent[vertex.handle+(dimension)*numberOfVertices] = bCondition.getValue(vertex.handle)

		return independent

	tolerance = problemData.tolerance
	difference = 2*tolerance
	iteration = 0
	converged = False

	while difference > tolerance:
		matrix = assembleMatrix()
		independent = assembleIndependent()

		countDict = dict()
		for i in range(numberOfVertices):
			for j in range(3):
				for k in range(3):
					if matrix[i+j*numberOfVertices][i+k*numberOfVertices] != 0.0:
						s = f"({j},{k})"
						print(s, end=', ')
						if s in countDict:
							countDict[s] += 1
						else:
							countDict[s] = 1
			print("")
		for k,v in countDict.items():
			print(k,v)
		exit()

		# Resolve Conservação da massa para u (V_x)
		eq_idx, var_idx = 2, 0
		for i in range(numberOfVertices):
			results[i+var_idx*numberOfVertices] += ( independent[i+eq_idx*numberOfVertices] - np.dot(matrix[i+eq_idx*numberOfVertices], results) ) / matrix[i+eq_idx*numberOfVertices][i+var_idx*numberOfVertices]

		# Resolve Quantidade de Movimento em y para v (V_v)
		eq_idx, var_idx = 1, 1
		for i in range(numberOfVertices):
			results[i+var_idx*numberOfVertices] += ( independent[i+eq_idx*numberOfVertices] - np.dot(matrix[i+eq_idx*numberOfVertices], results) ) / matrix[i+eq_idx*numberOfVertices][i+var_idx*numberOfVertices]

		# Resolve Quantidade de Movimento em x para p
		eq_idx, var_idx = 0, 2
		for i in range(numberOfVertices):
			results[i+var_idx*numberOfVertices] += ( independent[i+eq_idx*numberOfVertices] - np.dot(matrix[i+eq_idx*numberOfVertices], results) ) / matrix[i+eq_idx*numberOfVertices][i+var_idx*numberOfVertices]

		difference = max(abs(results - prevResults))
		prevResults = results.copy()

		print(iteration, difference)
		iteration += 1




def main():
	p2=1000
	p1=2000
	L=3
	H=1
	mu=1
	print("{:>14}	{:>14}	{:>14}	{:>14}	{:>14}	{:>14}".format("pDifference", "uDifference", "vDifference", "uMean", "pMean", "vMean"))
	problemData = PyEFVLib.ProblemData(
		meshFilePath = "placa_plana.msh",
		outputFilePath = "{RESULTS}/navierStokes",
		numericalSettings = PyEFVLib.NumericalSettings( timeStep = 1000, tolerance = 1, maxNumberOfIterations = 50 ),
		propertyData = PyEFVLib.PropertyData({
			'Body':
			{
				'mu': 1,
				'rho': 1000.0,
				'g': 0.0,
			},
		}),
		boundaryConditions = PyEFVLib.BoundaryConditions({
            'v_x': {
                'InitialValue': 27.78,
                'West': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Variable, 'value' : f"{(p2-p1)/L}*y*(y-{H})/{2*mu}" },
                'East': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Variable, 'value' : f"{(p2-p1)/L}*y*(y-{H})/{2*mu}" },
                'South': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'North': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
            },
            'v_y': {
                'InitialValue': 0.0,
                'West': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'East': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'South': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'North': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
            },
            'p': {
                'InitialValue': p1,
                'West': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : p1 },
                'East': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : p2 },
                'South': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'North': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
			},
		}),
	)
	navierStokes(problemData)

if __name__ == '__main__':
	main()
